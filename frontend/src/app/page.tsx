'use client';

import { useState } from 'react';
import { useMarkets } from '@/hooks/useMarkets';
import { WalletConnection } from '@/components/WalletConnection';
import { MarketCard } from '@/components/MarketCard';
import { CreateMarketForm } from '@/components/CreateMarketForm';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  const { markets, loading, error, loadMarkets } = useMarkets();
  const [activeTab, setActiveTab] = useState<'markets' | 'create'>('markets');

  const handleMarketCreated = () => {
    loadMarkets();
    setActiveTab('markets');
  };

  const handleBetPlaced = () => {
    loadMarkets();
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Decentralized Sports Betting
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Bet on football matches using Algorand smart contracts. 
          Built with modern AlgoPy framework for transparent and secure predictions.
        </p>
      </div>

      {/* Wallet Connection */}
      <div className="flex justify-center">
        <WalletConnection />
      </div>

      {/* Navigation Tabs */}
      <div className="flex justify-center">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <Button
            variant={activeTab === 'markets' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('markets')}
            className="px-6"
          >
            Active Markets
          </Button>
          <Button
            variant={activeTab === 'create' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('create')}
            className="px-6"
          >
            Create Market
          </Button>
        </div>
      </div>

      {/* Content */}
      {activeTab === 'markets' && (
        <div className="space-y-6">
          <div className="text-center">
            <h3 className="text-2xl font-semibold mb-2">Active Markets</h3>
            <p className="text-gray-600">Place your bets on live football matches</p>
          </div>

          {loading && (
            <div className="text-center py-8">
              <div className="text-gray-500">Loading markets...</div>
            </div>
          )}

          {error && (
            <Card className="max-w-md mx-auto">
              <CardContent className="p-6">
                <div className="text-center text-red-600">
                  Error: {error}
                </div>
                <Button 
                  onClick={loadMarkets} 
                  className="w-full mt-4"
                  variant="outline"
                >
                  Retry
                </Button>
              </CardContent>
            </Card>
          )}

          {!loading && !error && markets.length === 0 && (
            <Card className="max-w-md mx-auto">
              <CardHeader>
                <CardTitle>No Markets Available</CardTitle>
                <CardDescription>
                  There are currently no active markets. Create one to get started!
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={() => setActiveTab('create')} 
                  className="w-full"
                >
                  Create First Market
                </Button>
              </CardContent>
            </Card>
          )}

          {!loading && !error && markets.length > 0 && (
            <div className="space-y-6">
              {markets.map((market) => (
                <div key={market.id} className="flex justify-center">
                  <MarketCard 
                    market={market} 
                    onBetPlaced={handleBetPlaced}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'create' && (
        <div className="space-y-6">
          <div className="text-center">
            <h3 className="text-2xl font-semibold mb-2">Create New Market</h3>
            <p className="text-gray-600">Set up a new sports betting market</p>
          </div>

          <div className="flex justify-center">
            <CreateMarketForm onMarketCreated={handleMarketCreated} />
          </div>
        </div>
      )}

      {/* Info Section */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h4 className="font-semibold text-blue-900 mb-2">How It Works</h4>
        <div className="grid md:grid-cols-3 gap-4 text-sm text-blue-800">
          <div>
            <div className="font-medium mb-1">1. Connect Wallet</div>
            <div>Connect your Algorand wallet to start betting</div>
          </div>
          <div>
            <div className="font-medium mb-1">2. Choose Market</div>
            <div>Select a match and betting option with fixed odds</div>
          </div>
          <div>
            <div className="font-medium mb-1">3. Place Bet & Win</div>
            <div>Place your bet and claim winnings after settlement</div>
          </div>
        </div>
      </div>

      {/* Technical Info */}
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Technical Features</CardTitle>
          <CardDescription>
            Built with cutting-edge Algorand technology
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h5 className="font-semibold mb-2">Smart Contract</h5>
              <ul className="space-y-1 text-gray-600">
                <li>• Modern AlgoPy framework (not PyTeal)</li>
                <li>• ARC4 compliant with ABI methods</li>
                <li>• Puya compiler for TEAL generation</li>
                <li>• Comprehensive security validation</li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-2">Features</h5>
              <ul className="space-y-1 text-gray-600">
                <li>• Fixed odds betting system</li>
                <li>• Multi-option markets (Home/Draw/Away)</li>
                <li>• Automatic payout calculation</li>
                <li>• 5% platform commission</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
