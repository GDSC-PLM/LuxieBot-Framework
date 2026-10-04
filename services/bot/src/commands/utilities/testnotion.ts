import {
  SlashCommandBuilder,
  ContainerBuilder,
  TextDisplayBuilder,
  SeparatorBuilder,
  MessageFlags,
} from "discord.js";

import { type ChatCommand } from "@/types/discord";
import type { LuxieBotClient } from "@/structures/LuxieBotClient";

const command: ChatCommand = {
  tag: "utility",
  usage: "/test",
  data: new SlashCommandBuilder()
    .setName("test")
    .setDescription("A test command for testing Notion API"),
  async execute(interaction) {
    await interaction.deferReply({ withResponse: true });
    const botClient = interaction.client as LuxieBotClient;

    if (!botClient.notion) {
      const embed = new ContainerBuilder()
        .setAccentColor(0xff0000)
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent("## Notion Integration Offline"),
        )
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent("The `NOTION_TOKEN` is not configured in `.env`."),
        );

      return await interaction.editReply({
        flags: MessageFlags.IsComponentsV2,
        components: [embed],
      });
    }

    try {
      const startTime = Date.now();
      const me = await botClient.notion.users.me({});
      const latency = Date.now() - startTime;

      const botName = me.name;

      const successContainer = new ContainerBuilder()
        .setAccentColor(0x00ff00)
        .addTextDisplayComponents(new TextDisplayBuilder().setContent("## ✅ Notion Connected"))
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent(
            `**Integration Name:** \`${botName}\`\n` +
              `**Bot ID:** \`${me.id}\`\n` +
              `**Response Time:** \`${latency}ms\``,
          ),
        )
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent(`*Requested by ${interaction.user.tag}*`),
        );

      await interaction.editReply({
        flags: MessageFlags.IsComponentsV2,
        components: [successContainer],
      });
    } catch (error: any) {
      const errorContainer = new ContainerBuilder()
        .setAccentColor(0xff0000)
        .addTextDisplayComponents(new TextDisplayBuilder().setContent("## ❌ Notion API Error"))
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent(
            `Failed to communicate with Notion API:\n\`\`\`\n${error.message || error}\n\`\`\``,
          ),
        );

      await interaction.editReply({
        flags: MessageFlags.IsComponentsV2,
        components: [errorContainer],
      });
    }
  },
};

export default command;
