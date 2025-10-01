'use client';

import { useWallet } from '@/hooks/useWallet';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function WalletConnection() {
  const { walletState, isConnecting, connectWallet, disconnectWallet } = useWallet();

  if (walletState.connected) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-lg">Wallet Connected</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div>
              <div className="text-sm text-gray-600">Address:</div>
              <div className="font-mono text-sm break-all">
                {walletState.address?.slice(0, 8)}...{walletState.address?.slice(-8)}
              </div>
            </div>
            
            <div>
              <div className="text-sm text-gray-600">Balance:</div>
              <div className="font-semibold">{walletState.balance.toFixed(2)} ALGO</div>
            </div>
            
            <Button 
              variant="outline" 
              onClick={disconnectWallet}
              className="w-full"
            >
              Disconnect
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-lg">Connect Wallet</CardTitle>
        <CardDescription>
          Connect your Algorand wallet to start betting
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button 
          onClick={connectWallet}
          disabled={isConnecting}
          className="w-full"
        >
          {isConnecting ? 'Connecting...' : 'Connect Wallet'}
        </Button>
        
        <div className="mt-4 text-xs text-gray-500 text-center">
          <p>This is a demo using mock wallet connection.</p>
          <p>In production, integrate with Pera Wallet or MyAlgo.</p>
        </div>
      </CardContent>
    </Card>
  );
}
