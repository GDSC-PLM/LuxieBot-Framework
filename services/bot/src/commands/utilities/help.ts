import {
  SlashCommandBuilder,
  ContainerBuilder,
  TextDisplayBuilder,
  SeparatorBuilder,
  MessageFlags,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  ComponentType,
} from "discord.js";
import { LuxieBotClient } from "@/structures/LuxieBotClient";

import { type ChatCommand, type Command } from "@/types/discord";

const command: ChatCommand = {
  tag: "utility",
  usage: "/help optional: command",
  data: new SlashCommandBuilder()
    .setName("help")
    .setDescription("Sends a list of commands and their descriptions")
    .addStringOption((option) =>
      option
        .setName("command")
        .setDescription("Show info for a specific command")
        .setAutocomplete(true)
        .setRequired(false),
    ),

  async autocomplete(interaction) {
    const client = interaction.client as LuxieBotClient;
    const focusedValue = interaction.options.getFocused().toLowerCase();
    const allCommands = Array.from(client.commands.values());
    const filtered = allCommands.filter((command) => {
      return command.data?.name?.toLowerCase().startsWith(focusedValue);
    });

    await interaction.respond(
      filtered.slice(0, 25).map((command) => ({
        name: command.data.name,
        value: command.data.name,
      })),
    );
  },

  /**
   * @param {import('discord.js').ChatInputCommandInteraction} interaction
   */
  async execute(interaction) {
    const client = interaction.client as LuxieBotClient;
    const response = await interaction.deferReply({
      flags: MessageFlags.Ephemeral,
    });

    const commands = client.commands;
    const specifier = interaction.options.getString("command");

    if (specifier && specifier.trim()) {
      const targetCmd = commands.get(specifier.trim().toLowerCase());

      if (!targetCmd) {
        return await interaction.editReply({
          content: `Command \`/${specifier}\` was not found.`,
        });
      }

      const cmdName = targetCmd.data?.name || specifier;
      const cmdDesc = targetCmd.data?.description || "No description available.";
      const cmdUsage = targetCmd.usage || `/${cmdName}`;

      const embed = new ContainerBuilder()
        .setAccentColor(0xffa500)
        .addTextDisplayComponents(new TextDisplayBuilder().setContent(`**Help | /${cmdName}**`))
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent(`${cmdDesc}\n\n**Usage** - \`${cmdUsage}\``),
        )
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent(`*Requested by ${interaction.user.tag}*`),
        );

      return await interaction.editReply({
        flags: MessageFlags.IsComponentsV2,
        components: [embed],
      });
    }

    const categoriesMap = new Map<string, Command[]>();

    commands.forEach((cmd) => {
      const categoryName =
        cmd.tag && typeof cmd.tag === "string" ? cmd.tag.toLowerCase() : "uncategorized";
      const category = categoriesMap.get(categoryName) || [];
      category.push(cmd);
      categoriesMap.set(categoryName, category);
    });

    const categoryArray = Array.from(categoriesMap.entries());
    const totalPages = categoryArray.length;
    let currentPage = 0;

    const generatePage = (pageIndex: number) => {
      const embed = new ContainerBuilder()
        .setAccentColor(0xffa500)
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent(
            `**Help Menu** (Category ${pageIndex + 1}/${totalPages || 1})`,
          ),
        )
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true));

      if (categoryArray.length === 0) {
        embed.addTextDisplayComponents(
          new TextDisplayBuilder().setContent("*No commands registered.*"),
        );
        return embed;
      }

      const [currentCategory, currentCommands] = categoryArray[pageIndex] || ["", []];

      embed.addTextDisplayComponents(
        new TextDisplayBuilder().setContent(`**${currentCategory.toUpperCase()}**`),
      );

      currentCommands.forEach((cmd) => {
        const cmdName = cmd.data?.name || "unknown-command";
        const cmdDesc = cmd.data?.description || "No description available.";
        const cmdUsage = cmd.usage || `/${cmdName}`;

        embed.addTextDisplayComponents(
          new TextDisplayBuilder().setContent(
            `*/${cmdName}*\n${cmdDesc}\n**Usage** - \`${cmdUsage}\``,
          ),
        );
      });

      embed
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent(`*Requested by ${interaction.user.tag}*`),
        );

      return embed;
    };

    const generateButtons = (pageIndex: number, disabled = false) => {
      return new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setCustomId("help_prev")
          .setLabel("Previous")
          .setStyle(ButtonStyle.Primary)
          .setDisabled(disabled || pageIndex === 0),
        new ButtonBuilder()
          .setCustomId("help_next")
          .setLabel("Next")
          .setStyle(ButtonStyle.Primary)
          .setDisabled(disabled || pageIndex === totalPages - 1),
      );
    };

    const embed = generatePage(currentPage);

    if (totalPages > 1) {
      embed.addActionRowComponents(generateButtons(currentPage));
    }

    await interaction.editReply({
      flags: MessageFlags.IsComponentsV2,
      components: [embed],
    });

    if (totalPages <= 1) return;

    const collector = response.createMessageComponentCollector({
      componentType: ComponentType.Button,
      time: 60_000,
    });

    collector.on("collect", async (i) => {
      if (i.user.id !== interaction.user.id) {
        return i.reply({
          content: "These buttons are not for you!",
          flags: MessageFlags.Ephemeral,
        });
      }

      if (i.customId === "help_prev") {
        currentPage--;
      } else if (i.customId === "help_next") {
        currentPage++;
      }

      const updatedContainer = generatePage(currentPage).addActionRowComponents(
        generateButtons(currentPage),
      );
      await i.update({
        components: [updatedContainer],
      });
    });

    collector.on("end", async () => {
      try {
        const finalContainer = generatePage(currentPage).addActionRowComponents(
          generateButtons(currentPage, true),
        );
        await interaction.editReply({
          components: [finalContainer],
        });
      } catch (error) {}
    });
  },
};

export default command;
