import type { ParcelType } from "../api/types";

export type StatusFilter = "all" | "calculated" | "pending";

interface FiltersProps {
  types: ParcelType[];
  typeId?: number;
  status: StatusFilter;
  onTypeChange: (value: string) => void;
  onStatusChange: (value: StatusFilter) => void;
  onReset: () => void;
}

export function Filters({
  types,
  typeId,
  status,
  onTypeChange,
  onStatusChange,
  onReset,
}: FiltersProps) {
  const hasActiveFilters = typeId !== undefined || status !== "all";

  return (
    <div className="card flex flex-col gap-3 p-4 sm:flex-row sm:items-end">
      <div className="sm:w-56">
        <label className="label" htmlFor="filter-type">
          Тип посылки
        </label>
        <select
          id="filter-type"
          className="input"
          value={typeId ?? ""}
          onChange={(event) => onTypeChange(event.target.value)}
        >
          <option value="">Все типы</option>
          {types.map((type) => (
            <option key={type.id} value={type.id}>
              {type.name}
            </option>
          ))}
        </select>
      </div>

      <div className="sm:w-56">
        <label className="label" htmlFor="filter-status">
          Статус расчёта
        </label>
        <select
          id="filter-status"
          className="input"
          value={status}
          onChange={(event) =>
            onStatusChange(event.target.value as StatusFilter)
          }
        >
          <option value="all">Все посылки</option>
          <option value="calculated">Рассчитанные</option>
          <option value="pending">Ожидают расчёта</option>
        </select>
      </div>

      {hasActiveFilters && (
        <button type="button" className="btn-secondary" onClick={onReset}>
          Сбросить фильтры
        </button>
      )}
    </div>
  );
}
