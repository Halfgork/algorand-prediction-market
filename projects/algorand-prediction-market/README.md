# Algorand Prediction Market

A modern prediction market smart contract built on Algorand using AlgoPy framework and Puya compiler for sports betting.

## ✅ Project Status

- **Smart Contract**: ✅ Compiles and builds successfully
- **Dependencies**: ✅ All development tools installed (ruff, mypy, pytest)
- **Linting**: ✅ Passes ruff checks with no errors
- **Type Checking**: ✅ Passes mypy validation
- **Architecture**: ✅ All 6 core methods implemented and working

## Features

- **Modern AlgoPy**: Built with latest Algorand Python framework
- **Dynamic Markets**: Create markets with 2-10 betting options  
- **Flexible Odds**: Support for any odds between 1.01x and 100.00x
- **Multiple Markets**: Create and manage concurrent prediction markets
- **Secure Betting**: Comprehensive validation and payment verification
- **Auto Settlement**: Market creators can settle and distribute winnings
- **Commission System**: 5% house edge with transparent calculations

## Smart Contract Methods

The contract implements all required ABI methods:

- `create_market(title, options, odds, duration_hours)` - Create new prediction markets
- `place_bet(market_id, option_index, payment_txn)` - Place bets with payment validation
- `settle_market(market_id, winning_option)` - Settle markets (creator only)
- `claim_winnings(market_id)` - Claim proportional payouts from winning bets
- `get_market_info(market_id)` - Query comprehensive market data
- `get_user_position(market_id, user)` - Get user's betting positions

## Quick Start

### Prerequisites
- Python 3.12+
- Poetry for dependency management
- Docker (for AlgoKit LocalNet)
- AlgoKit CLI

### 1. Setup Project
```bash
cd algorand-prediction-market/projects/algorand-prediction-market
poetry install
```

### 2. Verify Build
```bash
# Run comprehensive build verification
poetry run python build_and_verify.py

# Or individual steps:
poetry run ruff check .                              # Linting
poetry run mypy smart_contracts --ignore-missing-imports  # Type checking
poetry run algokit compile python smart_contracts/prediction_market/contract.py  # Compilation
```

### 3. Start LocalNet
```bash
algokit localnet start
```

### 4. Deploy Contract
```bash
algokit project deploy localnet
```

### 5. Run Demo
```bash
poetry run python examples/sample_usage.py
```

## Development Workflow

### Build and Test
```bash
# Install dependencies
poetry install

# Lint code
poetry run ruff check .
poetry run ruff check . --fix  # Auto-fix issues

# Type checking
poetry run mypy smart_contracts --ignore-missing-imports

# Compile contract
poetry run algokit compile python smart_contracts/prediction_market/contract.py

# Build all contracts
poetry run python -m smart_contracts build

# Run full verification
poetry run python build_and_verify.py
```

## Usage Example

```python
# Create a football market
market_id = app_client.call(
    "create_market",
    title="Premier League: Man City vs Arsenal",
    options=["Man City", "Draw", "Arsenal"],
    odds=[180, 320, 220],  # 1.80, 3.20, 2.20 odds (scaled by 100)
    duration_hours=48,     # 48-hour betting window
)

# Place a bet on Man City
app_client.call(
    "place_bet",
    market_id=market_id,
    option_index=0,        # Bet on Man City (index 0)
    payment_txn=payment_txn,  # 1+ ALGO payment transaction
    signer=bettor_account,
)

# Market creator settles after match ends
app_client.call(
    "settle_market", 
    market_id=market_id,
    winning_option=0,      # Man City won
    signer=creator_account,
)

# Winners claim their payouts
payout = app_client.call(
    "claim_winnings",
    market_id=market_id,
    signer=winning_bettor,
)
```

## Testing

```bash
# Requires LocalNet to be running
poetry run pytest tests/prediction_market_test.py -v
```

## Architecture

### Smart Contract Structure
- **Global State**: Market metadata, options, odds, pools, timing, status
- **Local State**: User betting positions and claim status per market
- **ARC4 Types**: Modern type system with dynamic arrays and structured data
- **Security**: Input validation, access control, payment verification

### Market Lifecycle
1. **Creation**: Creator defines title, options (2-10), odds, duration
2. **Active**: Users place bets, funds accumulate in option pools
3. **Ended**: Betting window closes, awaiting settlement
4. **Settled**: Creator determines winner, enables claiming
5. **Claimed**: Winners collect proportional payouts

### Economics
- **Minimum Bet**: 1 ALGO per bet
- **Commission**: 5% house edge on all bets
- **Payout Formula**: `user_bet / winning_pool * total_pool`
- **Proportional**: Winners share the total pool proportionally

## Project Structure

```
smart_contracts/
├── prediction_market/
│   ├── contract.py          # Main AlgoPy smart contract
│   └── deploy_config.py     # Deployment configuration
tests/
├── prediction_market_test.py # Comprehensive test suite
examples/
├── sample_usage.py          # Complete demo script
build_and_verify.py          # Build verification tool
```

## Development Tools

- **AlgoPy**: Modern Python framework for Algorand smart contracts
- **Puya**: AlgoPy compiler for generating TEAL bytecode
- **AlgoKit**: Development toolkit and LocalNet management
- **Poetry**: Python dependency and virtual environment management
- **Ruff**: Fast Python linter with auto-fix capabilities
- **MyPy**: Static type checking for Python code
- **Pytest**: Testing framework with async support

## Troubleshooting

### Common Issues
1. **Compilation Errors**: Ensure AlgoPy syntax compatibility
2. **Test Failures**: LocalNet must be running for integration tests
3. **Type Errors**: Use proper ARC4 types and .copy() for mutable references
4. **Deployment Issues**: Check AlgoKit configuration and network connectivity

### Getting Help
- Check build logs: `poetry run python build_and_verify.py`
- Verify dependencies: `poetry install`
- Test compilation: `poetry run algokit compile python smart_contracts/prediction_market/contract.py`

Built with ❤️ using AlgoPy framework for modern Algorand development.