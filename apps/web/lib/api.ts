"use client";

export class ApiError extends Error {
  status: number;
  requestId: string;

  constructor(message: string, status: number, requestId = "") {
    super(message);
    this.status = status;
    this.requestId = requestId;
  }
}

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const isFormData = options.body instanceof FormData;
  const headers = new Headers(options.headers);

  if (!isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(body || "Request failed", response.status, response.headers.get("X-Request-ID") || "");
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return {} as T;
  }
  return (await response.json()) as T;
}

export async function apiText(path: string, options: RequestInit = {}): Promise<string> {
  const headers = new Headers(options.headers);
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(body || "Request failed", response.status, response.headers.get("X-Request-ID") || "");
  }

  return response.text();
}
