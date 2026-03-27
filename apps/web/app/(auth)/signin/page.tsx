import Link from "next/link";

import { AuthForm } from "@/components/forms/auth-form";

export default function SignInPage() {
  return (
    <section className="space-y-4">
      <AuthForm mode="signin" />
      <p className="text-center text-sm text-slate-400">
        Need an account?{" "}
        <Link href="/signup" className="text-cyan-300 hover:text-cyan-200">
          Create one here
        </Link>
        .
      </p>
    </section>
  );
}
