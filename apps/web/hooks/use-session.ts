"use client";

import { useQuery } from "@tanstack/react-query";

import { api, ApiError } from "@/lib/api";
import type { SessionUser } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export function useSession() {
  const setSession = useAppStore((state) => state.setSession);

  const query = useQuery({
    queryKey: ["session"],
    queryFn: async () => {
      try {
        const user = await api<SessionUser>("/auth/me");
        setSession(user);
        return user;
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          setSession(null);
          return null;
        }
        throw error;
      }
    },
    staleTime: 60_000,
  });

  return {
    ...query,
    user: query.data ?? null,
  };
}
