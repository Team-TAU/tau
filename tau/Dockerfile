FROM rust:1.84 as builder
WORKDIR /app
COPY . .
RUN cargo install --locked --path .

FROM python:3.13-slim as prod-stage

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY migrate_constance.py /app
COPY --from=builder /usr/local/cargo/bin/tau /app/tau
CMD ["/app/tau"]
