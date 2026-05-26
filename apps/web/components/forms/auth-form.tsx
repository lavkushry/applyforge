"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useId } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import type { SessionUser } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormValues = z.infer<typeof schema>;
type AuthMode = "signin" | "signup";

const defaultSignInValues = {
  email: "defaultuser@applyforge.dev",
  password: "defaultuser123",
};

const enableBootstrapLogin = process.env.NEXT_PUBLIC_ENABLE_BOOTSTRAP_LOGIN === "1";

export function AuthForm({ mode }: { mode: AuthMode }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const pushToast = useAppStore((state) => state.pushToast);
  const setSession = useAppStore((state) => state.setSession);
  const session = useAppStore((state) => state.session);
  const emailId = useId();
  const passwordId = useId();
  const emailErrorId = useId();
  const passwordErrorId = useId();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: mode === "signin" && enableBootstrapLogin ? defaultSignInValues : undefined,
  });

  useEffect(() => {
    if (mode === "signin" && session) {
      router.replace("/dashboard");
    }
  }, [mode, router, session]);

  const mutation = useMutation({
    mutationFn: async (values: FormValues) =>
      api<{ user: SessionUser }>(mode === "signin" ? "/auth/login" : "/auth/register", {
        method: "POST",
        body: JSON.stringify(values),
      }),
    onSuccess: (result) => {
      queryClient.setQueryData(["session"], result.user);
      setSession(result.user);
      pushToast({
        title: mode === "signin" ? "Signed in to ApplyForge" : "Account created successfully",
        tone: "success",
      });
      router.replace("/dashboard");
    },
    onError: () => {
      pushToast({ title: "Authentication failed", tone: "error" });
    },
  });

  return (
    <Card className="mx-auto max-w-md space-y-6">
      <div className="space-y-2">
        <CardTitle>{mode === "signin" ? "Welcome back" : "Create your ApplyForge account"}</CardTitle>
        <CardDescription>
          {mode === "signin"
            ? "Sign in to continue your job hunt pipeline."
            : "Start building your AI-powered application workflow."}
        </CardDescription>
        {mode === "signin" && enableBootstrapLogin ? (
          <p className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs text-cyan-100">
            First local login: defaultuser@applyforge.dev / defaultuser123
          </p>
        ) : null}
      </div>

      <form className="space-y-4" onSubmit={handleSubmit((values) => mutation.mutate(values))}>
        <div className="space-y-2">
          <label htmlFor={emailId} className="text-sm text-slate-300">Email</label>
          <Input
            id={emailId}
            {...register("email")}
            placeholder="you@example.com"
            aria-invalid={errors.email ? "true" : "false"}
            aria-describedby={errors.email ? emailErrorId : undefined}
          />
          {errors.email ? <p id={emailErrorId} role="alert" className="text-xs text-rose-300">{errors.email.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label htmlFor={passwordId} className="text-sm text-slate-300">Password</label>
          <Input
            id={passwordId}
            {...register("password")}
            type="password"
            placeholder="At least 8 characters"
            aria-invalid={errors.password ? "true" : "false"}
            aria-describedby={errors.password ? passwordErrorId : undefined}
          />
          {errors.password ? <p id={passwordErrorId} role="alert" className="text-xs text-rose-300">{errors.password.message}</p> : null}
        </div>
        <Button className="w-full" disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "Working…" : mode === "signin" ? "Sign in" : "Create account"}
        </Button>
      </form>
    </Card>
  );
}
