import type {
  PortfolioDetailResponse,
  PortfolioListResponse,
  PortfolioRiskMetrics,
  PortfolioSummary,
  TradeInput,
} from "../types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);

    throw new Error(
      body?.detail?.message ?? body?.detail ?? "Portfolio request failed",
    );
  }

  return response.json();
}

export function getPortfolios() {
  return request<PortfolioListResponse>("/api/portfolios");
}

export function getPortfolio(portfolioId: string) {
  return request<PortfolioDetailResponse>(`/api/portfolios/${portfolioId}`);
}

export function getPortfolioSummary(portfolioId: string) {
  return request<PortfolioSummary>(`/api/portfolios/${portfolioId}/summary`);
}

export function executeTrade(portfolioId: string, input: TradeInput) {
  return request(`/api/portfolios/${portfolioId}/trades`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getPortfolioRisk(portfolioId: string) {
  return request<PortfolioRiskMetrics>(`/api/portfolios/${portfolioId}/risk`);
}
