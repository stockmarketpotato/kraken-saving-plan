#!/bin/bash

REGISTRY="<registry>"

echo "Build Docker Image"
docker build -t $REGISTRY/kraken_recurring_buy .
echo "Push Image"
docker push $REGISTRY/kraken_recurring_buy:latest