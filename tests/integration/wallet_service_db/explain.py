"""Print `EXPLAIN ANALYZE` for every address query on the seeded dataset.

Usage: WALLET_SERVICE_TEST_DB_URL=... python -m tests.integration.wallet_service_db.explain
"""
import os

from sqlalchemy.engine import create_engine

from tests.integration.wallet_service_db.dataset import Dataset
from tests.integration.wallet_service_db.test_address_queries import (
    explain_analyze,
    plan_cases,
)


def main() -> None:
    dataset = Dataset()
    engine = create_engine(os.environ["WALLET_SERVICE_TEST_DB_URL"])
    with engine.begin() as connection:
        dataset.seed(connection)
    with engine.connect() as connection:
        for name, query, params, _ in plan_cases(dataset):
            print(f"### {name}\n")
            print(explain_analyze(connection, query, params))
            print()


if __name__ == "__main__":
    main()
