# 🐙 Kraken Savings Plan Automation

**Automated Dollar-Cost Averaging (DCA) with Auto-Staking for Kraken.**

## 📖 Overview

This project provides a simple, containerized tool to execute a saving plan on the [Kraken](https://www.kraken.com/) cryptocurrency exchange via their API.

Blog post: [Low-Cost Automated Dollar-Cost Averaging on Kraken](https://www.stockmarketpotato.com/?p=29)

**Why use this instead of Kraken's "Recurring Buy"?**
Kraken's native recurring buy feature is convenient, but it often comes with higher fees and spread. This tool places **Limit Orders** directly via the API, significantly reducing costs over time.

**Key Features:**

  * **📉 Low Fees:** Uses Limit Orders at the current ask price to minimize fees.
  * **💸 Auto-Staking:** Automatically allocates the purchased amount to Kraken's "Earn" strategies immediately after filling the order.
  * **🐳 Dockerized:** Based on a tiny Alpine Python image, ready to run on a Raspberry Pi or VPS 24/7.

## ⚙️ Prerequisites

  * **Docker** installed on your machine.
  * A **Kraken Account**.
  * **API Keys** generated in [Kraken](https://pro.kraken.com/app/settings/api) with permissions.

## 🚀 Installation & Setup

### 1\. Clone the Repository

```bash
git clone https://github.com/yourusername/kraken-savings-plan.git
cd kraken-savings-plan
```

### 2\. Configure API Keys

Create a file named `.env` in the root directory. **Do not commit this file to version control.**

```ini
KRAKEN_API_KEY=your_api_key_here
KRAKEN_API_SECRET=your_api_secret_here
```

### 3\. Configure the Schedule (`mycron`)

Edit the `mycron` file to set your investment schedule. The syntax follows standard Cron format.

*Example: Buy €100 worth of Bitcoin on the 1st of every month at 20:00.*

```bash
0 20 1 * * python3 /app/buy_once.py --pair XXBTZEUR --fiat_to_spend 100 >>/tmp/out.log 2>/tmp/err.log
```

  * `--pair`: The trading pair (e.g., `XXBTZEUR` for BTC/EUR, `XETHZEUR` for ETH/EUR).
  * `--fiat_to_spend`: The amount of fiat currency to spend.

### 4\. (Optional) Adjust Timeout

If the market is highly volatile, the limit order might not fill immediately. You can adjust the `TIMEOUT_IN_SECONDS` variable inside `buy_once.py` to wait longer before cancelling the order.

## 🏃 Usage

### Local Build & Run

You can use the included helper script to build and run the container locally.

```bash
chmod +x build_and_run.sh
./build_and_run.sh
```

Or manually:

```bash
docker build -t kraken_saving_plan .
docker run --env-file .env -d kraken_saving_plan
```

### Verify it's running

Check the logs to ensure the cron service started successfully:

```bash
docker ps
docker logs -f <container_id>
```

## 🛠️ How it Works (`buy_once.py`)

The script executes a specific logic flow to ensure safety and efficiency:

1.  **Analyze Pair:** Determines precision and asset names.
2.  **Calculate Volume:** Checks current ask price and calculates how much crypto to buy based on your fiat limit.
3.  **Place Limit Order:** Submits the order to Kraken.
4.  **Wait & Verify:** Waits for `TIMEOUT_IN_SECONDS`.
      * *If filled:* Proceeds to staking.
      * *If timed out:* Cancels the order and exits (no money spent).
5.  **Allocate to Earn:** If the buy was successful, it retrieves the strategy ID for the asset and stakes 100% of the purchased amount.

## ⚠️ Disclaimer

**I am not a financial advisor.** This software is for educational purposes only. Trading cryptocurrencies involves risk. Using automated trading tools and API keys always carries a risk of software failure or security breaches.

**Use this tool at your own risk.** Ensure your API keys are kept secure and are never shared.