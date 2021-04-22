#!/bin/bash
#
# A simple continuous integration script checking the Docker image builds and runs
#

set -e

export BINANCE_NETWORK=spot-testnet
docker build -t miohtama/binance-api-test-tool:latest .

binance_status=$(docker run -e BINANCE_NETWORK miohtama/binance-api-test-tool:latest status)

if [[ $binance_status != "The status of https://testnet.binance.vision/api is: normal" ]] ; then
  echo "Got bad status: $binance_status"
  exit 1
fi

echo "Ok"
exit 0

