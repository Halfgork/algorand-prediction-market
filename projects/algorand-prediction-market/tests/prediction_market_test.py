import pytest
import algokit_utils
from algokit_utils import ApplicationClient
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk.account import generate_account
from algosdk.transaction import PaymentTxn


class TestPredictionMarket:
    """Test suite for the Prediction Market smart contract."""

    @pytest.fixture(scope="class")
    def app_client(
        self, algod_client: AlgodClient, indexer_client: IndexerClient
    ) -> ApplicationClient:
        """Create and deploy the prediction market application."""

        # Generate deployer account
        deployer_private_key, deployer_address = generate_account()
        deployer = algokit_utils.Account(
            private_key=deployer_private_key,
            address=deployer_address,
        )

        # Fund deployer account
        algokit_utils.ensure_funded(
            algod_client,
            algokit_utils.EnsureBalanceParameters(
                account_to_fund=deployer_address,
                min_spending_balance_micro_algos=10_000_000,  # 10 ALGOs
            ),
        )

        # Create application client
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

        app_client = ApplicationClient(
            algod_client=algod_client,
            app_spec=app_spec,
            creator=deployer,
            indexer_client=indexer_client,
        )

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
                min_spending_balance_micro_algos=5_000_000,  # 5 ALGOs
            ),
        )

        return app_client

    @pytest.fixture
    def bettor_account(self, algod_client: AlgodClient) -> algokit_utils.Account:
        """Create and fund a bettor account for testing."""
        private_key, address = generate_account()
        account = algokit_utils.Account(private_key=private_key, address=address)

        # Fund the account
        algokit_utils.ensure_funded(
            algod_client,
            algokit_utils.EnsureBalanceParameters(
                account_to_fund=address,
                min_spending_balance_micro_algos=20_000_000,  # 20 ALGOs
            ),
        )

        return account

    def test_create_market(self, app_client: ApplicationClient):
        """Test creating a new prediction market."""
        # Market parameters
        title = "Manchester United vs Liverpool"
        options = ["Manchester United", "Draw", "Liverpool"]
        odds = [200, 350, 180]  # 2.00, 3.50, 1.80 odds
        duration_hours = 48  # 48 hours

        # Create market
        result = app_client.call(
            "create_market",
            title=title,
            options=options,
            odds=odds,
            duration_hours=duration_hours,
        )

        market_id = result.return_value
        assert market_id == 1, "First market should have ID 1"

        # Verify market info
        market_info = app_client.call(
            "get_market_info",
            market_id=market_id,
        )

        market_data = market_info.return_value
        assert market_data[0] == title, "Market title should match"
        assert len(market_data[1]) == 3, "Should have 3 options"
        assert market_data[4] == 0, "Initial total pool should be 0"
        assert market_data[6] == 0, "Market should be active (status 0)"

    def test_create_market_validation(self, app_client: ApplicationClient):
        """Test market creation validation."""
        # Test with insufficient options
        with pytest.raises(Exception):
            app_client.call(
                "create_market",
                title="Invalid Market",
                options=["Only One"],
                odds=[200],
                duration_hours=24,
            )

        # Test with mismatched options and odds
        with pytest.raises(Exception):
            app_client.call(
                "create_market",
                title="Mismatched Market",
                options=["Option1", "Option2"],
                odds=[200],  # Only one odd for two options
                duration_hours=24,
            )

        # Test with invalid odds (too low)
        with pytest.raises(Exception):
            app_client.call(
                "create_market",
                title="Low Odds Market",
                options=["Option1", "Option2"],
                odds=[50, 200],  # 0.50 odds too low
                duration_hours=24,
            )

    def test_place_bet(
        self, 
        app_client: ApplicationClient, 
        bettor_account: algokit_utils.Account,
        algod_client: AlgodClient
    ):
        """Test placing bets on a market."""
        # First create a market
        title = "Real Madrid vs Barcelona"
        options = ["Real Madrid", "Draw", "Barcelona"]
        odds = [180, 300, 220]
        duration_hours = 24

        create_result = app_client.call(
            "create_market",
            title=title,
            options=options,
            odds=odds,
            duration_hours=duration_hours,
        )
        market_id = create_result.return_value

        # Opt the bettor into the application
        app_client.opt_in(signer=bettor_account)

        # Place a bet on option 0 (Real Madrid)
        bet_amount = 2_000_000  # 2 ALGOs
        option_index = 0

        # Create payment transaction
        payment_txn = PaymentTxn(
            sender=bettor_account.address,
            receiver=app_client.app_address,
            amt=bet_amount,
            sp=algod_client.suggested_params(),
        )

        # Place bet
        app_client.call(
            "place_bet",
            market_id=market_id,
            option_index=option_index,
            payment_txn=payment_txn,
            signer=bettor_account,
        )

        # Verify market state updated
        market_info = app_client.call(
            "get_market_info",
            market_id=market_id,
        )
        market_data = market_info.return_value
        assert market_data[4] == bet_amount, "Total pool should equal bet amount"

        # Verify user position
        user_position = app_client.call(
            "get_user_position",
            market_id=market_id,
            user=bettor_account.address,
        )
        position_data = user_position.return_value
        assert position_data[1] == bet_amount, "User total bet should match"

    def test_multiple_bets(
        self,
        app_client: ApplicationClient,
        bettor_account: algokit_utils.Account,
        algod_client: AlgodClient
    ):
        """Test multiple bets from different users."""
        # Create market
        create_result = app_client.call(
            "create_market",
            title="Test Multiple Bets",
            options=["A", "B", "C"],
            odds=[200, 300, 150],
            duration_hours=24,
        )
        market_id = create_result.return_value

        # Create second bettor
        bettor2_private_key, bettor2_address = generate_account()
        bettor2 = algokit_utils.Account(
            private_key=bettor2_private_key,
            address=bettor2_address,
        )

        # Fund second bettor
        algokit_utils.ensure_funded(
            algod_client,
            algokit_utils.EnsureBalanceParameters(
                account_to_fund=bettor2_address,
                min_spending_balance_micro_algos=10_000_000,
            ),
        )

        # Opt both bettors into the application
        app_client.opt_in(signer=bettor_account)
        app_client.opt_in(signer=bettor2)

        # Bettor 1 bets on option A
        bet1_amount = 3_000_000  # 3 ALGOs
        payment_txn1 = PaymentTxn(
            sender=bettor_account.address,
            receiver=app_client.app_address,
            amt=bet1_amount,
            sp=algod_client.suggested_params(),
        )

        app_client.call(
            "place_bet",
            market_id=market_id,
            option_index=0,
            payment_txn=payment_txn1,
            signer=bettor_account,
        )

        # Bettor 2 bets on option B
        bet2_amount = 2_000_000  # 2 ALGOs
        payment_txn2 = PaymentTxn(
            sender=bettor2_address,
            receiver=app_client.app_address,
            amt=bet2_amount,
            sp=algod_client.suggested_params(),
        )

        app_client.call(
            "place_bet",
            market_id=market_id,
            option_index=1,
            payment_txn=payment_txn2,
            signer=bettor2,
        )

        # Verify total pool
        market_info = app_client.call("get_market_info", market_id=market_id)
        total_pool = market_info.return_value[4]
        assert total_pool == bet1_amount + bet2_amount

    def test_settle_market(self, app_client: ApplicationClient):
        """Test settling a market."""
        # Create market with short duration for testing
        create_result = app_client.call(
            "create_market",
            title="Quick Settlement Test",
            options=["Win", "Lose"],
            odds=[200, 200],
            duration_hours=1,  # 1 hour
        )
        market_id = create_result.return_value

        # Wait for market to end (in real test, you might mock time)
        # For now, we'll test the validation logic
        
        # Try to settle before market ends (should fail)
        with pytest.raises(Exception):
            app_client.call(
                "settle_market",
                market_id=market_id,
                winning_option=0,
            )

        # Test settling with invalid option
        with pytest.raises(Exception):
            app_client.call(
                "settle_market",
                market_id=market_id,
                winning_option=5,  # Invalid option index
            )

    def test_market_count(self, app_client: ApplicationClient):
        """Test getting market count."""
        initial_count = app_client.call("get_market_count").return_value

        # Create a new market
        app_client.call(
            "create_market",
            title="Count Test Market",
            options=["Yes", "No"],
            odds=[180, 220],
            duration_hours=24,
        )

        # Check count increased
        new_count = app_client.call("get_market_count").return_value
        assert new_count == initial_count + 1

    def test_bet_validation(
        self,
        app_client: ApplicationClient,
        bettor_account: algokit_utils.Account,
        algod_client: AlgodClient
    ):
        """Test bet placement validation."""
        # Create market
        create_result = app_client.call(
            "create_market",
            title="Validation Test",
            options=["Option1", "Option2"],
            odds=[200, 200],
            duration_hours=24,
        )
        market_id = create_result.return_value

        app_client.opt_in(signer=bettor_account)

        # Test betting on non-existent market
        with pytest.raises(Exception):
            payment_txn = PaymentTxn(
                sender=bettor_account.address,
                receiver=app_client.app_address,
                amt=1_000_000,
                sp=algod_client.suggested_params(),
            )
            app_client.call(
                "place_bet",
                market_id=999,  # Non-existent market
                option_index=0,
                payment_txn=payment_txn,
                signer=bettor_account,
            )

        # Test betting on invalid option
        with pytest.raises(Exception):
            payment_txn = PaymentTxn(
                sender=bettor_account.address,
                receiver=app_client.app_address,
                amt=1_000_000,
                sp=algod_client.suggested_params(),
            )
            app_client.call(
                "place_bet",
                market_id=market_id,
                option_index=5,  # Invalid option
                payment_txn=payment_txn,
                signer=bettor_account,
            )

        # Test minimum bet amount
        with pytest.raises(Exception):
            payment_txn = PaymentTxn(
                sender=bettor_account.address,
                receiver=app_client.app_address,
                amt=500_000,  # Below minimum (1 ALGO)
                sp=algod_client.suggested_params(),
            )
            app_client.call(
                "place_bet",
                market_id=market_id,
                option_index=0,
                payment_txn=payment_txn,
                signer=bettor_account,
            )
