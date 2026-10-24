interface PaginationProps {
  total: number;
  limit: number;
  offset: number;
  onChange: (offset: number) => void;
}

export function Pagination({ total, limit, offset, onChange }: PaginationProps) {
  if (total === 0) {
    return null;
  }

  const from = offset + 1;
  const to = Math.min(offset + limit, total);

  return (
    <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
      <p className="text-sm text-slate-500">
        Показано {from}–{to} из {total}
      </p>

      <div className="flex items-center gap-2">
        <button
          type="button"
          className="btn-secondary"
          disabled={offset === 0}
          onClick={() => onChange(Math.max(0, offset - limit))}
        >
          Назад
        </button>
        <button
          type="button"
          className="btn-secondary"
          disabled={to >= total}
          onClick={() => onChange(offset + limit)}
        >
          Вперёд
        </button>
      </div>
    </div>
  );
}
