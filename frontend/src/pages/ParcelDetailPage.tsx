import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ApiError, errorMessage } from "../api/client";
import { parcelsApi } from "../api/parcels";
import { StatusBadge } from "../components/StatusBadge";
import { ArrowLeftIcon, RefreshIcon, TrashIcon } from "../components/icons";
import { useToast } from "../hooks/useToast";
import { formatDate, formatMoney, formatWeight } from "../utils/format";

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-100 py-3 last:border-0">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="text-sm font-medium text-slate-900">{value}</dd>
    </div>
  );
}

export function ParcelDetailPage() {
  const { parcelId } = useParams<{ parcelId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { notify } = useToast();

  const parcelQuery = useQuery({
    queryKey: ["parcel", parcelId],
    queryFn: () => parcelsApi.get(parcelId ?? ""),
    enabled: Boolean(parcelId),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => parcelsApi.remove(id),
    onSuccess: async () => {
      notify("Посылка удалена", "success");
      await queryClient.invalidateQueries({ queryKey: ["parcels"] });
      navigate("/parcels");
    },
    onError: (error) => notify(errorMessage(error), "error"),
  });

  const recalculateMutation = useMutation({
    mutationFn: (id: string) => parcelsApi.recalculate(id),
    onSuccess: async (data) => {
      notify(data.message, "success");
      window.setTimeout(() => {
        void queryClient.invalidateQueries({ queryKey: ["parcel", parcelId] });
        void queryClient.invalidateQueries({ queryKey: ["parcels"] });
      }, 2500);
    },
    onError: (error) => notify(errorMessage(error), "error"),
  });

  const handleDelete = (id: string, name: string) => {
    if (window.confirm(`Удалить посылку «${name}»? Действие необратимо.`)) {
      deleteMutation.mutate(id);
    }
  };

  if (parcelQuery.isLoading) {
    return <div className="card h-64 animate-pulse bg-slate-100" />;
  }

  const notFound =
    parcelQuery.error instanceof ApiError && parcelQuery.error.status === 404;

  if (parcelQuery.isError) {
    return (
      <div className="card flex flex-col items-start gap-3 p-6">
        <p className="text-sm font-medium text-rose-600">
          {notFound
            ? "Посылка не найдена или принадлежит другой сессии."
            : `Не удалось загрузить посылку: ${errorMessage(parcelQuery.error)}`}
        </p>
        <Link to="/parcels" className="btn-secondary">
          <ArrowLeftIcon className="h-4 w-4" />
          К списку посылок
        </Link>
      </div>
    );
  }

  if (!parcelQuery.data) {
    return null;
  }

  const parcel = parcelQuery.data;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <Link
          to="/parcels"
          className="mb-3 inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-900"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          К списку посылок
        </Link>

        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
              {parcel.name}
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              {parcel.type_name ?? "Без типа"} · создана{" "}
              {formatDate(parcel.created_at)}
            </p>
          </div>
          <StatusBadge calculated={parcel.is_calculated} />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="card p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Стоимость доставки
          </p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">
            {formatMoney(parcel.delivery_cost, "RUB")}
          </p>
          <p className="mt-1 text-xs text-slate-400">
            {parcel.is_calculated
              ? "Рассчитана по актуальному курсу ЦБ"
              : "Ещё не рассчитана — обновится автоматически"}
          </p>
        </div>

        <div className="card p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Стоимость содержимого
          </p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">
            {formatMoney(parcel.content_value, "USD")}
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Пошлина — 15% от суммы свыше 200 €
          </p>
        </div>
      </div>

      <div className="card p-5">
        <dl>
          <DetailRow label="Вес" value={formatWeight(parcel.weight)} />
          <DetailRow label="Тип" value={parcel.type_name ?? "Без типа"} />
          <DetailRow
            label="Перевозчик"
            value={parcel.carrier_name ?? "Назначается автоматически"}
          />
          <DetailRow label="Идентификатор" value={parcel.id} />
        </dl>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="btn-secondary"
          onClick={() => recalculateMutation.mutate(parcel.id)}
          disabled={recalculateMutation.isPending}
        >
          <RefreshIcon className="h-4 w-4" />
          {recalculateMutation.isPending ? "Запускаем…" : "Пересчитать стоимость"}
        </button>

        <button
          type="button"
          className="btn-danger"
          onClick={() => handleDelete(parcel.id, parcel.name)}
          disabled={deleteMutation.isPending}
        >
          <TrashIcon className="h-4 w-4" />
          Удалить посылку
        </button>
      </div>
    </div>
  );
}
