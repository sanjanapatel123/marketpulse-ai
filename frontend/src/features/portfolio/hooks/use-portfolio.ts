"use client";

import { useCallback, useEffect, useState } from "react";

import {
  executeTrade,
  getPortfolio,
  getPortfolioRisk,
  getPortfolios,
  getPortfolioSummary,
} from "../api/portfolio-api";

import type {
  Portfolio,
  PortfolioRiskMetrics,
  PortfolioSummary,
  PortfolioTransaction,
  TradeInput,
} from "../types";

export function usePortfolio() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);

  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string | null>(
    null,
  );

  const [summary, setSummary] = useState<PortfolioSummary | null>(null);

  const [transactions, setTransactions] = useState<PortfolioTransaction[]>([]);

  const [risk, setRisk] = useState<PortfolioRiskMetrics | null>(null);

  const [loading, setLoading] = useState(true);
  const [submittingTrade, setSubmittingTrade] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const loadSelectedPortfolio = useCallback(async (portfolioId: string) => {
    setLoading(true);
    setError(null);

    try {
      const [summaryResponse, detailResponse, riskResponse] = await Promise.all(
        [
          getPortfolioSummary(portfolioId),
          getPortfolio(portfolioId),
          getPortfolioRisk(portfolioId),
        ],
      );

      setSummary(summaryResponse);
      setRisk(riskResponse);

      setTransactions([...detailResponse.transactions].reverse());
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load portfolio",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    async function loadPortfolioList() {
      try {
        const response = await getPortfolios();

        setPortfolios(response.data);

        if (response.data.length > 0) {
          setSelectedPortfolioId(response.data[0].id);
        } else {
          setLoading(false);
        }
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load portfolios",
        );
        setLoading(false);
      }
    }

    void loadPortfolioList();
  }, []);

  useEffect(() => {
    if (selectedPortfolioId) {
      void loadSelectedPortfolio(selectedPortfolioId);
    }
  }, [selectedPortfolioId, loadSelectedPortfolio]);

  async function submitTrade(input: TradeInput) {
    if (!selectedPortfolioId) {
      return;
    }

    setSubmittingTrade(true);
    setError(null);

    try {
      await executeTrade(selectedPortfolioId, input);

      await loadSelectedPortfolio(selectedPortfolioId);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Trade execution failed",
      );

      throw requestError;
    } finally {
      setSubmittingTrade(false);
    }
  }

  return {
    portfolios,
    selectedPortfolioId,
    summary,
    risk,
    transactions,
    loading,
    submittingTrade,
    error,
    setSelectedPortfolioId,
    submitTrade,
    retry: () => {
      if (selectedPortfolioId) {
        return loadSelectedPortfolio(selectedPortfolioId);
      }
    },
  };
}
