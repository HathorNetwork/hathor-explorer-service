# hathor-explorer-service

## Running locally

First, rename `.env.example` file to `.env`. You can do that by running `cp .env.example .env`

Then, run `docker-compose up -d` to enable explorer-service, Redis, and daemons locally.

Explorer service will be exposed on port 3001.

## Adding a new API

If you add a new API, be careful to add ```request.header.origin``` as cacheKey, if applicable. Otherwise, you may see CORS error when accessing the same resource from different domains.

## Deploying

See in the [SOP](https://github.com/HathorNetwork/ops-tools/blob/master/docs/sops/hathor-explorer-service.md#deployment).
