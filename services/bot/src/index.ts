import * as dotenv from "dotenv";
import * as path from "path";

dotenv.config({ path: path.resolve(__dirname, "../../../.env") });

import { Events, Guild } from "discord.js";
import { LuxieBotClient } from "@/structures/LuxieBotClient";
import { load_components, load_cmds, deploy_cmds, load_events } from "@/handler";

const client = new LuxieBotClient();
const token = process.env.BOT_TOKEN;
const clientId = process.env.CLIENT_ID;
const guildId = process.env.GUILD_ID;

async function start() {
  try {
    if (client == null || token == null || clientId == null || guildId == null) {
      console.error("Environment variables are not set.");
      return;
    }
    await load_components(client);
    await load_cmds(client);
    await load_events(client);
    await deploy_cmds(clientId, guildId);
    await client.login(token);
  } catch (err) {
    console.error("Bot failed to start:", err);
  }
}

start();

export { token, clientId, client, Events, Guild };
