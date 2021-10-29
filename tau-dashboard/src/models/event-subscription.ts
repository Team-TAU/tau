export interface EventSubSubscription {
  condition: { [key: string]: string };
  cost: number;
  created_at: string;
  id: string;
  status: string;
  transport: {
    callback: string;
    method: string;
  };
  type: string;
  version: string;
}

export interface EventSubConditionSchema {
  $id: string;
  $schema: string;
  description: string;
  properties: { [key: string]: { type: string; description: string } };
  required: string[];
  title: string;
  type: string;
}

export interface EventSubscription {
  active: boolean;
  base_url: string;
  condition_schema: any;
  description: string;
  event_schema: any;
  id: string;
  lookup_name: string;
  name: string;
  scope_required: string;
  status: string;
  subscription: EventSubSubscription;
  subscription_type: string;
  version: string;
}
