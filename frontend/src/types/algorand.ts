export interface Market {
  id: number;
  title: string;
  options: string[];
  odds: number[];
  optionPools: number[];
  totalPool: number;
  endTime: number;
  status: MarketStatus;
  winningOption: number;
  creator: string;
}

export enum MarketStatus {
  ACTIVE = 0,
  ENDED = 1,
  SETTLED = 2,
}

export interface UserPosition {
  userBets: number[];
  totalBetAmount: number;
  isClaimed: boolean;
}

export interface BetOption {
  index: number;
  name: string;
  odds: number;
  pool: number;
}

export interface WalletState {
  connected: boolean;
  address: string | null;
  balance: number;
}

export interface ContractConfig {
  appId: number;
  appAddress: string;
}

export interface BetTransaction {
  marketId: number;
  optionIndex: number;
  amount: number;
  txId?: string;
}
