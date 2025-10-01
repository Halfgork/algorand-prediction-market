# Algorand Prediction Market Frontend

A modern React/Next.js frontend for the Algorand prediction market smart contract built with AlgoPy.

## Features

- **Modern UI**: Built with Next.js 15, React 18, and Tailwind CSS
- **Algorand Integration**: Direct smart contract interaction using AlgoSDK
- **Wallet Connection**: Mock wallet integration (ready for Pera Wallet/MyAlgo)
- **Real-time Updates**: Live market data and user positions
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Running Algorand LocalNet (for development)

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/                 # Next.js App Router
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # React components
│   ├── ui/            # Base UI components
│   ├── MarketCard.tsx # Market display & betting
│   ├── WalletConnection.tsx
│   └── CreateMarketForm.tsx
├── hooks/             # Custom React hooks
│   ├── useWallet.ts   # Wallet connection logic
│   └── useMarkets.ts  # Market data management
├── lib/               # Utilities
│   ├── utils.ts       # Helper functions
│   └── algorand.ts    # Algorand service layer
└── types/             # TypeScript definitions
    └── algorand.ts    # Algorand-specific types
```

## Smart Contract Integration

The frontend integrates with the AlgoPy smart contract through:

### Market Operations
- **View Markets**: Display active prediction markets
- **Place Bets**: Submit betting transactions
- **Check Positions**: View user's betting positions
- **Claim Winnings**: Collect payouts from winning bets

### Wallet Integration
- **Connection**: Mock wallet for development
- **Balance Display**: Show ALGO balance
- **Transaction Signing**: Prepare transactions for wallet

## Development Features

### Mock Data
The app includes mock data for development:
- Sample football markets
- Simulated wallet connection
- Test betting scenarios

### Error Handling
- Network connection errors
- Invalid transaction handling
- User-friendly error messages

### Responsive Design
- Mobile-first approach
- Tablet and desktop optimized
- Touch-friendly betting interface

## Production Deployment

### Wallet Integration
Replace mock wallet with real wallet providers:

```typescript
// Install wallet packages
npm install @perawallet/connect @walletconnect/client

// Update useWallet.ts with real wallet logic
import { PeraWalletConnect } from '@perawallet/connect';
```

### Environment Configuration
Create `.env.local` for production:

```env
NEXT_PUBLIC_ALGOD_SERVER=https://mainnet-api.algonode.cloud
NEXT_PUBLIC_ALGOD_PORT=443
NEXT_PUBLIC_INDEXER_SERVER=https://mainnet-idx.algonode.cloud
NEXT_PUBLIC_INDEXER_PORT=443
NEXT_PUBLIC_APP_ID=your_app_id
```

### Build for Production
```bash
npm run build
npm start
```

## API Integration

The frontend communicates with the smart contract via:

### Read Operations
- `get_market_info()`: Fetch market details
- `get_user_position()`: Get user's bets
- `get_market_count()`: Total markets

### Write Operations  
- `create_market()`: Create new markets
- `place_bet()`: Submit betting transactions
- `settle_market()`: Resolve markets (creator only)
- `claim_winnings()`: Collect payouts

## Styling

### Tailwind CSS
- Utility-first CSS framework
- Custom design system
- Dark mode ready
- Component variants

### shadcn/ui Components
- Accessible UI components
- Consistent design language
- Customizable themes

## Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# E2E tests
npm run test:e2e
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure responsive design
5. Submit pull request

## License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for the Algorand ecosystem**
