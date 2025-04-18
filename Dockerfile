# build stage
FROM node:16 as builder-client
WORKDIR /app
COPY ./tau-dashboard/package*.json ./
RUN npm install
COPY ./tau-dashboard /app
RUN npm run build

FROM rust:1.84 as builder
WORKDIR /app
COPY ./tau/. .
COPY ./tau/.sqlx .
COPY eventsub_subscriptions.json .
COPY helix_endpoints.json .
RUN cargo install --locked --path .

FROM python:3.13-slim as prod-stage

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY ./tau/migrate_constance.py /app
COPY --from=builder /usr/local/cargo/bin/tau /app/tau
COPY --from=builder-client /app/dist /app/dist
CMD ["/app/tau"]
