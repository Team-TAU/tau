ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS id;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS subscription_type;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS description;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS scope_required;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS status;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS base_url;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS subscription;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS event_schema;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS condition_schema;
ALTER TABLE public.twitch_twitcheventsubsubscription
DROP COLUMN IF EXISTS lookup_name;
