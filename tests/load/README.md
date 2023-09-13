# Pre-requisite

Install the load test framework k6, read the [installation](https://k6.io/docs/get-started/installation/) instructions. For more details on the tool, read the [get stated](https://k6.io/docs/) documentation.

On MacOS:
```sh
brew install k6
```

# Smoke test

This test is devised to verify minimum requirements on the target. Read more about the [different types of load tests](https://k6.io/docs/test-types/load-test-types/). From here we can evolve to more complex tests.

# How to run

After installing k6, you can run the test by executing:
```sh
k6 run tests/load/network_statistics_smoke_test.js
```

> [!NOTE]
> Despite the tool ingest JavaScript, it is built with Go lang.

## Network Statistics

In the case of network_statistics load test, you can pass a diferent host URL:
```sh
k6 run tests/load/network_statistics_smoke_test.js --env HOST_URL=https://e732
bbkkd3.execute-api.eu-central-1.amazonaws.com/dev
```

