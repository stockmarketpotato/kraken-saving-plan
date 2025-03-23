# kraken-saving-plan

A simple containerized tool to execute a saving plan on Kraken's API

The script `recurring_buy.py` places a purchase order for the specified amount of fiat money at the current ask price.
Afterwards, the full amount of purchased crypto currency is allocated for earning.

No allocation is performed, if the order is partially filled or cancelled after a timeout.

```console
usage: recurring_buy.py [-h] --pair PAIR --fiat_to_spend FIAT_TO_SPEND

Buy and stake a coin on Kraken.

options:
  -h, --help            show this help message and exit
  --pair PAIR           Trading pair, e.g., XXBTZEUR for BTC/EUR or XETHZEUR for ETH/EUR
  --fiat_to_spend FIAT_TO_SPEND
                        Amount in fiat money to spend on coin
```

Place keys in `kraken.key` to run the script directly from the local command line.

# Run Container on Local Machine

1. [Create an API key for spot trading](https://pro.kraken.com/app/settings/api) in your Kranken Account
2. Add public and private keys to `Dockerfile`
3. Configure the investment scheme in `mycron`
4. (Optional) Configure timeout (`TIMEOUT_IN_SECONDS`) in `recurring_buy.py`
6. Build and Run Docker container: `build_and_run.sh` / `build_and_run.bat`

# Deploy Container to Registry

1. [Create an API key for spot trading](https://pro.kraken.com/app/settings/api) in your Kranken Account
2. Add public and private keys to `Dockerfile`
3. Configure the investment scheme in `mycron`
4. (Optional) Configure timeout (`TIMEOUT_IN_SECONDS`) in `recurring_buy.py`
5. Configure Docker Registry in `deploy.sh` / `deploy.bat`
6. Deploy Docker container: `deploy.sh` / `deploy.bat`
7. Run the container:
```console
foo@bar:~$ docker run -d $REGISTRY/kraken_recurring_buy
```

Make sure your account has sufficient balance to execute the order.