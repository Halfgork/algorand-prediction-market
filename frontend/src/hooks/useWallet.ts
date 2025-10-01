'use client';

import { useState, useEffect, useCallback } from 'react';
import { WalletState } from '@/types/algorand';
import { algorandService } from '@/lib/algorand';

// Mock wallet connection for development
// In production, you would integrate with Pera Wallet, MyAlgo, or other wallets
export function useWallet() {
  const [walletState, setWalletState] = useState<WalletState>({
    connected: false,
    address: null,
    balance: 0,
  });

  const [isConnecting, setIsConnecting] = useState(false);

  const connectWallet = useCallback(async () => {
    setIsConnecting(true);
    try {
      // Mock wallet connection - in production, integrate with actual wallet
      const mockAddress = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
      
      // Get account info
      try {
        const accountInfo = await algorandService.getAccountInfo(mockAddress);
        setWalletState({
          connected: true,
          address: mockAddress,
          balance: algorandService.microAlgosToAlgos(accountInfo.amount),
        });
      } catch (error) {
        // If account doesn't exist, set balance to 0
        setWalletState({
          connected: true,
          address: mockAddress,
          balance: 0,
        });
      }
    } catch (error) {
      console.error('Failed to connect wallet:', error);
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const disconnectWallet = useCallback(() => {
    setWalletState({
      connected: false,
      address: null,
      balance: 0,
    });
  }, []);

  const updateBalance = useCallback(async () => {
    if (!walletState.address) return;
    
    try {
      const accountInfo = await algorandService.getAccountInfo(walletState.address);
      setWalletState(prev => ({
        ...prev,
        balance: algorandService.microAlgosToAlgos(accountInfo.amount),
      }));
    } catch (error) {
      console.error('Failed to update balance:', error);
    }
  }, [walletState.address]);

  useEffect(() => {
    // Check if wallet was previously connected (localStorage)
    const savedAddress = localStorage.getItem('wallet_address');
    if (savedAddress) {
      setWalletState(prev => ({
        ...prev,
        connected: true,
        address: savedAddress,
      }));
      // Update balance
      updateBalance();
    }
  }, [updateBalance]);

  useEffect(() => {
    // Save wallet state to localStorage
    if (walletState.connected && walletState.address) {
      localStorage.setItem('wallet_address', walletState.address);
    } else {
      localStorage.removeItem('wallet_address');
    }
  }, [walletState.connected, walletState.address]);

  return {
    walletState,
    isConnecting,
    connectWallet,
    disconnectWallet,
    updateBalance,
  };
}
