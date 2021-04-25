#!/bin/sh
#
# Create a Docker Hub release
#

set -e
set -u

# Needed for the smoke test of Docker image
export BINANCE_NETWORK=spot-testnet

IMAGE="miohtama/binance-api-test-tool"

VERSION=`python -c "import binance_testnet_tool ; print(binance_testnet_tool.__version__)"`
echo "Preparing a release for version $VERSION"

# https://stackoverflow.com/a/66420668/315168
read -p "Continue? (y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

# Build
docker build -t miohtama/binance-api-test-tool:latest .

# Smoke test
echo "Docker local version is now " && docker run -e BINANCE_NETWORK $IMAGE:latest version

git tag -a v$VERSION -m "Releasing new version with release.sh - $VERSION"
git push origin master && git push origin master --tags

# Push the release to hub
docker tag $IMAGE:latest $IMAGE:$VERSION

# Update the latest and the tag
docker push $IMAGE:$VERSION
docker push $IMAGE:latest

echo "Release $VERSION done"