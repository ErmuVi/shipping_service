import { api } from "./client";
import type {
  ActionResponse,
  ChatMessagePayload,
  Parcel,
  ParcelCreatePayload,
  ParcelPage,
  ParcelType,
  SupportAnswer,
} from "./types";

export interface ParcelQuery {
  limit: number;
  offset: number;
  typeId?: number;
  isCalculated?: boolean;
}

function buildQueryString({ typeId, isCalculated, ...rest }: ParcelQuery): string {
  const params = new URLSearchParams({
    limit: String(rest.limit),
    offset: String(rest.offset),
  });

  if (typeId !== undefined) {
    params.set("type_id", String(typeId));
  }
  if (isCalculated !== undefined) {
    params.set("is_calculated", String(isCalculated));
  }

  return params.toString();
}

export const parcelsApi = {
  list: (query: ParcelQuery) =>
    api.get<ParcelPage>(`/parcels?${buildQueryString(query)}`),

  get: (id: string) => api.get<Parcel>(`/parcels/${id}`),

  types: () => api.get<ParcelType[]>("/types"),

  create: (payload: ParcelCreatePayload) =>
    api.post<Parcel>("/parcels", payload),

  remove: (id: string) => api.delete<void>(`/parcels/${id}`),

  recalculate: (id: string) =>
    api.post<ActionResponse>(`/parcels/${id}/recalculate`),

  calculateAll: () => api.post<ActionResponse>("/parcels/calculate-now"),

  askSupport: (question: string, history: ChatMessagePayload[] = []) =>
    api.post<SupportAnswer>("/support/ask", { question, history }),
};
