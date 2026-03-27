export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description: string;
}) {
  return (
    <div className="space-y-2">
      {eyebrow ? <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">{eyebrow}</p> : null}
      <div className="space-y-1">
        <h1 className="text-3xl font-semibold text-white">{title}</h1>
        <p className="max-w-3xl text-sm text-slate-300">{description}</p>
      </div>
    </div>
  );
}
