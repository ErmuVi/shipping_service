export function formatMoney(
  value: number | null,
  currency: "USD" | "RUB",
): string {
  if (value === null || Number.isNaN(value)) {
    return "—";
  }

  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatWeight(value: number): string {
  return `${new Intl.NumberFormat("ru-RU", {
    maximumFractionDigits: 2,
  }).format(value)} кг`;
}

export function formatDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}
