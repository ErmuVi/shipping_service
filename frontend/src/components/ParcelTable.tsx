import { Link } from "react-router-dom";

import type { Parcel } from "../api/types";
import { formatDate, formatMoney, formatWeight } from "../utils/format";
import { TrashIcon } from "./icons";
import { StatusBadge } from "./StatusBadge";

interface ParcelTableProps {
  parcels: Parcel[];
  deletingId?: string;
  onDelete: (parcel: Parcel) => void;
}

export function ParcelTable({
  parcels,
  deletingId,
  onDelete,
}: ParcelTableProps) {
  return (
    <div className="card overflow-hidden">
      {/* Десктопная таблица */}
      <table className="hidden w-full text-left text-sm md:table">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-5 py-3 font-medium">Посылка</th>
            <th className="px-5 py-3 font-medium">Вес</th>
            <th className="px-5 py-3 font-medium">Стоимость</th>
            <th className="px-5 py-3 font-medium">Доставка</th>
            <th className="px-5 py-3 font-medium">Статус</th>
            <th className="px-5 py-3 font-medium">Создана</th>
            <th className="px-5 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {parcels.map((parcel) => (
            <tr key={parcel.id} className="transition-colors hover:bg-slate-50/70">
              <td className="px-5 py-4">
                <Link
                  to={`/parcels/${parcel.id}`}
                  className="font-medium text-slate-900 hover:text-indigo-600"
                >
                  {parcel.name}
                </Link>
                <p className="text-xs text-slate-500">
                  {parcel.type_name ?? "Без типа"}
                </p>
              </td>
              <td className="px-5 py-4 text-slate-600">
                {formatWeight(parcel.weight)}
              </td>
              <td className="px-5 py-4 text-slate-600">
                {formatMoney(parcel.content_value, "USD")}
              </td>
              <td className="px-5 py-4 font-medium text-slate-900">
                {formatMoney(parcel.delivery_cost, "RUB")}
              </td>
              <td className="px-5 py-4">
                <StatusBadge calculated={parcel.is_calculated} />
              </td>
              <td className="px-5 py-4 text-slate-500">
                {formatDate(parcel.created_at)}
              </td>
              <td className="px-5 py-4 text-right">
                <button
                  type="button"
                  className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-rose-50 hover:text-rose-600 disabled:opacity-50"
                  onClick={() => onDelete(parcel)}
                  disabled={deletingId === parcel.id}
                  aria-label={`Удалить посылку ${parcel.name}`}
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Мобильные карточки */}
      <ul className="divide-y divide-slate-100 md:hidden">
        {parcels.map((parcel) => (
          <li key={parcel.id} className="flex flex-col gap-3 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <Link
                  to={`/parcels/${parcel.id}`}
                  className="font-medium text-slate-900 hover:text-indigo-600"
                >
                  {parcel.name}
                </Link>
                <p className="text-xs text-slate-500">
                  {parcel.type_name ?? "Без типа"} ·{" "}
                  {formatWeight(parcel.weight)}
                </p>
              </div>
              <StatusBadge calculated={parcel.is_calculated} />
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">
                {formatMoney(parcel.content_value, "USD")} ·{" "}
                {formatDate(parcel.created_at)}
              </span>
              <span className="font-semibold text-slate-900">
                {formatMoney(parcel.delivery_cost, "RUB")}
              </span>
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                className="btn-danger"
                onClick={() => onDelete(parcel)}
                disabled={deletingId === parcel.id}
              >
                <TrashIcon className="h-4 w-4" />
                Удалить
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
