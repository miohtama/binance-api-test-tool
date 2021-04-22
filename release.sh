#!/bin/sh
#
# Create a Docker Hub release
#

set -e
set -u

export BINANCE_NETWORK=spot-testnet

IMAGE="miohtama/binance-api-test-tool"

VERSION=`python -c "import binance_testnet_tool ; print(binance_testnet_tool.__version__)"`

echo "Preparing a release for version $VERSION"
docker build -t miohtama/binance-api-test-tool:latest .

# Test run - smoke test will probably exit non-zero if Python dependencies failed
echo "Docker local version is now " && docker run -e BINANCE_NETWORK $IMAGE:latest version
# Push the release to hub
docker tag $IMAGE:latest $IMAGE:$VERSION

# Update the latest and the tag
docker push $IMAGE:$VERSION
docker push $IMAGE:latest