# Breaking Changes for recent TAU version

A recent release of TAU created some breaking changes from the original version of TAU. The new version of TAU now allows you to chose the specific `EventSub` subscriptions you want to subscribe to, and moves all of the View Subscription events (Subscribe, Gift Sub, etc..) from PubSub to EventSub. In order to accomodate these new features, the event naming convention was changed, which may break any existing integrations you have set up with older versions of TAU. Specifically, the following event names were changed:

- old: `update`, new: `channel-update`
- old: `follow`, new: `channel-follow`
- old: `point-redemption`, new: `channel-channel_points_custom_reward_redemption-add`
- old: `cheer`, new: `channel-cheer`
- old: `subscribe`, new: `channel-subscribe`
- old: `raid`, new: `channel-raid`
- old: `hype-train-progress`, new: `channel-hype_train-progress`
- old: `hype-train-begin`, new: `channel-hype_train-begin`
- old: `hype-train-end`, new: `channel-hype_train-end`

Additionally, on your first run of the new TAU version, you will need to select the `EventSub` events you want to subscribe to. Once you load the dashboard, "Config" in the side menu, toggle on all of the Twitch EventSub Subscriptions you require, then click the "Update Subscriptions" button at the bottom of the subscription list, and approve the new required scopes.
