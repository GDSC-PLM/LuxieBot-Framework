import { Collection, ChatInputCommandInteraction, ContextMenuCommandInteraction, AutocompleteInteraction, SlashCommandBuilder } from 'discord.js';
import WebSocket from 'ws';

export interface Command<T extends ChatInputCommandInteraction | ContextMenuCommandInteraction = ChatInputCommandInteraction> {
    tag?: string;
    usage?: string;
    data: { name: string, description?: string, toJSON: () => any };
    execute: (interaction: T) => Promise<unknown>;
    autocomplete?: (interaction: AutocompleteInteraction) => Promise<unknown>;
    cooldown?: number;
}

export interface ComponentHandler {
    data: { customId: string };
    execute: (interaction: ButtonInteraction | ModalSubmitInteraction | AnySelectMenuInteraction) => Promise<unknown>;
}

export type ChatCommand = Command<ChatInputCommandInteraction>
export type ContextMenuCommand = Command<ContextMenuCommandInteraction>

export interface WsRequestDetails {
    resolve: (data: any) => void;
    reject: (error: Error) => void;
    timer: NodeJS.Timeout;
}