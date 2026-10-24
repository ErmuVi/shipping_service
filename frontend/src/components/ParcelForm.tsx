import { useState, type FormEvent } from "react";

import type { ParcelCreatePayload, ParcelType } from "../api/types";
import { MAX_PARCEL_WEIGHT_KG } from "../constants";

interface ParcelFormProps {
  types: ParcelType[];
  submitting: boolean;
  serverErrors: Record<string, string>;
  submitLabel?: string;
  onSubmit: (payload: ParcelCreatePayload) => void;
}

interface FormValues {
  name: string;
  weight: string;
  contentValue: string;
  typeId: string;
}

function parseNumber(raw: string): number | null {
  const normalized = raw.replace(",", ".").trim();

  if (!normalized) {
    return null;
  }

  const value = Number(normalized);
  return Number.isFinite(value) ? value : null;
}

export function ParcelForm({
  types,
  submitting,
  serverErrors,
  submitLabel = "Зарегистрировать посылку",
  onSubmit,
}: ParcelFormProps) {
  const [values, setValues] = useState<FormValues>({
    name: "",
    weight: "",
    contentValue: "",
    typeId: "",
  });
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});

  const errors = { ...localErrors, ...serverErrors };

  const update = (field: keyof FormValues, value: string) => {
    setValues((current) => ({ ...current, [field]: value }));

    if (localErrors[field]) {
      setLocalErrors((current) => {
        const next = { ...current };
        delete next[field];
        return next;
      });
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const nextErrors: Record<string, string> = {};
    const name = values.name.trim();
    const weight = parseNumber(values.weight);
    const contentValue = parseNumber(values.contentValue);
    const typeId = values.typeId ? Number(values.typeId) : null;

    if (!name) {
      nextErrors.name = "Укажите название посылки";
    }

    if (weight === null || weight <= 0) {
      nextErrors.weight = "Вес должен быть больше нуля";
    } else if (weight > MAX_PARCEL_WEIGHT_KG) {
      nextErrors.weight = `Максимальный вес — ${MAX_PARCEL_WEIGHT_KG} кг`;
    }

    if (contentValue === null || contentValue <= 0) {
      nextErrors.content_value = "Стоимость должна быть больше нуля";
    }

    if (typeId === null) {
      nextErrors.type_id = "Выберите тип посылки";
    }

    setLocalErrors(nextErrors);

    if (
      Object.keys(nextErrors).length > 0 ||
      weight === null ||
      contentValue === null ||
      typeId === null
    ) {
      return;
    }

    onSubmit({
      name,
      weight,
      content_value: contentValue,
      type_id: typeId,
    });
  };

  return (
    <form className="card space-y-5 p-6" onSubmit={handleSubmit} noValidate>
      <div>
        <label className="label" htmlFor="parcel-name">
          Название посылки
        </label>
        <input
          id="parcel-name"
          className="input"
          placeholder="Например: Зимняя куртка"
          value={values.name}
          onChange={(event) => update("name", event.target.value)}
          maxLength={255}
        />
        {errors.name && <p className="field-error">{errors.name}</p>}
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <label className="label" htmlFor="parcel-weight">
            Вес, кг
          </label>
          <input
            id="parcel-weight"
            className="input"
            inputMode="decimal"
            placeholder="1.5"
            value={values.weight}
            onChange={(event) => update("weight", event.target.value)}
          />
          {errors.weight ? (
            <p className="field-error">{errors.weight}</p>
          ) : (
            <p className="mt-1.5 text-xs text-slate-400">
              Максимум {MAX_PARCEL_WEIGHT_KG} кг — правило международной доставки
            </p>
          )}
        </div>

        <div>
          <label className="label" htmlFor="parcel-value">
            Стоимость содержимого, USD
          </label>
          <input
            id="parcel-value"
            className="input"
            inputMode="decimal"
            placeholder="120.00"
            value={values.contentValue}
            onChange={(event) => update("contentValue", event.target.value)}
          />
          {errors.content_value && (
            <p className="field-error">{errors.content_value}</p>
          )}
          <p className="mt-1.5 text-xs text-slate-400">
            От стоимости считается пошлина при превышении 200 €
          </p>
        </div>
      </div>

      <div>
        <label className="label" htmlFor="parcel-type">
          Тип посылки
        </label>
        <select
          id="parcel-type"
          className="input"
          value={values.typeId}
          onChange={(event) => update("typeId", event.target.value)}
        >
          <option value="">Выберите тип</option>
          {types.map((type) => (
            <option key={type.id} value={type.id}>
              {type.name}
            </option>
          ))}
        </select>
        {errors.type_id && <p className="field-error">{errors.type_id}</p>}
      </div>

      <div className="flex items-center gap-3 border-t border-slate-100 pt-5">
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Сохраняем…" : submitLabel}
        </button>
        <p className="text-xs text-slate-400">
          Стоимость доставки рассчитается автоматически в фоне
        </p>
      </div>
    </form>
  );
}
