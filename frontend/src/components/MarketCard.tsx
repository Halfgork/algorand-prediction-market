'use client';

import { useState } from 'react';
import { Market, MarketStatus } from '@/types/algorand';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { algorandService } from '@/lib/algorand';
import { useWallet } from '@/hooks/useWallet';

interface MarketCardProps {
  market: Market;
  onBetPlaced?: () => void;
}

export function MarketCard({ market, onBetPlaced }: MarketCardProps) {
  const { walletState } = useWallet();
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [betAmount, setBetAmount] = useState('');
  const [isPlacingBet, setIsPlacingBet] = useState(false);

  const isActive = market.status === MarketStatus.ACTIVE;
  const hasEnded = market.endTime < Date.now();
  const canBet = isActive && !hasEnded && walletState.connected;

  const handlePlaceBet = async () => {
    if (!walletState.address || selectedOption === null || !betAmount) return;

    setIsPlacingBet(true);
    try {
      const betAmountMicroAlgos = algorandService.algosToMicroAlgos(parseFloat(betAmount));
      
      // This would typically open a wallet signing interface
      const transactions = await algorandService.placeBet(
        walletState.address,
        market.id,
        selectedOption,
        betAmountMicroAlgos
      );

      console.log('Bet transactions created:', transactions);
      
      // In a real app, you'd sign and submit these transactions
      alert(`Bet placed: ${betAmount} ALGO on ${market.options[selectedOption]}`);
      
      setBetAmount('');
      setSelectedOption(null);
      onBetPlaced?.();
    } catch (error) {
      console.error('Failed to place bet:', error);
      alert('Failed to place bet. Please try again.');
    } finally {
      setIsPlacingBet(false);
    }
  };

  const formatTimeRemaining = (endTime: number) => {
    const remaining = endTime - Date.now();
    if (remaining <= 0) return 'Ended';
    
    const hours = Math.floor(remaining / (1000 * 60 * 60));
    const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h remaining`;
    }
    
    return `${hours}h ${minutes}m remaining`;
  };

  const getStatusBadge = () => {
    switch (market.status) {
      case MarketStatus.ACTIVE:
        return hasEnded ? 
          <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">Ended</span> :
          <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Active</span>;
      case MarketStatus.SETTLED:
        return <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">Settled</span>;
      default:
        return <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">Unknown</span>;
    }
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl">{market.title}</CardTitle>
            <CardDescription className="mt-2">
              {formatTimeRemaining(market.endTime)}
            </CardDescription>
          </div>
          {getStatusBadge()}
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {/* Pool Information */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Pool Information</h4>
            <div className="text-sm text-gray-600">
              Total Pool: {algorandService.microAlgosToAlgos(market.totalPool).toFixed(2)} ALGO
            </div>
          </div>

          {/* Betting Options */}
          <div className="space-y-3">
            <h4 className="font-semibold">Betting Options</h4>
            {market.options.map((option, index) => {
              const odds = algorandService.formatOdds(market.odds[index]);
              const pool = algorandService.microAlgosToAlgos(market.optionPools[index]);
              const isSelected = selectedOption === index;
              
              return (
                <div
                  key={index}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  } ${!canBet ? 'opacity-50 cursor-not-allowed' : ''}`}
                  onClick={() => canBet && setSelectedOption(index)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">{option}</div>
                      <div className="text-sm text-gray-500">Pool: {pool.toFixed(2)} ALGO</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-lg">{odds}</div>
                      <div className="text-xs text-gray-500">odds</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Betting Interface */}
          {canBet && (
            <div className="border-t pt-4">
              <h4 className="font-semibold mb-3">Place Your Bet</h4>
              
              {selectedOption !== null && (
                <div className="space-y-3">
                  <div className="text-sm">
                    Betting on: <span className="font-medium">{market.options[selectedOption]}</span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Input
                      type="number"
                      placeholder="Amount in ALGO"
                      value={betAmount}
                      onChange={(e) => setBetAmount(e.target.value)}
                      min="1"
                      step="0.1"
                    />
                    <Button 
                      onClick={handlePlaceBet}
                      disabled={isPlacingBet || !betAmount || parseFloat(betAmount) < 1}
                    >
                      {isPlacingBet ? 'Placing...' : 'Place Bet'}
                    </Button>
                  </div>
                  
                  {betAmount && parseFloat(betAmount) >= 1 && (
                    <div className="text-sm text-gray-600">
                      Potential winnings: {algorandService.calculatePotentialWinnings(
                        parseFloat(betAmount), 
                        market.odds[selectedOption]
                      ).toFixed(2)} ALGO
                    </div>
                  )}
                </div>
              )}
              
              {selectedOption === null && (
                <div className="text-sm text-gray-500">
                  Select an option above to place your bet
                </div>
              )}
            </div>
          )}

          {/* Connection prompt */}
          {!walletState.connected && (
            <div className="text-center py-4 text-gray-500">
              Connect your wallet to place bets
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
