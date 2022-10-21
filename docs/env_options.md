# Environment Variables

The following environment variables can be used to manipulate your Tau install.

| Key                   | Description                                                                      | Default Value |
|-----------------------|----------------------------------------------------------------------------------|---------------|
| PUBLIC_URL            | Hostname used to communicate with TAU                                            | localhost     |
| PROTOCOL              | Protocol being used, either "http:" or "https:"                                  | http:         |
| PORT                  | Port for the application to listen on                                            | 8000          |
| BEHIND_PROXY          | Whether or not the application is running behind a reverse proxy (like NGINX)    | False         |
| USE_NGROK             | Whether or not to use NGROK to allow running TAU locally without port forwarding | False         |
| NGROK_TOKEN           | Token used for authenticating with NGROK                                         | ''            |
| REDIS_ENDPOINT        | Address and Port to connect to Redis at                                          | redis:6379    |
| REDIS_PW              | Password used to authenticate with Redis                                         | ''            |
| DJANGO_DB_TYPE        | Database types django uses, options are `postgres` and `sqlite`                  | postgres      |
| DJANGO_DB             | Name of the database                                                             | tau_db        |
| DJANGO_DB_URL         | Hostname of the database                                                         | db            |
| DJANGO_DB_USER        | Username to connect to the database with                                         | tau_db        |
| DJANGO_DB_PW          | Password for the `DJANGO_DB_USER`                                                | ''            |
| DJANGO_CONFIGURATION  | Configuration django uses                                                        | Local         |
| DJANGO_SECRET_KEY     | Key used by Django for keeping your data stored securely                         | None          |
| TWITCH_CLIENT_ID         | Application ID for connecting to twitch                                          | ''            |
| TWITCH_CLIENT_SECRET  | Used for communicating with the twitch API                                       | ''            |
| TWITCH_WEBHOOK_SECRET | Used for signing the webhooks from twitch to validate they are legitimate        | ''            |
