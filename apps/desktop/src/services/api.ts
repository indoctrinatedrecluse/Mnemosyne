const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export interface World {
  id: string;
  name: string;
  description: string | null;
  seed: number;
  calendar_start_year: number;
  calendar_start_month: number;
  tick_interval_seconds: number;
  created_at: string;
  updated_at: string;
}

export interface WorldCreate {
  name: string;
  description?: string | null;
  seed: number;
  calendar_start_year: number;
  calendar_start_month: number;
  tick_interval_seconds: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { detail?: string | Array<{ loc?: string[]; msg?: string }> }
      | null;
    const detail = body?.detail;
    const message = Array.isArray(detail)
      ? detail.map((issue) => `${issue.loc?.at(-1) ?? "input"}: ${issue.msg ?? "invalid"}`).join("; ")
      : detail ?? `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function listWorlds(): Promise<World[]> {
  return request<World[]>('/api/v1/worlds');
}

export function createWorld(payload: WorldCreate): Promise<World> {
  return request<World>('/api/v1/worlds', {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
