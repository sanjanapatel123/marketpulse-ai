"use client";

import { useCallback, useEffect, useState } from "react";

import {
  addWatchlistItem,
  createPriceAlert,
  createWatchlist,
  getWatchlistDetail,
  getWatchlists,
  removeWatchlistItem,
} from "../api/watchlist-api";

import type {
  AddWatchlistItemInput,
  CreatePriceAlertInput,
  CreateWatchlistInput,
  Watchlist,
  WatchlistDetail,
} from "../types/watchlist";

const REFRESH_INTERVAL_MS = 10_000;

export function useWatchlists() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);

  const [selectedWatchlistId, setSelectedWatchlistId] = useState<string | null>(
    null,
  );

  const [detail, setDetail] = useState<WatchlistDetail | null>(null);

  const [isLoadingWatchlists, setIsLoadingWatchlists] = useState(true);

  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const loadWatchlists = useCallback(async () => {
    try {
      setError(null);

      const response = await getWatchlists();

      setWatchlists(response.data);

      setSelectedWatchlistId((currentId) => {
        if (
          currentId &&
          response.data.some((watchlist) => watchlist.id === currentId)
        ) {
          return currentId;
        }

        return response.data[0]?.id ?? null;
      });
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load watchlists",
      );
    } finally {
      setIsLoadingWatchlists(false);
    }
  }, []);

  const loadWatchlistDetail = useCallback(
    async (watchlistId: string, showLoading = true) => {
      try {
        if (showLoading) {
          setIsLoadingDetail(true);
        }

        setError(null);

        const response = await getWatchlistDetail(watchlistId);

        setDetail(response);
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load watchlist details",
        );
      } finally {
        if (showLoading) {
          setIsLoadingDetail(false);
        }
      }
    },
    [],
  );

  useEffect(() => {
    void loadWatchlists();
  }, [loadWatchlists]);

  useEffect(() => {
    if (!selectedWatchlistId) {
      setDetail(null);
      return;
    }

    void loadWatchlistDetail(selectedWatchlistId);

    const intervalId = window.setInterval(() => {
      // Silent refresh: UI loading skeleton will not flash.
      void loadWatchlistDetail(selectedWatchlistId, false);
    }, REFRESH_INTERVAL_MS);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [selectedWatchlistId, loadWatchlistDetail]);

  const selectWatchlist = useCallback((watchlistId: string) => {
    setSelectedWatchlistId(watchlistId);
  }, []);

  const handleCreateWatchlist = useCallback(
    async (payload: CreateWatchlistInput) => {
      try {
        setIsSubmitting(true);
        setError(null);

        const created = await createWatchlist(payload);

        await loadWatchlists();
        setSelectedWatchlistId(created.id);

        return created;
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : "Unable to create watchlist";

        setError(message);
        throw requestError;
      } finally {
        setIsSubmitting(false);
      }
    },
    [loadWatchlists],
  );

  const handleAddItem = useCallback(
    async (payload: AddWatchlistItemInput) => {
      if (!selectedWatchlistId) {
        throw new Error("Select a watchlist first");
      }

      try {
        setIsSubmitting(true);
        setError(null);

        const created = await addWatchlistItem(selectedWatchlistId, payload);

        await loadWatchlistDetail(selectedWatchlistId, false);

        return created;
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : "Unable to add stock";

        setError(message);
        throw requestError;
      } finally {
        setIsSubmitting(false);
      }
    },
    [selectedWatchlistId, loadWatchlistDetail],
  );

  const handleRemoveItem = useCallback(
    async (symbol: string) => {
      if (!selectedWatchlistId) {
        throw new Error("Select a watchlist first");
      }

      try {
        setIsSubmitting(true);
        setError(null);

        await removeWatchlistItem(selectedWatchlistId, symbol);

        await loadWatchlistDetail(selectedWatchlistId, false);
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : "Unable to remove stock";

        setError(message);
        throw requestError;
      } finally {
        setIsSubmitting(false);
      }
    },
    [selectedWatchlistId, loadWatchlistDetail],
  );

  const handleCreateAlert = useCallback(
    async (payload: CreatePriceAlertInput) => {
      if (!selectedWatchlistId) {
        throw new Error("Select a watchlist first");
      }

      try {
        setIsSubmitting(true);
        setError(null);

        const created = await createPriceAlert(selectedWatchlistId, payload);

        await loadWatchlistDetail(selectedWatchlistId, false);

        return created;
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : "Unable to create price alert";

        setError(message);
        throw requestError;
      } finally {
        setIsSubmitting(false);
      }
    },
    [selectedWatchlistId, loadWatchlistDetail],
  );

  const refresh = useCallback(async () => {
    if (!selectedWatchlistId) {
      await loadWatchlists();
      return;
    }

    await loadWatchlistDetail(selectedWatchlistId, false);
  }, [selectedWatchlistId, loadWatchlists, loadWatchlistDetail]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    watchlists,
    selectedWatchlistId,
    detail,

    isLoadingWatchlists,
    isLoadingDetail,
    isSubmitting,
    error,

    selectWatchlist,
    createWatchlist: handleCreateWatchlist,
    addItem: handleAddItem,
    removeItem: handleRemoveItem,
    createAlert: handleCreateAlert,
    refresh,
    clearError,
  };
}
