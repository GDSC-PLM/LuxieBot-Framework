export interface DiscordUser {
    id: string;
    username: string;
    avatar: string | null;
}

export interface Profile {
    nexsplit_uid: string;
    standoff2_id: string;
    global_mmr: number;
    played_servers: {
        guild_id: string;
        guild_name: string;
        guild_icon: string;
        mmr: number;
    }[];
    discord_id: string;
}

export interface AuthResponse {
    token: string;
    user: DiscordUser;
}