export function StatusBadge({ calculated }: { calculated: boolean }) {
  if (calculated) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
        Рассчитано
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700 ring-1 ring-inset ring-amber-600/20">
      <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
      Ожидает расчёта
    </span>
  );
}
