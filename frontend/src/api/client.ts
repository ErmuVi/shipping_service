import type { ValidationDetail } from "./types";

export class ApiError extends Error {
  status: number;
  details: ValidationDetail[] | null;

  constructor(
    message: string,
    status: number,
    details: ValidationDetail[] | null = null,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

/** Превращает details из 422-ответа в карту "поле -> сообщение". */
export function fieldErrors(error: unknown): Record<string, string> {
  if (!(error instanceof ApiError) || !error.details) {
    return {};
  }

  const result: Record<string, string> = {};

  for (const detail of error.details) {
    const field = detail.loc.filter((part) => part !== "body").join(".");
    if (field && !result[field]) {
      result[field] = detail.msg;
    }
  }

  return result;
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Неизвестная ошибка";
}

/** Все запросы к API идут через префикс /api, чтобы не конфликтовать
 *  с клиентскими маршрутами SPA (/parcels, /support и т.д.). */
const API_BASE = "/api";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  });

  if (!response.ok) {
    let payload: {
      message?: string;
      details?: ValidationDetail[] | null;
    } | null = null;

    try {
      payload = await response.json();
    } catch {
      // Тело ответа может быть не JSON (например, 502 от прокси)
    }

    throw new ApiError(
      payload?.message ?? `Ошибка запроса (${response.status})`,
      response.status,
      payload?.details ?? null,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
