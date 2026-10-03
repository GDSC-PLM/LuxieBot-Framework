import { Client, GatewayIntentBits, Collection } from "discord.js";
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

  constructor() {
    super({ intents: [GatewayIntentBits.Guilds] });
  }
}
