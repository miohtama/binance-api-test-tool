"""

Make a marker order on Binance Spot Testnet to move the market.

This is to trigger your own limit orders and then your client to get event for the triggered orders.
Needed for manual simulation of different event flows or integration testing.

Tutorials:

- https://dev.to/drcloudycoder/develop-python-cli-with-subcommands-using-click-4892

"""

import logging
from decimal import Decimal
from dataclasses import dataclass

import click
from binance.client import Client
from binance_testnet_tool.logs import setup_logging
from tabulate import tabulate


logger = logging.getLogger()


client: Client = None


@dataclass
class BinanceUrlConfig:
    """URLS for Binance API interaction.

    Lose your money and Spot Testnet flavours.

    Looks like python-binance does not have direct support for Spot Testnet urls.
    """

    api_end_point: str
    user_stream_endpoint: str
    wss_user_stream: str

    def __init__(self, network: str):
        if network == "spot-testnet":
            self.api_end_point = "https://testnet.binance.vision/api"
            self.user_stream_endpoint = "userDataStream"
            self.wss_user_stream = "wss://testnet.binance.vision/ws/"
        elif network == "production":
            self.api_end_point = Client.API_URL
            self.user_stream_endpoint = "userDataStream"
            self.wss_user_stream = "wss://stream.binance.{}:9443/ws/"
        else:
            raise RuntimeError(f"Unknown Binance network {network}")



def create_client(api_key, api_secret, network: str):
    """Create Binance client with proper testnet configuration."""

    # Patch the client for testnet if needed
    urls = BinanceUrlConfig(network)
    Client.API_URL = urls.api_end_point

    client = Client()

    logger.info("Binance client configured for %s, using API endpoint %s", network, client.API_URL)
    return client


@click.command()
@click.option('--market', default=None, help='Market where the order is made', required=True)
def make_market_order(client: Client, market: str, side: str, amount: Decimal):
    """Move the market."""
    pass


@click.command()
def fetch_markets():
    """List available markets in Binance"""
    client


@click.command()
def status():
    """Print exchange status

    https://python-binance.readthedocs.io/en/latest/general.html
    """
    status = client.get_system_status()
    print(f"The status of {client.API_URL} is: {status['msg']}")


@click.command()
def available_pairs():
    """Available pairs for the user to trade.

    https://python-binance.readthedocs.io/en/latest/general.html
    """
    tokens = client.get_all_tickers()
    tokens = sorted(tokens, key=lambda x: x["symbol"])

    def get_entries():
        entries = []
        for idx, token in enumerate(tokens):
            yield idx + 1, token["symbol"], token["price"]

    headers = ["#", "Symbol", "Midprice"]
    print(tabulate(get_entries(), headers, floatfmt=".8f"))


@click.group("Binance Spot Testnet command line tool")
@click.option('--api-key', default=None, help='Binance API key', required=True, envvar="BINANCE_API_KEY")
@click.option('--api-secret', default=None, help='Binance API secret', required=True, envvar="BINANCE_API_SECRET")
@click.option('--log-level', default="info", help='Python logging level', required=False)
@click.option('--network',  help='Use Binance Vision Spot testnet', type=click.Choice(['production', 'spot-testnet']), required=True, envvar="BINANCE_NETWORK")
def main(api_key, api_secret, network, log_level):
    global client
    setup_logging(log_level)
    client = create_client(api_key, api_secret, network)


main.add_command(fetch_markets)
main.add_command(status)
main.add_command(available_pairs)


if __name__ == "__main__":
    main()
