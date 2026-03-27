"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
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

export function AuthForm({ mode }: { mode: AuthMode }) {
  const router = useRouter();
  const pushToast = useAppStore((state) => state.pushToast);
  const setSession = useAppStore((state) => state.setSession);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: mode === "signin" ? { email: "demo@applyforge.dev", password: "demo1234" } : undefined,
  });

  const mutation = useMutation({
    mutationFn: async (values: FormValues) =>
      api<{ user: SessionUser }>(mode === "signin" ? "/auth/login" : "/auth/register", {
        method: "POST",
        body: JSON.stringify(values),
      }),
    onSuccess: (result) => {
      setSession(result.user);
      pushToast({
        title: mode === "signin" ? "Signed in to ApplyForge" : "Account created successfully",
        tone: "success",
      });
      router.push("/dashboard");
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
      </div>

      <form className="space-y-4" onSubmit={handleSubmit((values) => mutation.mutate(values))}>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Email</label>
          <Input {...register("email")} placeholder="you@example.com" />
          {errors.email ? <p className="text-xs text-rose-300">{errors.email.message}</p> : null}
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Password</label>
          <Input {...register("password")} type="password" placeholder="At least 8 characters" />
          {errors.password ? <p className="text-xs text-rose-300">{errors.password.message}</p> : null}
        </div>
        <Button className="w-full" disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "Working…" : mode === "signin" ? "Sign in" : "Create account"}
        </Button>
      </form>
    </Card>
  );
}
