import {
  SlashCommandBuilder,
  ContainerBuilder,
  TextDisplayBuilder,
  SeparatorBuilder,
  MessageFlags,
} from "discord.js";

import { type ChatCommand } from "@/types/discord";

const command: ChatCommand = {
  tag: "utility",
  usage: "/ping",
  data: new SlashCommandBuilder()
    .setName("ping")
    .setDescription("Pings the bot and shows connection latency"),
  async execute(interaction) {
    const sent = await interaction.deferReply({ withResponse: true });
    const responseTimestamp =
      sent.resource?.message?.createdTimestamp ?? Date.now();
    const roundtripLatency = responseTimestamp - interaction.createdTimestamp;
    const websocketLatency = interaction.client.ws.ping;

    const accentColor = roundtripLatency < 200 ? 0x00ff00 : 0xffa500;

    const embed = new ContainerBuilder()
      .setAccentColor(accentColor)
      .addTextDisplayComponents(
        new TextDisplayBuilder().setContent("**Pong!**"),
      )
      .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
      .addTextDisplayComponents(
        new TextDisplayBuilder().setContent(
          `**Bot Latency:** \`${roundtripLatency}ms\``,
        ),
        new TextDisplayBuilder().setContent(
          `**API Latency:** \`${websocketLatency}ms\``,
        ),
      )
      .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
      .addTextDisplayComponents(
        new TextDisplayBuilder().setContent(
          `*Requested by ${interaction.user.tag}*`,
        ),
      );

    await interaction.editReply({
      flags: MessageFlags.IsComponentsV2,
      components: [embed],
    });
  },
};

export default command;
