import Link from "next/link";
import type { Route } from "next";

import { Card } from "@/components/ui/card";

export function EmptyState({
  title,
  description,
  ctaHref,
  ctaLabel,
}: {
  title: string;
  description: string;
  ctaHref?: Route;
  ctaLabel?: string;
}) {
  return (
    <Card className="border-dashed text-center">
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="text-sm text-slate-300">{description}</p>
        {ctaHref && ctaLabel ? (
          <Link
            href={ctaHref}
            className="inline-flex rounded-xl bg-cyan-400 px-4 py-2 text-sm font-medium text-slate-950"
          >
            {ctaLabel}
          </Link>
        ) : null}
      </div>
    </Card>
  );
}
