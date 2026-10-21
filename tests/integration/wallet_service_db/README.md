# Wallet-service DB checks

`test_address_queries.py` runs the explorer's address queries against a real
wallet-service schema: results, ordering, paging, counts, 404s, and that each
query reads only the address's own rows. The unit tests mock the engine and
can't catch a bad query.

They are skipped unless `WALLET_SERVICE_TEST_DB_URL` is set, so `make test` and
CI don't run them.

## Running

1. Get a MySQL 8 database. Each run deletes and rewrites the tables it seeds,
   so use a scratch database.
2. Apply the wallet-service migrations from a `hathor-wallet-service` checkout
   that has the public address tables:

   ```sh
   cd <hathor-wallet-service>
   DB_ENDPOINT=127.0.0.1 DB_PORT=3306 DB_USER=<user> DB_PASS=<password> \
   DB_NAME=<database> NODE_ENV=development npx sequelize db:migrate
   ```

3. Run the tests:

   ```sh
   WALLET_SERVICE_TEST_DB_URL=mysql+pymysql://<user>:<password>@127.0.0.1:3306/<database> \
   ENVIRONMENT=test poetry run pytest -p no:warnings tests/integration
   ```

`explain.py` prints `EXPLAIN ANALYZE` for every address query on the same data:

```sh
WALLET_SERVICE_TEST_DB_URL=... ENVIRONMENT=test \
poetry run python -m tests.integration.wallet_service_db.explain
```
