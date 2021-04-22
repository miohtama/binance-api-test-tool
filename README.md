This is a command line tool for Binance testnet to test your orders.

The main use case is to fill your own limit orders on Binance Spot Testnet, or otherwise trigger and simulate events you receive over Binance API.

[For more information about trade execution and bot development, contact Capitalgram](https://capitalgram.com) 

## Features

* Fetch available markets on Binance testnet

* Fill your limit orderes on Binance testnet

* Read parametes from command line or environment variables

* Colored logging output

* Based on [python-binance](https://python-binance.readthedocs.io/)

## Installation

Check out from Github.

Install using [Poetry](https://python-poetry.org/).

```shell
# Activate a new environment in the check
poetry shell

# Install dependencies
poetry install
```

## Usage

Get keys from [Binance Spot Testnet](https://testnet.binance.vision/).

Example:

```shell
export BINANCE_API_KEY=... 
xport BINANCE_API_SECRET="..."
export BINANCE_NETWORK="spot-testnet"

python binance_testnet_tool/main.py fetch-markets --
```

More usage information available with `--help` switch.

## License

MIT
