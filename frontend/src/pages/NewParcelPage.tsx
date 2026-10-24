import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";

import { errorMessage, fieldErrors } from "../api/client";
import { parcelsApi } from "../api/parcels";
import { ParcelForm } from "../components/ParcelForm";
import { ArrowLeftIcon } from "../components/icons";
import { useToast } from "../hooks/useToast";

export function NewParcelPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { notify } = useToast();

  const typesQuery = useQuery({
    queryKey: ["types"],
    queryFn: parcelsApi.types,
    staleTime: Infinity,
  });

  const createMutation = useMutation({
    mutationFn: parcelsApi.create,
    onSuccess: async (parcel) => {
      notify("Посылка зарегистрирована", "success");
      await queryClient.invalidateQueries({ queryKey: ["parcels"] });
      navigate(`/parcels/${parcel.id}`);
    },
    onError: (error) => notify(errorMessage(error), "error"),
  });

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <Link
          to="/parcels"
          className="mb-3 inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-900"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          К списку посылок
        </Link>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Новая посылка
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Укажите параметры — стоимость доставки рассчитается автоматически.
        </p>
      </div>

      {typesQuery.isLoading && (
        <div className="card h-64 animate-pulse bg-slate-100" />
      )}

      {typesQuery.isError && (
        <div className="card p-6 text-sm text-rose-600">
          Не удалось загрузить типы посылок:{" "}
          {errorMessage(typesQuery.error)}
        </div>
      )}

      {typesQuery.data && (
        <ParcelForm
          types={typesQuery.data}
          submitting={createMutation.isPending}
          serverErrors={
            createMutation.error ? fieldErrors(createMutation.error) : {}
          }
          onSubmit={(payload) => createMutation.mutate(payload)}
        />
      )}
    </div>
  );
}
