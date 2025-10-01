'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { algorandService } from '@/lib/algorand';
import { useWallet } from '@/hooks/useWallet';

interface CreateMarketFormProps {
  onMarketCreated?: () => void;
}

export function CreateMarketForm({ onMarketCreated }: CreateMarketFormProps) {
  const { walletState } = useWallet();
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    option1: '',
    option2: '',
    option3: '',
    odds1: '',
    odds2: '',
    odds3: '',
    duration: '24'
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCreateMarket = async () => {
    if (!walletState.address) return;

    // Validation
    if (!formData.title || !formData.option1 || !formData.option2) {
      alert('Please fill in all required fields');
      return;
    }

    const options = [formData.option1, formData.option2];
    const odds = [parseFloat(formData.odds1), parseFloat(formData.odds2)];

    if (formData.option3) {
      options.push(formData.option3);
      odds.push(parseFloat(formData.odds3));
    }

    // Validate odds
    if (odds.some(odd => isNaN(odd) || odd < 1.01 || odd > 100)) {
      alert('Please enter valid odds between 1.01 and 100.00');
      return;
    }

    setIsCreating(true);
    try {
      // Convert odds to scaled format (multiply by 100)
      const scaledOdds = odds.map(odd => Math.floor(odd * 100));
      
      const transaction = await algorandService.createMarket(
        walletState.address,
        formData.title,
        options,
        scaledOdds,
        parseInt(formData.duration)
      );

      console.log('Market creation transaction:', transaction);
      
      // In a real app, you'd sign and submit this transaction
      alert(`Market "${formData.title}" created successfully!`);
      
      // Reset form
      setFormData({
        title: '',
        option1: '',
        option2: '',
        option3: '',
        odds1: '',
        odds2: '',
        odds3: '',
        duration: '24'
      });
      
      onMarketCreated?.();
    } catch (error) {
      console.error('Failed to create market:', error);
      alert('Failed to create market. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  if (!walletState.connected) {
    return (
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Create Market</CardTitle>
          <CardDescription>
            Connect your wallet to create prediction markets
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Please connect your wallet to create markets
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Create New Market</CardTitle>
        <CardDescription>
          Create a sports prediction market for others to bet on
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {/* Market Title */}
          <div>
            <label className="text-sm font-medium">Market Title *</label>
            <Input
              placeholder="e.g., Manchester United vs Liverpool"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
            />
          </div>

          {/* Betting Options */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Betting Options *</label>
            
            <div className="grid grid-cols-2 gap-4">
              <Input
                placeholder="Option 1 (e.g., Home Team)"
                value={formData.option1}
                onChange={(e) => handleInputChange('option1', e.target.value)}
              />
              <Input
                type="number"
                placeholder="Odds (e.g., 1.80)"
                value={formData.odds1}
                onChange={(e) => handleInputChange('odds1', e.target.value)}
                min="1.01"
                max="100"
                step="0.01"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <Input
                placeholder="Option 2 (e.g., Draw)"
                value={formData.option2}
                onChange={(e) => handleInputChange('option2', e.target.value)}
              />
              <Input
                type="number"
                placeholder="Odds (e.g., 3.20)"
                value={formData.odds2}
                onChange={(e) => handleInputChange('odds2', e.target.value)}
                min="1.01"
                max="100"
                step="0.01"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <Input
                placeholder="Option 3 (optional, e.g., Away Team)"
                value={formData.option3}
                onChange={(e) => handleInputChange('option3', e.target.value)}
              />
              <Input
                type="number"
                placeholder="Odds (e.g., 2.10)"
                value={formData.odds3}
                onChange={(e) => handleInputChange('odds3', e.target.value)}
                min="1.01"
                max="100"
                step="0.01"
                disabled={!formData.option3}
              />
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="text-sm font-medium">Betting Duration (hours) *</label>
            <Input
              type="number"
              placeholder="24"
              value={formData.duration}
              onChange={(e) => handleInputChange('duration', e.target.value)}
              min="1"
              max="168"
            />
            <div className="text-xs text-gray-500 mt-1">
              How long users can place bets (1-168 hours)
            </div>
          </div>

          {/* Create Button */}
          <Button
            onClick={handleCreateMarket}
            disabled={isCreating || !formData.title || !formData.option1 || !formData.option2}
            className="w-full"
          >
            {isCreating ? 'Creating Market...' : 'Create Market'}
          </Button>

          {/* Info */}
          <div className="text-xs text-gray-500 space-y-1">
            <p>• You will be able to settle this market after the betting period ends</p>
            <p>• A 5% commission is charged on winnings</p>
            <p>• Minimum bet amount is 1 ALGO</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
