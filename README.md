# hathor-explorer-service

## Running locally

First, rename `.env.example` file to `.env`. You can do that by running `cp .env.example .env`

Then, run `docker-compose up -d` to enable explorer-service, Redis, and daemons locally.

Explorer service will be exposed on port 3001.

## Adding a new API

If you add a new API, be careful to add ```request.header.origin``` as cacheKey, if applicable. Otherwise, you may see CORS error when accessing the same resource from different domains.

## Deploying

Deploys are automated using Github Actions and Flux in combination. A deployment is made for 3 environments: `dev`, `testnet` and `mainnet`; and 2 systems: lambdas and deamon.

Watch logs and alerts related to the deployment of the services in [SOP Logs](https://github.com/HathorNetwork/ops-tools/blob/master/docs/sops/hathor-explorer-service.md#logs).

### Systems

There are 2 systems.

#### Lambdas

It happens by the make script method `deploy-lambdas-ci`, which build and deploy the source code to lambda services in the AWS.

#### Deamon

It happens by the make script method `deploy-deamons`, which build a docker image and push it to ECR, in the `hathor-explorer-service` repository. Once an image is pushed to ECR, the [fluxcdbot] identifies the lastest version tag and commit it in the ops-tools, in the hathor-explorer-service's kubernetes manifest. When the new definition is commited, a scheme sync happens in the kubernetes and new pods for the new version are lifted up.

>[!TIP]
>After a deploy job finish with success in the GitHub action, look at the [Ops-Tools repository commits](https://github.com/HathorNetwork/ops-tools/commits/master) and check if the new hathor-explorer-service image for the new version is commited.

### Environments

There are 3 environments.

#### Dev

Every push to `dev` branch triggers the deployment for both systems in the `dev` environment.

#### Testnet

Every push to `main` branch triggers the deployment for both systems in the `testnet` environment.

#### Mainnet

Every push of a tag in the format `v0.0.0` triggers the deployment for both systems in the `mainnet` environment.

### Troubleshooting

Look for issues and possible solutions in the [On-Call Incidents repository](https://github.com/HathorNetwork/on-call-incidents/issues?q=is:issue+explorer-service), [Internal Issues](https://github.com/HathorNetwork/internal-issues/issues?q=is:issue+is:open+explorer-service), or in the repository itself.
