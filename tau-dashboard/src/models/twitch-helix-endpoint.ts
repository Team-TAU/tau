export interface TwitchHelixEndpoint {
  id: string;
  description: string;
  endpoint: string;
  method: string;
  reference_url: string;
  scope: string;
  token_type: string;
}

export interface EventsubSubscriptionResponse {
  total: number;
  data: EventsubSubscription[];
  maxTotalCost: number;
  totalCost: number;
  pagination: Pagination;
}

export interface Pagination {
  cursor?: string;
}

export interface EventsubSubscription {
  id: string;
  status: string;
  type: string;
  version: string;
  condition: Condition;
  createdAt: Date;
  transport: Transport;
  cost: number;
}

export interface Condition {
  broadcasterUserId?: string;
  rewardId?: string;
  fromBroadcasterUserId?: string;
  toBroadcasterUserId?: string;
}

export interface Transport {
  method: string;
  callback: string;
}
