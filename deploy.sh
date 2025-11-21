#!/bin/bash

REGISTRY="<registry>"

echo "Build Docker Image"
docker build -t $REGISTRY/kraken_saving_plan .
echo "Push Image"
docker push $REGISTRY/kraken_saving_plan:latest