#!/usr/bin/env python3
"""
Sample usage script for the Algorand Prediction Market smart contract.
Demonstrates how to deploy, create markets, place bets, and claim winnings.
"""

import logging

import algokit_utils
from algokit_utils import ApplicationClient, Account
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk.account import generate_account
from algosdk.transaction import PaymentTxn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_clients() -> tuple[AlgodClient, IndexerClient]:
    """Set up Algorand clients for local development."""
    # For AlgoKit LocalNet
    algod_client = AlgodClient(
        algod_token="a" * 64,
        algod_address="http://localhost:4001"
    )
    
    indexer_client = IndexerClient(
        indexer_token="a" * 64,
        indexer_address="http://localhost:8980"
    )
    
    return algod_client, indexer_client


def create_and_fund_account(algod_client: AlgodClient, name: str, amount: int = 10_000_000) -> Account:
    """Create and fund a new account."""
    private_key, address = generate_account()
    account = Account(private_key=private_key, address=address)
    
    logger.info(f"Created {name} account: {address}")
    
    # Fund the account using AlgoKit's dispenser (LocalNet only)
    algokit_utils.ensure_funded(
        algod_client,
        algokit_utils.EnsureBalanceParameters(
            account_to_fund=address,
            min_spending_balance_micro_algos=amount,
        ),
    )
    
    logger.info(f"Funded {name} with {amount / 1_000_000} ALGOs")
    return account


def deploy_prediction_market(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    deployer: Account
) -> ApplicationClient:
    """Deploy the prediction market smart contract."""
    
    # Create application specification
    app_spec = algokit_utils.ApplicationSpecification.from_json({
        "hints": {},
        "source": {
            "approval": "",
            "clear": ""
        },
        "state": {
            "global": {
                "num_byte_slices": 32,
                "num_uints": 64
            },
            "local": {
                "num_byte_slices": 8,
                "num_uints": 16
            }
        },
        "schema": {
            "global": {
                "declared": {},
                "reserved": {}
            },
            "local": {
                "declared": {},
                "reserved": {}
            }
        },
        "contract": {
            "name": "PredictionMarket",
            "methods": []
        }
    })
    
    # Create application client
    app_client = ApplicationClient(
        algod_client=algod_client,
        app_spec=app_spec,
        creator=deployer,
        indexer_client=indexer_client,
    )
    
    logger.info("Deploying Prediction Market contract...")
    
    # Deploy the application
    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.ReplaceApp,
        on_update=algokit_utils.OnUpdate.UpdateApp,
    )
    
    # Fund the application account
    algokit_utils.ensure_funded(
        algod_client,
        algokit_utils.EnsureBalanceParameters(
            account_to_fund=app_client.app_address,
            min_spending_balance_micro_algos=10_000_000,  # 10 ALGOs
        ),
    )
    
    logger.info("✅ Contract deployed successfully!")
    logger.info(f"   App ID: {app_client.app_id}")
    logger.info(f"   App Address: {app_client.app_address}")
    
    return app_client


def create_sample_market(app_client: ApplicationClient) -> int:
    """Create a sample football market."""
    logger.info("Creating sample football market...")
    
    # Market details
    title = "Premier League: Manchester City vs Arsenal"
    options = ["Manchester City", "Draw", "Arsenal"]
    odds = [180, 320, 220]  # 1.80, 3.20, 2.20 (scaled by 100)
    duration_hours = 48  # 48 hours betting window
    
    # Create the market
    result = app_client.call(
        "create_market",
        title=title,
        options=options,
        odds=odds,
        duration_hours=duration_hours,
    )
    
    market_id = result.return_value
    logger.info(f"✅ Market created with ID: {market_id}")
    logger.info(f"   Title: {title}")
    logger.info(f"   Options: {options}")
    logger.info(f"   Odds: {[f'{odd/100:.2f}' for odd in odds]}")
    
    return market_id


def demonstrate_betting(
    app_client: ApplicationClient,
    algod_client: AlgodClient,
    market_id: int,
    bettors: list[Account]
) -> None:
    """Demonstrate betting functionality with multiple users."""
    logger.info("Demonstrating betting functionality...")
    
    # Opt all bettors into the application
    for i, bettor in enumerate(bettors):
        logger.info(f"Opting bettor {i+1} into the application...")
        app_client.opt_in(signer=bettor)
    
    # Betting scenarios
    bets = [
        (bettors[0], 0, 3_000_000, "Manchester City"),  # Bettor 1: 3 ALGO on City
        (bettors[1], 2, 2_000_000, "Arsenal"),         # Bettor 2: 2 ALGO on Arsenal
        (bettors[2], 1, 1_500_000, "Draw"),            # Bettor 3: 1.5 ALGO on Draw
        (bettors[0], 2, 1_000_000, "Arsenal"),         # Bettor 1: 1 ALGO on Arsenal (hedging)
    ]
    
    for bettor, option_index, amount, option_name in bets:
        logger.info(f"Placing bet: {amount/1_000_000} ALGO on {option_name}")
        
        # Create payment transaction
        payment_txn = PaymentTxn(
            sender=bettor.address,
            receiver=app_client.app_address,
            amt=amount,
            sp=algod_client.suggested_params(),
        )
        
        # Place the bet
        app_client.call(
            "place_bet",
            market_id=market_id,
            option_index=option_index,
            payment_txn=payment_txn,
            signer=bettor,
        )
        
        logger.info("✅ Bet placed successfully")
    
    # Check market state after betting
    market_info = app_client.call("get_market_info", market_id=market_id)
    market_data = market_info.return_value
    
    total_pool = market_data[4] / 1_000_000  # Convert to ALGOs
    option_pools = [pool.native / 1_000_000 for pool in market_data[3]]  # Convert to ALGOs
    
    logger.info("📊 Market state after betting:")
    logger.info(f"   Total pool: {total_pool} ALGO")
    logger.info(f"   Manchester City pool: {option_pools[0]} ALGO")
    logger.info(f"   Draw pool: {option_pools[1]} ALGO")
    logger.info(f"   Arsenal pool: {option_pools[2]} ALGO")


