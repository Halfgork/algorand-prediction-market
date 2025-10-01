'use client';

import { useState, useEffect, useCallback } from 'react';
import { Market, UserPosition } from '@/types/algorand';
import { algorandService } from '@/lib/algorand';

export function useMarkets() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadMarkets = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock data for development - in production, fetch from blockchain
      const mockMarkets: Market[] = [
        {
          id: 1,
          title: 'Manchester City vs Arsenal',
          options: ['Manchester City', 'Draw', 'Arsenal'],
          odds: [180, 320, 220],
          optionPools: [5_000_000, 2_000_000, 3_000_000], // in microAlgos
          totalPool: 10_000_000,
          endTime: Date.now() + 24 * 60 * 60 * 1000, // 24 hours from now
          status: 0, // Active
          winningOption: 0,
          creator: 'CREATOR_ADDRESS_HERE',
        },
        {
          id: 2,
          title: 'Liverpool vs Chelsea',
          options: ['Liverpool', 'Draw', 'Chelsea'],
          odds: [150, 280, 300],
          optionPools: [8_000_000, 3_000_000, 4_000_000],
          totalPool: 15_000_000,
          endTime: Date.now() + 48 * 60 * 60 * 1000, // 48 hours from now
          status: 0, // Active
          winningOption: 0,
          creator: 'CREATOR_ADDRESS_HERE',
        },
      ];
      
      setMarkets(mockMarkets);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load markets');
    } finally {
      setLoading(false);
    }
  }, []);

  const getMarket = useCallback(async (marketId: number): Promise<Market | null> => {
    try {
      return await algorandService.getMarketInfo(marketId);
    } catch (err) {
      console.error('Failed to get market:', err);
      return null;
    }
  }, []);

  const getUserPosition = useCallback(async (
    marketId: number,
    userAddress: string
  ): Promise<UserPosition | null> => {
    try {
      return await algorandService.getUserPosition(marketId, userAddress);
    } catch (err) {
      console.error('Failed to get user position:', err);
      return null;
    }
  }, []);

  useEffect(() => {
    loadMarkets();
  }, [loadMarkets]);

  return {
    markets,
    loading,
    error,
    loadMarkets,
    getMarket,
    getUserPosition,
  };
}
