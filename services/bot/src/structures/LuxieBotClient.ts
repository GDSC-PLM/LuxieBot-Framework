import { Client, GatewayIntentBits, Collection } from "discord.js";
import { Client as NotionClient } from "@notionhq/client";
import type {
  ChatCommand,
  Command,
  ComponentHandler,
  ContextMenuCommand,
  WsRequestDetails,
} from "@/types/discord";
import WebSocket from "ws";

export class LuxieBotClient extends Client {
  public commands: Collection<string, Command> = new Collection();
  public chatCommands: Collection<string, ChatCommand> = new Collection();
  public contextCommands: Collection<string, ContextMenuCommand> = new Collection();
  public cooldowns: Collection<string, Collection<string, number>> = new Collection();
  public buttons: Collection<string, ComponentHandler> = new Collection();
  public modals: Collection<string, ComponentHandler> = new Collection();
  public selectMenus: Collection<string, ComponentHandler> = new Collection();
  public wsBridge?: WebSocket;
  public wsRequests: Map<string, WsRequestDetails> = new Map();
  public notion?: NotionClient;

  constructor() {
    super({ intents: [GatewayIntentBits.Guilds] });

    if (process.env.NOTION_TOKEN) {
      this.notion = new NotionClient({ auth: process.env.NOTION_TOKEN });
    }
  }
}
