This is a command line tool for Binance to test your Binance API application code, orders and events. It works with Binance main API as well as [Binance Spot Testnet](https://testnet.binance.vision/).

The main use case is to fill your own limit orders on Binance Spot Testnet, or otherwise trigger and simulate events you receive over Binance API.

[For more information about trade execution and bot development, contact Capitalgram](https://capitalgram.com)

## About Binance Spot Testnet

Binance Spot Testnet order books contain pretty much random data. To do meaningful tests, you need to play both sides of the market yourself: creating limit orders and creating market orders. You can use the same API key to trade against yourself.

- There is no frontend available for Binance Spot Testnet. All interaction must happen over the API.

- Looks like all API endpoints under withdraw section do not seem to work: e.g. you cannot query your balances

## Prerequisites

You need to understand Python and UNIX command line basics.

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

Give the given Binance API endpoint and keys as environment variales:

```shell
export BINANCE_API_KEY=... 
export BINANCE_API_SECRET=...
export BINANCE_NETWORK="spot-testnet"
```

## Defaults

Some command requires you to specify order book. Because this is a testnet tool, unless you specify anything, we default to BTCUSDT order book, buy order and amount of 0.1 BTC. This is for the tool to be more wrist friendly.


## Command examples

### Help

```shell
python binance_testnet_tool/main.py --help
```

```

```

### Available trading pairs

List available trading pairs. As the trading of this, Binance has 1400 trading pairs, whileas Spot Testnet has only 20 pairs.

```shell
python binance_testnet_tool/main.py available-pairs
```

```
   #  Symbol                   Midprice
----  -------------  ------------------
   1  1INCHBTC               0.00009253
   2  1INCHBUSD              4.94450000
   3  1INCHDOWNUSDT          8.38000000
   4  1INCHUPUSDT            5.60000000
   5  1INCHUSDT              4.93450000
   6  AAVEBKRW          164167.00000000
   7  AAVEBNB                0.68990000
   8  AAVEBTC                0.00703600
   ...
1409  ZRXBUSD                1.58700000
1410  ZRXETH                 0.00064937
1411  ZRXUSDT                1.58220000
```

### Further usage help

More usage information available with `--help` switch.

## Contributions

I am not reading my Github status updates due to high volume updates I am receiving. Contact me on [Ethereum Python Discord](https://discord.gg/s8ZujXHaKN) to discuss about contributions.  

## Further reading

* [Binance API changelog](https://binance-docs.github.io/apidocs/spot/en/#change-log)

* [Binance API changelog](https://binance-docs.github.io/apidocs/spot/en/#change-log)

## License

MIT

The work was sponsored by [Digital Asset Management Ltd.](https://www.dam.gi/). The authors are not affiliated with Binance.


