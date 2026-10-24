import type { ReactNode } from "react";

interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="card flex flex-col items-center gap-3 px-6 py-14 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-2xl">
        📦
      </span>
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      <p className="max-w-md text-sm text-slate-500">{description}</p>
      {action}
    </div>
  );
}
