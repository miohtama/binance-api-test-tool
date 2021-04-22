![badge](https://github.com/miohtama/binance-api-test-tool/workflows/CI/badge.svg)

`binance-api-test-tool` is a tool to test your Binance API application, orders and events from command line and Python console. It works with [Binance Spot Testnet](https://testnet.binance.vision/). The main use case is to make and fill your own orders, or otherwise trigger and simulate events you receive over Binance API.

* [Github](https://github.com/miohtama/binance-api-test-tool)

* [Docker GHub](https://hub.docker.com/repository/docker/miohtama/binance-api-test-tool)

![An example IPython session](./demo.gif)

*An example session how to make 0.001 BTC market buy order on Binance Spot Testnet using Python APIs.*

For more information about [Binance trade execution and bot development, contact authors at Capitalgram](https://capitalgram.com).

## About Binance Spot Testnet

[Binance Spot Testnet](https://testnet.binance.vision/) is a Binance matching engine with test money and some order books. You can get an API key with a Github account. 

Some important notes about Binance Spot Testnet

- Spot Testnet is good for integration testing for your application code.

- Spot Testnet is shared with other users and is noisy.

- Order books are in funny states because other users testing and have ridiculous prices, so e.g. arbitrage bot testing is difficult.

- There is no frontend available for Binance Spot Testnet. All interaction must happen over the API.

- Looks like all API endpoints under withdraw section do not seem to work: e.g. a your balances query fails because you cannot set the required Withdraw permissions for your API key on Binance Spot Testnet.

## Prerequisites

This software works on Windows, macOS and Linux.

* You need to understand command line basics.

* You need to be able to use [Docker](https://www.docker.com/).

* You need to have a Binance API key

## Installation

The application is distributed as Docker image and automatically downloaded when you run it for the first time.
You need to have Docker properly configured on your computer.

First create an alias to run the application:

```shell
alias binance-api-test-tool='docker run -it -v `pwd`:`pwd` -w `pwd` -e BINANCE_API_KEY -e BINANCE_API_SECRET -e BINANCE_NETWORK miohtama/binance-api-test-tool:latest'
```

Then you can run the tool:

```shell
binance-ai-test-tool --help
```

You will get overview of commands:

```
Usage: docker-entrypoint.py [OPTIONS] COMMAND [ARGS]...

Options:
  --api-key TEXT                  Binance API key  [required]
  --api-secret TEXT               Binance API secret  [required]
  --log-level TEXT                Python logging level  [default: info]
  --network [production|spot-testnet]
                                  Binance API endpoint to use  [required]
  --help                          Show this message and exit.

Commands:
  available-pairs      Available pairs for the user to trade
  balances             Account balances
  cancel-all           Cancel all open orders
  create-limit-order   Add liquidity to the market.
  create-market-order  Move the market.
  current-price        Current price info for a trading pair
  order-event-stream   Open order event stream
  orders               Open orders
  status               Print exchange status
  symbol-info          Information on a single trading pair
```

## Features

* An easy to use command line client based on [Python click](https://click.palletsprojects.com/)

* Make orders, get your balances, etc. APIs needed to trade

* Interactive Python console to explore Binance APIs using [IPython](https://github.com/ipython/ipython)

* HTTP request/response logging from Binance API 

* Websockets event streams 

* Highly readabble colored console output

* Uses on [python-binance](https://python-binance.readthedocs.io/) API wrapper

* Configure with command line parameters or environment variables

## Usage

### Setting up API keys

Get keys from [Binance Spot Testnet](https://testnet.binance.vision/).

Give the given Binance API endpoint and keys as environment variales before running `binance-api-test-tool`:

```shell
export BINANCE_API_KEY=... 
export BINANCE_API_SECRET=...
export BINANCE_NETWORK="spot-testnet"
```

Alternatively you can use [.env config file](https://pypi.org/project/python-dotenv/).

A sample `.env`:

```ini
BINANCE_API_KEY=... 
BINANCE_API_SECRET=...
BINANCE_NETWORK="spot-testnet"
```

Then you can load keys from this file:

```shell
binance-api-test-tool --config-file=.env 
```

### Test flow

The usual test flow is 

1. `balances` - get your testnet balances

1. `current-price` - check what is the current order book status

1. `order-event-stream` - listen to the order change event in stream (run this in another terminal)

1. `create-limit-order` - create a new limit order based on the price data

1. `orders` - show your active orders (you should have one limit order now)

1. `create-market-order` - fill your previously created limit order

Now you should see your limit order filled in the event stream.

## Defaults

Some command requires you to specify order book. Because this is a testnet tool, unless you specify anything, we default to BTCUSDT order book, buy order and amount of 0.1 BTC. This is for the tool to be more wrist friendly.

## Command examples

### Interactive console

Start console with

```shell
binance-testnet-tool console
```

Now you can use [client](https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.Client) object directly from the Python prompt.

```jupyterpython
>> %cpaste
```

Then paste in simple market order execution:

```python
# Buy 0.001 Bitcoin on Binance Spot Testnet
order = client.create_order(
    symbol="BTCUSDT",
    side=binance_enums.SIDE_BUY,
    type=binance_enums.ORDER_TYPE_MARKET,
    quantity="0.001")
```
Press CTRL+D for IPython to execute the pasted code.

Then you can check the order results:

```jupyterpython
>> print_colorful_json(order)
```

### Available trading pairs

List available trading pairs. As the trading of this, Binance has 1400 trading pairs, whileas Spot Testnet has only 20 pairs.

```shell
binance-testnet-tool available-pairs
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

### Dumping HTTP request/responses

Use `--log-level` flag.

Example:

```shell
binance-testnet-tool --log-level=debug create-limit-order --side=buy --price-amount=8000
```

### Further usage help

More usage information available with `--help` switch.

## Development

Python 3.8+.

Check out from Github.

Install using [Poetry](https://python-poetry.org/).

```shell
# Activate a new environment in the check
poetry shell

# Install dependencies
poetry install
```

You can run the application locally:

```shell
poetry run binance-testnet-tool
```

### Building and releasing Docker image

Build Docker:

```shell
docker build -t miohtama/binance-api-test-tool:latest .
```

Test it:

```shell
docker run miohtama/binance-api-test-tool:latest 
```

Pop open a shell in Docker:

```shell
docker run -it --entrypoint /bin/sh miohtama/binance-api-test-tool:latest  
```

Publish on DockerHub:

```shell
docker login
./release.sh
```

## Contributions

I am not reading my Github status updates due to high volume updates I am receiving. Contact me on [Ethereum Python Discord](https://discord.gg/s8ZujXHaKN) to discuss about contributions.  

## Further reading

* [Binance API changelog](https://binance-docs.github.io/apidocs/spot/en/#change-log)

* [python-binance documentation](https://python-binance.readthedocs.io/)

## License

MIT

## Sponsors

The work was sponsored by [Digital Asset Management Ltd.](https://www.dam.gi/). The authors are not affiliated with Binance.


