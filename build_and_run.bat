echo off

echo "Build Docker Image"
docker build -t kraken_saving_plan .
echo "Run Docker Image"
docker run --env-file .env -d kraken_saving_plan