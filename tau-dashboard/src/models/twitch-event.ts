export interface TwitchEvent {
  created: string;
  event_data: any;
  event_id: string;
  event_source: string;
  event_type: string;
  id: string;
  origin: string;
}

export const eventTitleMap: { [key: string]: any } = {
  'channel-update': (obj: any) => `Channel Updated.`,
  'channel-cheer': (obj: any) =>
    `${obj.event_data.user_name} cheered ${obj.event_data.bits} bits`,
  'channel-follow': (obj: any) => `${obj.event_data.user_name} followed`,
  'channel-channel_points_custom_reward_redemption-add': (obj: any) =>
    `${obj.event_data.user_name} redeemed ${obj.event_data.reward.title}`,
  'stream-offline': (obj: any) => `${event_data.broadcaster_user_name} is offline`,
  'stream-online': (obj: any) => `${event_data.broadcaster_user_name} is online`,
  'channel-subscription-end': (obj: any) => `${event_data.user_name} stopped subscribing`,
  'channel-subscribe': (obj: any) => `${event_data.user_name} subscribed`,
  'channel-subscription-gift': (obj: any) => `${event_data.user_name} gifted ${event_data.total} subs`,
  'channel-raid': (obj: any) => `${event_data.from_broadcaster_user_name} raided with ${event_data.viewers} viewers`,
  'channel-channel_points_custom_reward_redemption-add': (obj: any) => `${event_data.user_name} redeemed ${event_data.reward.title}`,
  default: (obj: any) =>
    `${obj.event_type.replaceAll('-', ' ').replaceAll('_', ' ')}`,
};
