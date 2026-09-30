export function formatCurrency(value: string | number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

export function formatCompactNumber(value: number) {
  return new Intl.NumberFormat("en-IN", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatChartDate(timestamp: string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
  }).format(new Date(timestamp));
}

export function formatDateTime(timestamp: string) {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Kolkata",
  }).format(new Date(timestamp));
}

export function formatCrores(value: string | number) {
  return `${new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 2,
  }).format(Number(value))} Cr`;
}

export function formatRatio(value: string | number) {
  return `${Number(value).toFixed(2)}x`;
}

export function formatPercent(value: string | number) {
  return `${Number(value).toFixed(2)}%`;
}
