import {
  SlashCommandBuilder,
  ContainerBuilder,
  TextDisplayBuilder,
  SeparatorBuilder,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  ComponentType,
  MessageFlags,
  ModalBuilder,
  LabelBuilder,
  TextInputBuilder,
  TextInputStyle,
} from "discord.js";
import { type ChatCommand } from "@/types/discord";
import { type LuxieBotClient } from "@/structures/LuxieBotClient";

const RESOURCES_HUB_URL =
  "https://app.notion.com/p/GDGoC-PLM-Resources-Hub-3b6c5d8d20d080a78772d896639d6918";
const DATABASE_ID = "3b6c5d8d-20d0-8044-9ced-dd3848ba51e4";

const OVERVIEW = `This is our official, living knowledge base built **by the community, for the community**.

📝 **Reviewers**
  \`Structured study materials to learn or refresh a specific tool or skill.\`

📃 **Documentation & Language**
  \`Syntax guides, common patterns, and best practices.\`

🛠️ **Platforms & Tools**
  \`Practical guides for the platforms our tracks actually use.\`

🚀 **Cheat Sheets**
  \`Quick-reference, single-page condensations meant to be glanced at.\`

📒 **Notes on Past Subjects/Sessions**
  \`Recaps from Study Jams, workshops, or academic classes.\`

🧭 **Tutorials & Guides**
  \`Step-by-step walkthroughs for building something from start to finish.\`

🗃️ **Curated External Resource Lists**
  \`Collections of genuinely useful outside links and playlists.\`

📋 **Templates:**
  \`Reusable starting points for common deliverables.\`

🗂️ **Project Docs & PAR Archives**
  \`Documentation and reports from completed projects.\`

💼 **Career & Opportunity**
  \`Internship prep, portfolio tips, and tech resume guidance.\`

▶️ **Recorded Walkthroughs** 
  \`Short screen recordings for processes that are easier to show than explain in text.\``;

interface ResourceItem {
  title: string;
  url: string;
  category: string;
  about: string;
  submittedBy: string;
}

interface CreateResourceInput {
  title: string;
  url: string;
  category: string;
  about: string;
  userNotionEmail: string;
}

async function getUserEmail(notion: any, email: string) {
  let cursor: string | undefined = undefined;

  do {
    const response: any = await notion.users.list({
      start_cursor: cursor,
      page_size: 100,
    });

    const user = response.results.find(
      (u: any) =>
        u.type === "person" && u.person.email.toLowerCase() === email.trim().toLowerCase(),
    );

    if (user) return user;

    cursor = response.has_more ? response.next_cursor : undefined;
  } while (cursor);

  return null;
}

async function fetchResources(notion: any) {
  try {
    const db = await notion.databases.retrieve({ database_id: DATABASE_ID });
    const sourceID = db.data_sources[0].id;

    const result = await notion.dataSources.query({ data_source_id: sourceID });
    const items: ResourceItem[] = [];

    for (const row of result.results) {
      const props = row.properties;
      const title = props["Resource Name"].title.map((t: any) => t.plain_text).join("");
      if (!title || title.startsWith("[Template]")) continue;

      const url = props["Resource Link"].url;
      const category = props["Category"].multi_select.map((c: any) => c.name).join(", ");
      const about = props["About"].rich_text.map((t: any) => t.plain_text).join("");
      const submittedBy = props["Submitted By"].people.map((u: any) => u.name);

      items.push({ title, url, category, about, submittedBy });
    }
    return items;
  } catch {
    return [];
  }
}

async function addResources(notion: any, input: CreateResourceInput) {
  const notionUser = await getUserEmail(notion, input.userNotionEmail);
  if (!notionUser) {
    throw new Error(`No Notion account matching \`${input.userNotionEmail}\``);
  }

  return await notion.pages.create({
    parent: {
      database_id: DATABASE_ID,
    },
    properties: {
      "Resource Name": {
        title: [
          {
            text: {
              content: input.title,
            },
          },
        ],
      },
      Category: {
        multi_select: [
          {
            name: input.category,
          },
        ],
      },
      "Submitted By": {
        people: [
          {
            id: notionUser.id,
          },
        ],
      },
      "Resource Link": {
        url: input.url,
      },
      About: {
        rich_text: [
          {
            text: {
              content: input.about,
            },
          },
        ],
      },
    },
  });
}

function formatResources(resources: ResourceItem[]): string {
  if (resources.length === 0) {
    return "*No resources have been submitted yet.*";
  }

  return resources
    .map((r: ResourceItem, i: number): string => {
      const link = `[${r.title}](${r.url})`;
      const metadata = `**Category:** \`${r.category}\`\n**By:** \`${r.submittedBy}\``;
      const description = `\n> ${r.about}`;
      return `### ${i + 1}. ${link}\n${metadata}${description}`;
    })
    .join("\n\n");
}

function buildButtons(activeTab: "overview" | "resources" | "submit", disabled = false) {
  return new ActionRowBuilder<ButtonBuilder>().addComponents(
    new ButtonBuilder()
      .setCustomId("tab_resources")
      .setLabel(`Resources`)
      .setStyle(activeTab === "resources" ? ButtonStyle.Primary : ButtonStyle.Secondary)
      .setDisabled(disabled || activeTab === "resources"),
    new ButtonBuilder()
      .setCustomId("tab_overview")
      .setLabel("Overview")
      .setStyle(activeTab === "overview" ? ButtonStyle.Primary : ButtonStyle.Secondary)
      .setDisabled(disabled || activeTab === "overview"),
    new ButtonBuilder()
      .setCustomId("tab_submit")
      .setLabel("Submit")
      .setStyle(activeTab === "submit" ? ButtonStyle.Primary : ButtonStyle.Secondary)
      .setDisabled(disabled || activeTab === "submit"),
  );
}

