echo off

echo "Build Docker Image"
docker build -t kraken_recurring_buy .
echo "Run Docker Image"
docker run -d kraken_recurring_buy