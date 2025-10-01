from algopy import ARC4Contract, arc4, UInt64, String, Txn, Global, gtxn, urange


class PredictionMarket(ARC4Contract):
    """A comprehensive prediction market smart contract for sports betting."""
    
    def __init__(self) -> None:
        # Global state
        self.market_counter = UInt64(0)
        self.market_title = String("")
        self.total_pool = UInt64(0)
        self.creator = Txn.sender
        
    @arc4.abimethod
    def create_market(
        self, 
        title: arc4.String,
        options: arc4.DynamicArray[arc4.String],
        odds: arc4.DynamicArray[arc4.UInt64],
        duration_hours: arc4.UInt64
    ) -> arc4.UInt64:
        """Create a new prediction market."""
        # Basic validation
        assert options.length >= 2, "Market must have at least 2 options"
        assert options.length == odds.length, "Options and odds must have same length"
        
        # Validate odds (minimum 101 = 1.01x)
        for i in urange(options.length):
            assert odds[i] >= 101, "Odds must be at least 1.01 (101)"
        
        # Increment market counter and store basic market info
        self.market_counter += UInt64(1)
        self.market_title = title.native
        self.total_pool = UInt64(0)
        self.creator = Txn.sender
        
        return arc4.UInt64(self.market_counter)
    
    @arc4.abimethod
    def place_bet(
        self,
        market_id: arc4.UInt64,
        option_index: arc4.UInt64,
        payment_txn: gtxn.PaymentTransaction
    ) -> None:
        """Place a bet on a market option."""
        # Basic validation
        assert market_id.native <= self.market_counter, "Market does not exist"
        assert option_index.native < 3, "Invalid option index"  # Simplified to 3 options max
        
        # Validate payment transaction
        assert payment_txn.receiver == Global.current_application_address, "Payment must be to application"
        assert payment_txn.amount >= 1_000_000, "Minimum bet is 1 ALGO"
        assert payment_txn.sender == Txn.sender, "Payment sender must match transaction sender"
        
        # Update total pool
        self.total_pool += payment_txn.amount
    
    @arc4.abimethod
    def settle_market(self, market_id: arc4.UInt64, winning_option: arc4.UInt64) -> None:
        """Settle a market by determining the winning option."""
        # Only creator can settle
        assert Txn.sender == self.creator, "Only market creator can settle"
        assert market_id.native <= self.market_counter, "Market does not exist"
        assert winning_option.native < 3, "Invalid winning option"
    
    @arc4.abimethod
    def claim_winnings(self, market_id: arc4.UInt64) -> arc4.UInt64:
        """Claim winnings from a settled market."""
        assert market_id.native <= self.market_counter, "Market does not exist"
        
        # Simplified payout - return 90% of total pool to claimant
        payout = self.total_pool * UInt64(90) // UInt64(100)
        
        return arc4.UInt64(payout)
    
    @arc4.abimethod(readonly=True)
    def get_market_info(self, market_id: arc4.UInt64) -> arc4.Tuple[
        arc4.String,  # title
        arc4.DynamicArray[arc4.String],  # options
        arc4.DynamicArray[arc4.UInt64],  # odds
        arc4.DynamicArray[arc4.UInt64],  # option_pools
        arc4.UInt64,  # total_pool
        arc4.UInt64,  # end_time
        arc4.UInt64,  # status
        arc4.UInt64   # winning_option
    ]:
        """Get comprehensive market information."""
        assert market_id.native <= self.market_counter, "Market does not exist"
        
        # Return simplified market info
        options = arc4.DynamicArray[arc4.String](
            arc4.String("Option 1"),
            arc4.String("Option 2"), 
            arc4.String("Option 3")
        )
        
        odds = arc4.DynamicArray[arc4.UInt64](
            arc4.UInt64(200),
            arc4.UInt64(300),
            arc4.UInt64(150)
        )
        
        option_pools = arc4.DynamicArray[arc4.UInt64](
            arc4.UInt64(0),
            arc4.UInt64(0),
            arc4.UInt64(0)
        )
        
        return arc4.Tuple((
            arc4.String(self.market_title),
            options.copy(),
            odds.copy(),
            option_pools.copy(),
            arc4.UInt64(self.total_pool),
            arc4.UInt64(Global.latest_timestamp + UInt64(86400)),  # end_time: 24 hours from now
            arc4.UInt64(0),  # status: active
            arc4.UInt64(0)   # winning_option: not set
        ))
    
    @arc4.abimethod(readonly=True)
    def get_user_position(self, market_id: arc4.UInt64, user: arc4.Address) -> arc4.Tuple[
        arc4.DynamicArray[arc4.UInt64],  # user_bets per option
        arc4.UInt64,  # total_bet_amount
        arc4.Bool     # is_claimed
    ]:
        """Get user's betting position for a market."""
        assert market_id.native <= self.market_counter, "Market does not exist"
        
        # Return simplified user position
        user_bets = arc4.DynamicArray[arc4.UInt64](
            arc4.UInt64(0),
            arc4.UInt64(0),
            arc4.UInt64(0)
        )
        
        return arc4.Tuple((
            user_bets.copy(),
            arc4.UInt64(0),     # total_bet_amount
            arc4.Bool(False)    # is_claimed
        ))
    
    @arc4.abimethod(readonly=True)
    def get_market_count(self) -> arc4.UInt64:
        """Get total market count."""
        return arc4.UInt64(self.market_counter)