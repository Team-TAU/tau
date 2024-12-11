
-- recreate the old django state if we don't already have it

CREATE TABLE IF NOT EXISTS public.chatbots_chatbot (
    id uuid NOT NULL,
    user_name character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    access_token character varying(255),
    refresh_token character varying(255),
    token_expiration timestamp with time zone,
    connected boolean NOT NULL,
    created timestamp with time zone NOT NULL,
    updated timestamp with time zone NOT NULL,
    user_login character varying(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.chatbots_chatbotchannel (
    id uuid NOT NULL,
    channel character varying(255) NOT NULL,
    chat_bot_id uuid NOT NULL
);

CREATE TABLE IF NOT EXISTS public.streamers_stream (
    id uuid NOT NULL,
    stream_id character varying(64) NOT NULL,
    game_id character varying(64) NOT NULL,
    game_name character varying(64) NOT NULL,
    type character varying(32) NOT NULL,
    title character varying(255) NOT NULL,
    viewer_count integer NOT NULL,
    started_at timestamp with time zone NOT NULL,
    language character varying(16) NOT NULL,
    thumbnail_url character varying(255) NOT NULL,
    tag_ids character varying(255),
    is_mature boolean NOT NULL,
    streamer_id uuid NOT NULL,
    ended_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS public.streamers_streamer (
    created timestamp with time zone NOT NULL,
    id uuid NOT NULL,
    twitch_username character varying(64) NOT NULL,
    twitch_id character varying(64),
    streaming boolean NOT NULL,
    disabled boolean NOT NULL,
    updated timestamp with time zone NOT NULL,
    online_subscription jsonb,
    offline_subscription jsonb
);

CREATE TABLE IF NOT EXISTS public.twitch_twitcheventsubsubscription (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    subscription_type character varying(255) NOT NULL,
    description text,
    active boolean NOT NULL,
    version character varying(16) NOT NULL,
    scope_required character varying(255),
    status character varying(3),
    base_url character varying(255),
    subscription jsonb,
    event_schema jsonb NOT NULL,
    condition_schema jsonb NOT NULL,
    lookup_name character varying(255)
);

CREATE TABLE IF NOT EXISTS public.twitchevents_twitchevent (
    id uuid NOT NULL,
    event_id character varying(255),
    event_type character varying(255) NOT NULL,
    event_source character varying(32) NOT NULL,
    event_data jsonb NOT NULL,
    created timestamp with time zone NOT NULL
);

ALTER TABLE ONLY public.chatbots_chatbotchannel
    DROP CONSTRAINT IF EXISTS chatbots_chatbotchan_chat_bot_id_5d7e8552_fk_chatbots_;

ALTER TABLE ONLY public.streamers_stream
    DROP CONSTRAINT IF EXISTS streamers_stream_streamer_id_b61307a5_fk_streamers_streamer_id;

ALTER TABLE ONLY public.chatbots_chatbot
    DROP CONSTRAINT IF EXISTS chatbots_chatbot_pkey,
    ADD CONSTRAINT chatbots_chatbot_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.chatbots_chatbot
    DROP CONSTRAINT IF EXISTS chatbots_chatbot_user_id_672223b5_uniq,
    ADD CONSTRAINT chatbots_chatbot_user_id_672223b5_uniq UNIQUE (user_id);

ALTER TABLE ONLY public.chatbots_chatbotchannel
    DROP CONSTRAINT IF EXISTS chatbots_chatbotchannel_pkey,
    ADD CONSTRAINT chatbots_chatbotchannel_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.streamers_stream
    DROP CONSTRAINT IF EXISTS streamers_stream_pkey,
    ADD CONSTRAINT streamers_stream_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.streamers_streamer
    DROP CONSTRAINT IF EXISTS streamers_streamer_pkey,
    ADD CONSTRAINT streamers_streamer_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.streamers_streamer
    DROP CONSTRAINT IF EXISTS streamers_streamer_twitch_id_f9ea9edd_uniq,
    ADD CONSTRAINT streamers_streamer_twitch_id_f9ea9edd_uniq UNIQUE (twitch_id);

ALTER TABLE ONLY public.streamers_streamer
    DROP CONSTRAINT IF EXISTS streamers_streamer_twitch_username_d2e1cf4f_uniq,
    ADD CONSTRAINT streamers_streamer_twitch_username_d2e1cf4f_uniq UNIQUE (twitch_username);

ALTER TABLE ONLY public.twitch_twitcheventsubsubscription
    DROP CONSTRAINT IF EXISTS twitch_twitcheventsubsubscription_lookup_name_951ea1e4_uniq,
    ADD CONSTRAINT twitch_twitcheventsubsubscription_lookup_name_951ea1e4_uniq UNIQUE (lookup_name);

ALTER TABLE ONLY public.twitch_twitcheventsubsubscription
    DROP CONSTRAINT IF EXISTS twitch_twitcheventsubsubscription_name_28add889_uniq,
    ADD CONSTRAINT twitch_twitcheventsubsubscription_name_28add889_uniq UNIQUE (name);

ALTER TABLE ONLY public.twitch_twitcheventsubsubscription
    DROP CONSTRAINT IF EXISTS twitch_twitcheventsubsubscription_pkey,
    ADD CONSTRAINT twitch_twitcheventsubsubscription_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.twitchevents_twitchevent
    DROP CONSTRAINT IF EXISTS twitchevents_twitchevent_pkey,
    ADD CONSTRAINT twitchevents_twitchevent_pkey PRIMARY KEY (id);

CREATE INDEX IF NOT EXISTS chatbots_chatbot_user_id_672223b5_like ON public.chatbots_chatbot USING btree (user_id varchar_pattern_ops);

CREATE INDEX IF NOT EXISTS chatbots_chatbotchannel_chat_bot_id_5d7e8552 ON public.chatbots_chatbotchannel USING btree (chat_bot_id);

CREATE INDEX IF NOT EXISTS streamers_stream_streamer_id_b61307a5 ON public.streamers_stream USING btree (streamer_id);

CREATE INDEX IF NOT EXISTS streamers_streamer_twitch_id_f9ea9edd_like ON public.streamers_streamer USING btree (twitch_id varchar_pattern_ops);

CREATE INDEX IF NOT EXISTS streamers_streamer_twitch_username_d2e1cf4f_like ON public.streamers_streamer USING btree (twitch_username varchar_pattern_ops);

CREATE INDEX IF NOT EXISTS twitch_twitcheventsubsubscription_lookup_name_951ea1e4_like ON public.twitch_twitcheventsubsubscription USING btree (lookup_name varchar_pattern_ops);

CREATE INDEX IF NOT EXISTS twitch_twitcheventsubsubscription_name_28add889_like ON public.twitch_twitcheventsubsubscription USING btree (name varchar_pattern_ops);

ALTER TABLE ONLY public.chatbots_chatbotchannel
    ADD CONSTRAINT chatbots_chatbotchan_chat_bot_id_5d7e8552_fk_chatbots_ FOREIGN KEY (chat_bot_id) REFERENCES public.chatbots_chatbot(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.streamers_stream
    ADD CONSTRAINT streamers_stream_streamer_id_b61307a5_fk_streamers_streamer_id FOREIGN KEY (streamer_id) REFERENCES public.streamers_streamer(id) DEFERRABLE INITIALLY DEFERRED;
