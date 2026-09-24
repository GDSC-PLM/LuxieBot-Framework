import { Profile, AuthResponse } from './types';

export class DiscordClientConnection {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  public setToken(token: string) {
    this.token = token;
  }

  public clearToken() {
    this.token = null;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers || {});
    headers.set('Content-Type', 'application/json');
    
    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw { status: response.status, message: await response.text() };
    }

    return response.json();
  }

  public async authenticateDiscord(code: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/discord/callback', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
  }

  public async getMe(): Promise<Profile> {
    return this.request<Profile>('/users/@me');
  }
}