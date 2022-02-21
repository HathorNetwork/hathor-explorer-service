# hathor-explorer-service

## Running locally

First, rename `.env.example` file to `.env`. You can do that by running `cp .env.example .env`

Then, run `docker-compose up -d` to enable explorer-service, Redis, and daemons locally.

Explorer service will be exposed on port 3001.

## Deploying

Deploys are automated using Github Actions and Flux.

To deploy to the `testnet` environment, simply commit to the `main` branch.

To deploy to the `mainnet` environment, create a release in Github using a tag in the format `v0.0.0`

Currently we do not have an automated mechanism to be warned if some automated deployment fails. So, after triggering the deploy, you should check if a commit was made by `fluxcdbot` in https://github.com/HathorNetwork/ops-tools/commits/master, updating the project's manifests with the new Docker image tag.
