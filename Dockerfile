# build stage
FROM node:23 as builder-client
WORKDIR /app
COPY ./tau-dashboard/package*.json ./
RUN npm install
COPY ./tau-dashboard /app
RUN npm run build

FROM rust:1.84 as builder
WORKDIR /app
COPY ./tau/. .
COPY ./tau/.sqlx .
COPY eventsub_subscriptions.json ..
COPY helix_endpoints.json ..
RUN cargo install --locked --path .

FROM python:3.13-slim as prod-stage

RUN apt-get update && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN touch .env

COPY ./tau/migrate_constance.py .
COPY --from=builder /usr/local/cargo/bin/tau .
COPY --from=builder-client /app/dist .
CMD ["/app/tau"]
