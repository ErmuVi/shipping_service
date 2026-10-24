import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";

import { errorMessage } from "../api/client";
import { parcelsApi } from "../api/parcels";
import type { Parcel } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { Filters, type StatusFilter } from "../components/Filters";
import { Pagination } from "../components/Pagination";
import { ParcelTable } from "../components/ParcelTable";
import { PlusIcon, RefreshIcon } from "../components/icons";
import { PAGE_SIZE } from "../constants";
import { useToast } from "../hooks/useToast";

export function ParcelsPage() {
  const queryClient = useQueryClient();
  const { notify } = useToast();
  const [searchParams, setSearchParams] = useSearchParams();

  const page = Math.max(1, Number(searchParams.get("page") ?? "1") || 1);
  const typeParam = searchParams.get("type");
  const typeId = typeParam ? Number(typeParam) : undefined;
  const status = (searchParams.get("status") ?? "all") as StatusFilter;
  const isCalculated =
    status === "calculated" ? true : status === "pending" ? false : undefined;
  const offset = (page - 1) * PAGE_SIZE;

  const typesQuery = useQuery({
    queryKey: ["types"],
    queryFn: parcelsApi.types,
    staleTime: Infinity,
  });

  const parcelsQuery = useQuery({
    queryKey: ["parcels", { page, typeId, status }],
    queryFn: () =>
      parcelsApi.list({ limit: PAGE_SIZE, offset, typeId, isCalculated }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => parcelsApi.remove(id),
    onSuccess: async () => {
      notify("Посылка удалена", "success");
      await queryClient.invalidateQueries({ queryKey: ["parcels"] });
    },
    onError: (error) => notify(errorMessage(error), "error"),
  });

  const calculateMutation = useMutation({
    mutationFn: parcelsApi.calculateAll,
    onSuccess: async (data) => {
      notify(data.message, "success");
      // Расчёт идет в фоне, поэтому обновляем список чуть позже
      window.setTimeout(() => {
        void queryClient.invalidateQueries({ queryKey: ["parcels"] });
      }, 2500);
    },
    onError: (error) => notify(errorMessage(error), "error"),
  });

  const updateFilter = (key: "type" | "status", value: string) => {
    const next = new URLSearchParams(searchParams);

    if (value && value !== "all") {
      next.set(key, value);
    } else {
      next.delete(key);
    }

    next.delete("page");
    setSearchParams(next);
  };

  const resetFilters = () => {
    const next = new URLSearchParams(searchParams);
    next.delete("type");
    next.delete("status");
    next.delete("page");
    setSearchParams(next);
  };

  const changePage = (nextOffset: number) => {
    const next = new URLSearchParams(searchParams);
    next.set("page", String(Math.floor(nextOffset / PAGE_SIZE) + 1));
    setSearchParams(next);
  };

  const handleDelete = (parcel: Parcel) => {
    const confirmed = window.confirm(
      `Удалить посылку «${parcel.name}»? Действие необратимо.`,
    );

    if (confirmed) {
      deleteMutation.mutate(parcel.id);
    }
  };

  const hasFilters = typeId !== undefined || status !== "all";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Мои посылки
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Список привязан к вашему браузеру — авторизация не нужна.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            className="btn-secondary"
            onClick={() => calculateMutation.mutate()}
            disabled={calculateMutation.isPending}
          >
            <RefreshIcon className="h-4 w-4" />
            {calculateMutation.isPending ? "Запускаем…" : "Пересчитать всё"}
          </button>
          <Link to="/parcels/new" className="btn-primary">
            <PlusIcon className="h-4 w-4" />
            Новая посылка
          </Link>
        </div>
      </div>

      <Filters
        types={typesQuery.data ?? []}
        typeId={typeId}
        status={status}
        onTypeChange={(value) => updateFilter("type", value)}
        onStatusChange={(value) => updateFilter("status", value)}
        onReset={resetFilters}
      />

      {parcelsQuery.isLoading && (
        <div className="card space-y-3 p-5" aria-label="Загрузка посылок">
          {[0, 1, 2].map((row) => (
            <div key={row} className="h-12 animate-pulse rounded-xl bg-slate-100" />
          ))}
        </div>
      )}

      {parcelsQuery.isError && (
        <div className="card flex flex-col items-start gap-3 p-6">
          <p className="text-sm font-medium text-rose-600">
            Не удалось загрузить посылки: {errorMessage(parcelsQuery.error)}
          </p>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => void parcelsQuery.refetch()}
          >
            Повторить
          </button>
        </div>
      )}

      {parcelsQuery.data && parcelsQuery.data.total === 0 && (
        <EmptyState
          title={hasFilters ? "Ничего не найдено" : "Посылок пока нет"}
          description={
            hasFilters
              ? "Попробуйте изменить фильтры или сбросить их."
              : "Зарегистрируйте первую посылку — мы рассчитаем стоимость доставки автоматически."
          }
          action={
            hasFilters ? (
              <button
                type="button"
                className="btn-secondary"
                onClick={resetFilters}
              >
                Сбросить фильтры
              </button>
            ) : (
              <Link to="/parcels/new" className="btn-primary">
                <PlusIcon className="h-4 w-4" />
                Создать посылку
              </Link>
            )
          }
        />
      )}

      {parcelsQuery.data && parcelsQuery.data.total > 0 && (
        <>
          <ParcelTable
            parcels={parcelsQuery.data.items}
            deletingId={
              deleteMutation.isPending ? deleteMutation.variables : undefined
            }
            onDelete={handleDelete}
          />

          <Pagination
            total={parcelsQuery.data.total}
            limit={parcelsQuery.data.limit}
            offset={parcelsQuery.data.offset}
            onChange={changePage}
          />
        </>
      )}
    </div>
  );
}
