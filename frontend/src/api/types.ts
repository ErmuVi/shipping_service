export interface Parcel {
  id: string;
  name: string;
  weight: number;
  content_value: number;
  type_id: number;
  type_name: string | null;
  carrier_name: string | null;
  delivery_cost: number | null;
  is_calculated: boolean;
  created_at: string;
}

export interface ParcelPage {
  items: Parcel[];
  total: number;
  limit: number;
  offset: number;
}

export interface ParcelType {
  id: number;
  name: string;
}

export interface ParcelCreatePayload {
  name: string;
  weight: number;
  content_value: number;
  type_id: number;
}

export interface SupportAnswer {
  answer: string;
}

export interface ChatMessagePayload {
  role: "user" | "assistant";
  content: string;
}

export interface ActionResponse {
  status: string;
  message: string;
}

export interface ValidationDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}