function buildContainer(
  activeTab: "overview" | "resources" | "submit",
  content: string,
  disabled = false,
) {
  const container = new ContainerBuilder()
    .setAccentColor(0x2f3438)
    .addTextDisplayComponents(
      new TextDisplayBuilder().setContent(`[**GDGoC PLM Resources Hub**](${RESOURCES_HUB_URL})`),
    )
    .addTextDisplayComponents(new TextDisplayBuilder().setContent(content))
    .addActionRowComponents(buildButtons(activeTab, disabled));

  return container;
}

const command: ChatCommand = {
  tag: "notion",
  usage: "/resources",
  data: new SlashCommandBuilder()
    .setName("resources")
    .setDescription("Displays our GDGoC PLM Resources Hub and submitted resources"),

  async execute(interaction) {
    await interaction.deferReply({ withResponse: true });
    const botClient = interaction.client as LuxieBotClient;

    if (!botClient.notion) {
      const embed = new ContainerBuilder()
        .setAccentColor(0xff0000)
        .addTextDisplayComponents(new TextDisplayBuilder().setContent("## Notion Offline"))
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent("`NOTION_TOKEN` is not set in `.env`."),
        );

      return await interaction.editReply({
        flags: MessageFlags.IsComponentsV2,
        components: [embed],
      });
    }

    try {
      const resources = await fetchResources(botClient.notion);
      const resourcesText = formatResources(resources);

      let currentTab: "overview" | "resources" = "resources";

      const response = await interaction.editReply({
        flags: MessageFlags.IsComponentsV2,
        components: [buildContainer(currentTab, resourcesText)],
      });

      const collector = response.createMessageComponentCollector({
        componentType: ComponentType.Button,
        time: 120000,
      });

      collector.on("collect", async (i) => {
        if (i.user.id !== interaction.user.id) {
          return i.reply({
            content: "Only the user who ran this command can switch tabs.",
            flags: MessageFlags.Ephemeral,
          });
        }

        if (i.customId === "tab_resources" || i.customId === "tab_overview") {
          currentTab = i.customId === "tab_resources" ? "resources" : "overview";
          const content = currentTab === "resources" ? resourcesText : OVERVIEW;
          const updated = buildContainer(currentTab, content);
          return await i.update({ components: [updated] });
        }

        if (i.customId === "tab_submit") {
          const modal = new ModalBuilder()
            .setCustomId("modal_submit_resource")
            .setTitle("Submit Resource to Notion")
            .addLabelComponents(
              new LabelBuilder()
                .setLabel("Resource Title")
                .setTextInputComponent(
                  new TextInputBuilder()
                    .setCustomId("res_title")
                    .setStyle(TextInputStyle.Short)
                    .setRequired(true),
                ),
              new LabelBuilder()
                .setLabel("Resource URL")
                .setTextInputComponent(
                  new TextInputBuilder()
                    .setCustomId("res_url")
                    .setStyle(TextInputStyle.Short)
                    .setRequired(true),
                ),
              new LabelBuilder()
                .setLabel("Category")
                .setDescription("Refer to Overview for a complete list")
                .setTextInputComponent(
                  new TextInputBuilder()
                    .setCustomId("res_category")
                    .setStyle(TextInputStyle.Short)
                    .setRequired(true),
                ),
              new LabelBuilder()
                .setLabel("Your Notion Email")
                .setTextInputComponent(
                  new TextInputBuilder()
                    .setCustomId("res_email")
                    .setStyle(TextInputStyle.Short)
                    .setRequired(true),
                ),
              new LabelBuilder()
                .setLabel("About / Description")
                .setTextInputComponent(
                  new TextInputBuilder()
                    .setCustomId("res_about")
                    .setStyle(TextInputStyle.Paragraph)
                    .setRequired(false),
                ),
            );

          await i.showModal(modal);

          try {
            const modalSubmission = await i.awaitModalSubmit({
              filter: (sub) =>
                sub.customId === "modal_submit_resource" && sub.user.id === interaction.user.id,
              time: 300000,
            });

            await modalSubmission.deferReply({ flags: MessageFlags.Ephemeral });

            const title = modalSubmission.fields.getTextInputValue("res_title");
            const url = modalSubmission.fields.getTextInputValue("res_url");
            const category = modalSubmission.fields.getTextInputValue("res_category");
            const email = modalSubmission.fields.getTextInputValue("res_email");
            const about = modalSubmission.fields.getTextInputValue("res_about");

            await addResources(botClient.notion, {
              title,
              url,
              category,
              about,
              userNotionEmail: email,
            });

            await modalSubmission.editReply({
              content: `Successfully submitted [${title}](${url}) to Notion!`,
            });
          } catch (err: any) {
            if (err.code !== "InteractionCollectorError") {
              console.error("Failed to submit resource:", err);
            }
          }
        }
      });

      collector.on("end", async () => {
        try {
          const finalContent = currentTab === "resources" ? resourcesText : OVERVIEW;
          const disabledContainer = buildContainer(currentTab, finalContent, true);
          await interaction.editReply({ components: [disabledContainer] });
        } catch {}
      });
    } catch (error: any) {
      const errContainer = new ContainerBuilder()
        .setAccentColor(0xff0000)
        .addTextDisplayComponents(new TextDisplayBuilder().setContent("## Notion Error"))
        .addSeparatorComponents(new SeparatorBuilder().setDivider(true))
        .addTextDisplayComponents(
          new TextDisplayBuilder().setContent(`\`\`\`${error.message || error}\`\`\``),
        );

      await interaction.editReply({
        flags: MessageFlags.IsComponentsV2,
        components: [errContainer],
      });
    }
  },
};

export default command;
