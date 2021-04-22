#!/bin/sh
#
# Create a Docker Hub release
#

IMAGE="miohtama/binance-api-test-tool"

VERSION=`python -c "import binance_testnet_tool ; print(binance_testnet_tool.__version__)"`

docker build -t miohtama/binance-api-test-tool:latest .

# Test run - smoke test will probably exit non-zero if Python dependencies failed
echo "Docker local version is now " && docker run $IMAGE:latest version
# Push the release to hub
docker tag $IMAGE:latest $IMAGE:$(VERSION)

# Update the latest and the tag
docker push $IMAGE:$(VERSION)
docker push $IMAGE:latest