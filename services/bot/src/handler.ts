import fs from "node:fs";
import path from "node:path";
import { REST, Routes, Collection } from "discord.js";
import { type Command } from "@/types/discord";
import { LuxieBotClient } from "@/structures/LuxieBotClient";

const componentsPath = path.join(__dirname, "components");
const foldersPath = path.join(__dirname, "commands");
let commands: any[] = [];

export async function load_components(client: LuxieBotClient) {
  client.buttons = new Collection();
  client.modals = new Collection();
  client.selectMenus = new Collection();
  if (!fs.existsSync(componentsPath)) return;

  const componentFolders = fs.readdirSync(componentsPath);
  for (const folder of componentFolders) {
    const folderTypePath = path.join(componentsPath, folder);
    if (!fs.statSync(folderTypePath).isDirectory()) continue;

    const componentFiles = fs
      .readdirSync(folderTypePath)
      .filter((file) => file.endsWith(".js") || file.endsWith(".ts"));
    for (const file of componentFiles) {
      const filePath = path.join(folderTypePath, file);
      const componentModule = await import(filePath);
      const component = componentModule.default || componentModule;

      if (!("data" in component) || !("execute" in component)) {
        console.log(`[WARNING] Component at ${filePath} is missing "data" or "execute".`);
        continue;
      }
      switch (folder) {
        case "buttons":
          client.buttons?.set(component.data.customId, component);
          break;
        case "modals":
          client.modals?.set(component.data.customId, component);
          break;
        case "selectMenus":
          client.selectMenus?.set(component.data.customId, component);
          break;
        default:
          console.log(`[WARNING] Unknown component folder type: ${folder}`);
      }
    }
  }
}

export async function load_cmds(client: LuxieBotClient) {
  client.commands = new Collection();
  client.cooldowns = new Collection();
  commands = [];

  const commandFolders = fs.readdirSync(foldersPath);
  for (const folder of commandFolders) {
    const commandsPath = path.join(foldersPath, folder);
    const commandFiles = fs
      .readdirSync(commandsPath)
      .filter((file) => file.endsWith(".js") || file.endsWith(".ts"));

    for (const file of commandFiles) {
      const filePath = path.join(commandsPath, file);
      const commandModule = await import(filePath);
      const command: Command = commandModule.default || commandModule;

      if (command && "data" in command && "execute" in command) {
        client.commands.set(command.data.name, command);
        commands.push(command.data.toJSON());
      } else {
        console.log(
          `[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`,
        );
      }
    }
  }
}

export async function load_events(client: LuxieBotClient) {
  const eventsPath = path.join(__dirname, "events");
  const eventFiles = fs
    .readdirSync(eventsPath)
    .filter((file) => file.endsWith(".js") || file.endsWith(".ts"));

  for (const file of eventFiles) {
    const filePath = path.join(eventsPath, file);
    const eventModule = await import(filePath);
    const event = eventModule.default || eventModule;

    const method = event.once ? "once" : "on";
    client[method](event.name, (...args: any[]) => event.execute(...args));
  }
}

export async function deploy_cmds(clientId: string, guildId: string) {
  const rest = new REST().setToken(process.env.BOT_TOKEN as string);
  (async () => {
    try {
      console.log(`Started refreshing ${commands.length} application (/) commands in ${guildId}.`);
      const data: any = await rest.put(Routes.applicationGuildCommands(clientId, guildId), {
        body: commands,
      });
      console.log(`Successfully reloaded ${data.length} application (/) commands in ${guildId}.`);
    } catch (error) {
      console.error(error);
    }
  })();
}

export function delete_cmd(clientId: string, commandId: string) {
  const rest = new REST().setToken(process.env.BOT_TOKEN as string);
  (async () => {
    try {
      console.log(`Started deleting command with ID: ${commandId}`);
      await rest.delete(Routes.applicationCommand(clientId, commandId));
      console.log("Successfully deleted the application command.");
    } catch (error) {
      console.error(error);
    }
  })();
}
