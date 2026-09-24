declare global {
  namespace NodeJS {
    interface ProcessEnv {
      BOT_TOKEN: string;
      CLIENT_ID: string;
      GUILD_ID: string;
      DB_URI: string;
      WS_URL?: string;
      API_TOKEN: string;
      JWT_SECRET: string;
    }
  }
}
export {};
