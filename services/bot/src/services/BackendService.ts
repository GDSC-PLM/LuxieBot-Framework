import { WebSocket } from "ws";
import jwt from "jsonwebtoken";
import {
  BackendAction,
  BackendError,
  BackendEvent,
  type BackendRequest,
  type BackendResponse,
  type BackendSuccessResponse,
} from "@luxie-framework/sdk";
import { LuxieBotClient } from "@/structures/LuxieBotClient";

export class BackendService {
  private static instance: BackendService;
  private ws: WebSocket | null = null;
  private client!: LuxieBotClient;
  private reconnectAttempts = 0;

  private constructor() {}

  public static getInstance(): BackendService {
    if (!BackendService.instance) {
      BackendService.instance = new BackendService();
    }
    return BackendService.instance;
  }

  public connect(client: LuxieBotClient, url: string, botId: string): void {
    this.client = client;
    this.ws?.removeAllListeners();

    const apiToken = process.env.APITOKEN;
    const clientHeader = process.env.CLIENTHEADER;
    const jwtSecret = process.env.JWTSECRET;

    if (!apiToken || !clientHeader || !jwtSecret) {
      console.error(
        "CRITICAL: APITOKEN, CLIENTHEADER, or JWTSECRET is missing from environment variables.",
      );
      return;
    }

    this.ws = new WebSocket(url, {
      headers: {
        "Client-ID": `${clientHeader}`,
        Authorization: `Bearer ${apiToken}`,
      },
    });

    this.ws.on("open", () => {
      console.log("Connected to Python Backend via WebSocket!");

      const handshakeToken = jwt.sign(
        { sub: botId, type: "discord_bot" },
        jwtSecret,
        { expiresIn: "1m" },
      );

      this.ws?.send(
        JSON.stringify({
          action: BackendAction.HANDSHAKE,
          interaction_id: "handshake_init",
          token: handshakeToken,
        }),
      );

      this.reconnectAttempts = 0;
    });

    this.ws.on("message", async (data) => {
      try {
        const payload = JSON.parse(data.toString());

        if (
          payload.interaction_id &&
          this.client.wsRequests.has(payload.interaction_id)
        ) {
          const request = this.client.wsRequests.get(payload.interaction_id);
          if (request) {
            clearTimeout(request.timer);
            request.resolve(payload);
            this.client.wsRequests.delete(payload.interaction_id);
          }
        }
      } catch (parseError) {
        console.error("Failed to process WebSocket message:", parseError);
      }
    });

    this.ws.on("close", (code, reason) => {
      console.log("Lost connection to Backend. Reconnecting in 5 seconds...");

      for (const [_, { reject, timer }] of this.client.wsRequests.entries()) {
        clearTimeout(timer);
        if (typeof reject === "function") {
          reject(new Error("WebSocket disconnected."));
        }
      }
      this.client.wsRequests.clear();

      if (code === 1008) {
        console.error("FATAL: Halting reconnects. Reason:", reason);
        return;
      }

      const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 30000);
      this.reconnectAttempts++;
      setTimeout(() => this.connect(this.client, url, botId), delay);
    });

    this.ws.on("error", (error) => {
      console.error("WebSocket Error:", error.message);
      this.ws?.close();
    });
  }

  public dispatch(
    payload: BackendRequest,
    timeoutMs: number = 15000,
  ): Promise<BackendResponse> {
    if (!this.ws || this.ws.readyState !== this.ws.OPEN) {
      return Promise.reject(
        new Error("The backend service is currently offline."),
      );
    }

    return new Promise((resolve, reject) => {
      const interactionId = payload.interaction_id;
      if (!interactionId)
        return reject(new Error("Payload missing interaction_id"));

      const timer = setTimeout(() => {
        this.client.wsRequests.delete(interactionId);
        reject(new Error("Backend service timed out."));
      }, timeoutMs);

      this.client.wsRequests.set(interactionId, {
        resolve: (data: BackendResponse) => {
          clearTimeout(timer);
          this.client.wsRequests.delete(interactionId);
          resolve(data);
        },
        reject: (error: Error) => {
          clearTimeout(timer);
          this.client.wsRequests.delete(interactionId);
          reject(error);
        },
        timer,
      });

      this.ws!.send(JSON.stringify(payload));
    });
  }

  public async execute<T extends BackendSuccessResponse>(
    payload: BackendRequest,
    expectedEvent: BackendEvent,
  ): Promise<T> {
    const data = await this.dispatch(payload);

    if (data.error) {
      throw new BackendError(
        data.message || "An unknown error occurred on the backend.",
      );
    }

    const successData = data as BackendSuccessResponse;

    if (successData.event !== expectedEvent) {
      throw new BackendError("Received unexpected data from backend.");
    }

    return successData as T;
  }
}
