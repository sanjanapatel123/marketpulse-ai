"use client";

import { useCallback, useEffect, useState } from "react";

import {
  getFundamentals,
  getPriceHistory,
  getQuote,
  getStocks,
} from "../api/market-api";

import type {
  FundamentalsResponse,
  HistoryRange,
  MarketQuote,
  PriceCandle,
  Stock,
} from "../types";

export function useMarketData() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState("RELIANCE");
  const [range, setRange] = useState<HistoryRange>(30);

  const [fundamentals, setFundamentals] = useState<FundamentalsResponse | null>(
    null,
  );

  const [quote, setQuote] = useState<MarketQuote | null>(null);
  const [candles, setCandles] = useState<PriceCandle[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMarketData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [quoteResponse, historyResponse, fundamentalsResponse] =
        await Promise.all([
          getQuote(selectedSymbol),
          getPriceHistory(selectedSymbol, range),
          getFundamentals(selectedSymbol),
        ]);

      setQuote(quoteResponse);
      setCandles(historyResponse.candles);
      setFundamentals(fundamentalsResponse);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load market data",
      );
    } finally {
      setLoading(false);
    }
  }, [selectedSymbol, range]);

  useEffect(() => {
    async function loadStocks() {
      try {
        const response = await getStocks();
        setStocks(response.data);
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load stocks",
        );
      }
    }

    void loadStocks();
  }, []);

  useEffect(() => {
    void loadMarketData();
  }, [loadMarketData]);

  return {
    stocks,
    selectedSymbol,
    range,
    quote,
    candles,
    fundamentals,
    loading,
    error,
    setSelectedSymbol,
    setRange,
    retry: loadMarketData,
  };
}
