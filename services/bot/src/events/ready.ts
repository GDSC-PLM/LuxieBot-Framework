import { Events } from "discord.js";
import { LuxieBotClient } from "@/structures/LuxieBotClient";
import { BackendService } from "@/services/BackendService";

const WSURL = process.env.WSURL?.trim() || "http://localhost:8000/ws";

export default {
  name: Events.ClientReady,
  once: true,
  execute(client: LuxieBotClient) {
    console.log(`Ready! Logged in as ${client.user?.tag}`);
    client.wsRequests = new Map();

    const wsUrl = WSURL.replace(/^https?/, (match) => (match === "https" ? "wss" : "ws"));

    if (client.user) {
      BackendService.getInstance().connect(client, wsUrl, client.user.id);
    } else {
      console.error("Failed to connect to backend: Client user is undefined.");
    }
  },
};
