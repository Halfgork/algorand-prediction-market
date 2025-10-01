# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Quick Start Development Environment
```bash
# Start entire development stack (LocalNet + Smart Contract + Frontend)
./start-dev.sh
```

### Smart Contract Development (AlgoPy)
```bash
cd projects/algorand-prediction-market

# Install Python dependencies
poetry install

# Start Algorand LocalNet
algokit localnet start

# Deploy contract to LocalNet
algokit project deploy localnet

# Run tests
poetry run pytest tests/prediction_market_test.py -v

# Run build verification script
poetry run python build_and_verify.py

# Linting and type checking
poetry run ruff check .
poetry run mypy smart_contracts --ignore-missing-imports

# Run example usage
poetry run python examples/sample_usage.py
```

### Frontend Development (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Linting
npm run lint
```

## Architecture Overview

### Project Structure
- **Workspace Root**: AlgoKit workspace orchestrating multiple projects
- **Smart Contract**: `projects/algorand-prediction-market/` - AlgoPy prediction market contract
- **Frontend**: `frontend/` - Next.js React application with Algorand integration
- **Integration Scripts**: Root-level scripts for coordinated development

### Smart Contract Architecture (AlgoPy)
- **Contract**: `smart_contracts/prediction_market/contract.py` - Main PredictionMarket ARC4Contract
- **Core Methods**:
  - `create_market()` - Create prediction markets with title, options, odds
  - `place_bet()` - Submit bets with payment verification  
  - `settle_market()` - Resolve markets and determine winners
  - `claim_winnings()` - Collect payouts from winning positions
  - `get_market_info()` - Query market data (readonly)
  - `get_user_position()` - Query user betting positions (readonly)

### Frontend Architecture (Next.js 15)
- **Framework**: Next.js App Router with TypeScript and Tailwind CSS
- **Algorand Integration**: `src/lib/algorand.ts` - AlgorandService class wrapping algosdk
- **Components**:
  - `MarketCard.tsx` - Market display and betting interface
  - `CreateMarketForm.tsx` - Market creation form
  - `WalletConnection.tsx` - Wallet integration (mock for development)
- **Hooks**:
  - `useMarkets.ts` - Market data management and state
  - `useWallet.ts` - Wallet connection and account management
- **Types**: `src/types/algorand.ts` - TypeScript definitions for Market, UserPosition, etc.

### Integration Layer
- **AlgorandService**: Centralized service for smart contract interactions
- **Transaction Building**: Constructs application calls and payment transactions
- **Mock Data**: Development-time simulation of contract responses
- **Path Aliases**: TypeScript paths configured for `@/` imports

## Development Notes

### LocalNet Requirements
- Algorand LocalNet must be running for contract deployment and testing
- Default ports: Algod (4001), Indexer (8980)
- Use `algokit localnet start` to initialize

### Contract Development
- Uses AlgoPy framework with Puya compiler
- ARC4 contract pattern with typed method signatures
- Global state for market data, local state for user positions
- Poetry manages Python dependencies and virtual environment

### Frontend Development
- Next.js 15 with React 18 and TypeScript
- Tailwind CSS with shadcn/ui components
- Mock wallet integration for development (Pera Wallet ready for production)
- Real-time market updates through hooks

### Testing Strategy
- Python: pytest for contract unit tests
- Requires LocalNet for integration testing
- Frontend: Next.js testing setup ready for expansion

### Key Dependencies
- **Smart Contract**: algopy, algokit-utils, algorand-python
- **Frontend**: next, react, algosdk, @algorandfoundation/algokit-utils
- **Development**: poetry (Python), npm (Node.js)