def check_user_positions(
    app_client: ApplicationClient,
    market_id: int,
    bettors: list[Account]
) -> None:
    """Check and display user positions."""
    logger.info("Checking user positions...")
    
    for i, bettor in enumerate(bettors):
        position = app_client.call(
            "get_user_position",
            market_id=market_id,
            user=bettor.address,
        )
        
        user_bets, total_bet, is_claimed = position.return_value
        
        logger.info(f"👤 Bettor {i+1} ({bettor.address[:8]}...):")
        logger.info(f"   Total bet: {total_bet.native / 1_000_000} ALGO")
        logger.info(f"   Claimed: {is_claimed.native}")
        
        if len(user_bets) > 0:
            bet_amounts = [bet.native / 1_000_000 for bet in user_bets]
            logger.info(f"   Bets by option: {bet_amounts} ALGO")


def simulate_market_settlement(
    app_client: ApplicationClient,
    market_id: int,
    winning_option: int
) -> None:
    """Simulate market settlement (in production, this would be done by an oracle)."""
    logger.info(f"Settling market with winning option: {winning_option}")
    
    # In a real scenario, you'd wait for the market to end
    # For demo purposes, we'll assume the market creator can settle
    
    try:
        app_client.call(
            "settle_market",
            market_id=market_id,
            winning_option=winning_option,
        )
        
        logger.info("✅ Market settled successfully")
        
        # Check updated market info
        market_info = app_client.call("get_market_info", market_id=market_id)
        market_data = market_info.return_value
        
        status = market_data[6]  # Status
        winning_opt = market_data[7]  # Winning option
        
        option_names = ["Manchester City", "Draw", "Arsenal"]
        logger.info(f"   Status: {status} (2 = settled)")
        logger.info(f"   Winning option: {option_names[winning_opt]} (index {winning_opt})")
        
    except Exception as e:
        logger.error(f"Failed to settle market: {e}")


def demonstrate_claiming(
    app_client: ApplicationClient,
    market_id: int,
    bettors: list[Account],
    winning_option: int
) -> None:
    """Demonstrate claiming winnings."""
    logger.info("Demonstrating winnings claims...")
    
    option_names = ["Manchester City", "Draw", "Arsenal"]
    logger.info(f"Winning option: {option_names[winning_option]}")
    
    for i, bettor in enumerate(bettors):
        try:
            # Check if user has winning bets
            position = app_client.call(
                "get_user_position",
                market_id=market_id,
                user=bettor.address,
            )
            
            user_bets, total_bet, is_claimed = position.return_value
            
            if len(user_bets) > winning_option and user_bets[winning_option].native > 0:
                logger.info(f"👤 Bettor {i+1} has winning bets, attempting to claim...")
                
                # Attempt to claim winnings
                result = app_client.call(
                    "claim_winnings",
                    market_id=market_id,
                    signer=bettor,
                )
                
                payout = result.return_value / 1_000_000  # Convert to ALGOs
                logger.info(f"✅ Claimed {payout} ALGO in winnings")
                
            else:
                logger.info(f"👤 Bettor {i+1} has no winning bets")
                
        except Exception as e:
            logger.info(f"👤 Bettor {i+1} claim failed: {e}")


def main():
    """Main demonstration function."""
    logger.info("🚀 Starting Algorand Prediction Market Demo")
    logger.info("=" * 50)
    
    try:
        # Setup
        algod_client, indexer_client = setup_clients()
        
        # Create accounts
        deployer = create_and_fund_account(algod_client, "Deployer", 20_000_000)
        bettors = [
            create_and_fund_account(algod_client, "Bettor 1", 15_000_000),
            create_and_fund_account(algod_client, "Bettor 2", 15_000_000),
            create_and_fund_account(algod_client, "Bettor 3", 15_000_000),
        ]
        
        # Deploy contract
        app_client = deploy_prediction_market(algod_client, indexer_client, deployer)
        
        # Create market
        market_id = create_sample_market(app_client)
        
        # Demonstrate betting
        demonstrate_betting(app_client, algod_client, market_id, bettors)
        
        # Check positions
        check_user_positions(app_client, market_id, bettors)
        
        # Simulate settlement (Arsenal wins in this demo)
        winning_option = 2  # Arsenal
        simulate_market_settlement(app_client, market_id, winning_option)
        
        # Demonstrate claiming
        demonstrate_claiming(app_client, market_id, bettors, winning_option)
        
        logger.info("=" * 50)
        logger.info("✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
