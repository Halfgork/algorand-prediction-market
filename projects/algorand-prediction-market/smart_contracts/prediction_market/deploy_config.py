import logging

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

logger = logging.getLogger(__name__)


# define deployment behaviour based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:

    app_client = algokit_utils.ApplicationClient(
        algod_client,
        app_spec,
        creator=deployer,
        indexer_client=indexer_client,
    )

    # Deploy the application
    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )

    # Fund the application account with some ALGOs for operation
    app_address = app_client.app_address
    
    # Fund with 10 ALGOs for contract operations
    funding_amount = 10_000_000  # 10 ALGOs in microAlgos
    
    logger.info(f"Funding application account {app_address} with {funding_amount / 1_000_000} ALGOs")
    
    algokit_utils.ensure_funded(
        algod_client,
        algokit_utils.EnsureBalanceParameters(
            account_to_fund=app_address,
            min_spending_balance_micro_algos=funding_amount,
            funding_source=deployer,
        )
    )

    logger.info("Prediction Market application deployed successfully!")
    logger.info(f"App ID: {app_client.app_id}")
    logger.info(f"App Address: {app_address}")
    
    # Optionally create a sample market for testing
    if logger.isEnabledFor(logging.INFO):
        try:
            # Sample market creation
            sample_title = "Chelsea vs Arsenal"
            sample_options = ["Chelsea", "Draw", "Arsenal"]
            sample_odds = [180, 320, 210]  # 1.80, 3.20, 2.10 odds
            duration_hours = 24  # 24 hours betting window
            
            logger.info("Creating sample market for testing...")
            result = app_client.call(
                "create_market",
                title=sample_title,
                options=sample_options,
                odds=sample_odds,
                duration_hours=duration_hours,
            )
            
            market_id = result.return_value
            logger.info(f"Sample market created with ID: {market_id}")
            
        except Exception as e:
            logger.warning(f"Failed to create sample market: {e}")


# Configuration for different deployment environments
def get_deploy_config() -> dict:
    """Get deployment configuration parameters."""
    return {
        "global_schema": {
            "num_uints": 64,  # Sufficient for all global state variables
            "num_byte_slices": 32,  # For strings and dynamic arrays
        },
        "local_schema": {
            "num_uints": 16,  # For user betting data
            "num_byte_slices": 8,  # For user state arrays
        },
        "extra_pages": 2,  # Additional program pages for complex logic
    }
