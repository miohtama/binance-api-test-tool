"""

Make a marker order on Binance Spot Testnet to move the market.

This is to trigger your own limit orders and then your client to get event for the triggered orders.
Needed for manual simulation of different event flows or integration testing.

Tutorials:

- https://dev.to/drcloudycoder/develop-python-cli-with-subcommands-using-click-4892

"""

from decimal import Decimal
from dataclasses import dataclass

import click
from binance.client import Client

from binance_testnet_tool.logs import setup_logging


client = None


@dataclass
class BinanceUrlConfig:
    """URLS for Binance API interaction.

    Lose your money and Spot Testnet flavours.

    Looks like python-binance does not have direct support for Spot Testnet urls.
    """
    api_end_point = "https://api.binance.{}/api/v1/"
    user_stream_endpoint = "userDataStream"
    wss_user_stream = "wss://stream.binance.{}:9443/ws/"

    def __init__(self, network: str):
        if network == "spot-testnet":
            self.api_endpoint = "https://testnet.binance.vision/api/v1/"
            self.user_stream_endpoint = "userDataStream"
            self.wss_user_stream = "wss://testnet.binance.vision/ws/"


def create_client(api_key, api_secret, testnet: bool):
    """Create Binance client with proper testnet configuration."""
    client = Client()

    urls = BinanceUrlConfig(testnet)

    # Patch the client
    client.API_URL = urls.api_endpoint
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
def ping():
    """Ping API"""
    client.ping()


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
main.add_command(ping)


if __name__ == "__main__":
    main()
