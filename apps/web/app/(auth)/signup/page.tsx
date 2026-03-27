import Link from "next/link";

import { AuthForm } from "@/components/forms/auth-form";

export default function SignUpPage() {
  return (
    <section className="space-y-4">
      <AuthForm mode="signup" />
      <p className="text-center text-sm text-slate-400">
        Already have an account?{" "}
        <Link href="/signin" className="text-cyan-300 hover:text-cyan-200">
          Sign in
        </Link>
        .
      </p>
    </section>
  );
}
