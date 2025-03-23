import sys
import base64
import krakenex
import time
import os
from decimal import Decimal
from enum import Enum
import argparse

# Initialize Kraken API
kraken = krakenex.API()

if os.path.isfile('kraken.key'):
    kraken.load_key('kraken.key')
else:
    KRAKEN_API_KEY = os.environ['KRAKEN_API_KEY']
    KRAKEN_API_SECRET = os.environ['KRAKEN_API_SECRET']
    kraken = krakenex.API(KRAKEN_API_KEY, KRAKEN_API_SECRET)

class PriceType(Enum):
    ASK = 'a'
    BID = 'b'
    LAST = 'c'

TIMEOUT_IN_SECONDS = 60 * 5

class KrankenApiWrap(object):
    @staticmethod
    def get_price(pair : str) -> float:
        """Get the current price for a pair."""
        try:
            response = kraken.query_public('Ticker', {'pair': pair})
            if response['error']:
                raise Exception(f"{response['error']}")
            ask = Decimal(response['result'][pair][PriceType.ASK.value][0])
            bid = Decimal(response['result'][pair][PriceType.BID.value][0])
            last = Decimal(response['result'][pair][PriceType.LAST.value][0])
            return {'ask' : ask, 'bid' : bid, 'last' : last}
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    @staticmethod
    def get_balance(coin):
        """Fetch account balance for coin."""
        try:
            response = kraken.query_private('Balance')
            if response['error']:
                raise Exception(f"{response['error']}")
            return Decimal(response['result'].get(coin, 0.0))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    @staticmethod
    def place_limit_order(pair, volume, price, verbose=False):
        """Place a limit order."""
        try:
            order_details = {
                'pair': pair,
                'type': 'buy',
                'ordertype': 'limit',
                'price': price,  # Limit price in EUR
                'volume': volume
            }
            response = kraken.query_private('AddOrder', order_details)
            if response['error']:
                raise Exception(f"{response['error']}")
            if verbose:
                print(f"          Success: {response['result']}")
            return response['result']
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    @staticmethod
    def get_order_info(txid, verbose=False):
        """Retrieve information about specific orders."""
        try:
            order_info = {
                'txid': txid
            }
            response = kraken.query_private('QueryOrders', order_info)
            if response['error']:
                raise Exception(f"{response['error']}")
            if verbose:
                print(f"Order Info for {txid}: {response['result']}")
            return response['result']
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    @staticmethod
    def cancel_order(txid, verbose=False):
        """Cancel a particular open order (or set of open orders) by txid"""
        try:
            order_info = {
                'txid': txid
            }
            response = kraken.query_private('CancelOrder', order_info)
            if response['error']:
                raise Exception(f"{response['error']}")
            if verbose:
                print(f"          Cancel Order {txid}: {response['result']}")
            return response['result']
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    @staticmethod
    def get_asset_pair_details(pair):
        """Fetch details of an asset pair."""
        try:
            query = {
                'pair': pair,
            }
            response = kraken.query_public('AssetPairs', query)
            if response['error']:
                raise Exception(f"{response['error']}")
            if pair not in response['result']:
                raise Exception(f"Pair {pair} not found in asset pairs.")
            return response['result'][pair]
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    @staticmethod
    def earn_strategies(coin):
        """Stake COIN using the Kraken Staking API."""
        try:
            stake_details = {
                'asset': coin, # Kraken's identifier for Bitcoin 'XXBT'
            }
            response = kraken.query_private('Earn/Strategies', stake_details)
            if response['error']:
                raise Exception(f"{response['error']}")
            return response['result']
        except Exception as e:
            print(f"Info: {coin}")
            print(f"Error: {e}")
            sys.exit(1)

    @staticmethod
    def earn_allocate(amount, strategy_id):
        """Stake using the Kraken Staking API."""
        try:
            stake_details = {
                'amount': str(amount),  # Amount of coin to stake
                'strategy_id': strategy_id
            }
            response = kraken.query_private('Earn/Allocate', stake_details)
            if response['error']:
                raise Exception(f"{response['error']}")
            print(f"          Success: {response['result']}")
            return response['result']
        except Exception as e:
            print(f"Info: {strategy_id}")
            print(f"Error: {e}")
            sys.exit(1)


class BuyOnce:
    def __init__(self, pair, fiat_to_spend):
        pair_details = KrankenApiWrap.get_asset_pair_details(pair)

        base = pair_details['base']
        quote = pair_details['quote']
        precision = pair_details["pair_decimals"]
        wsname = pair_details["wsname"]
        
        base2 = wsname.split("/")[0]
        quote2 = wsname.split("/")[1] # fiat
        print("> Invest ")
        print(f"     {quote2} {fiat_to_spend}")
        print(f"     in {base2}")

        price = self._get_price(pair, base2, quote2)
        limit_price = self._get_limit_price(price, precision, quote2)
        volume = self._get_volume(fiat_to_spend, limit_price, base2)
        quote_balance = self._get_quote_balance(quote, quote2, fiat_to_spend)

        txid = self._place_limit_order(pair, volume, limit_price)
        time.sleep(5)
        success = self._wait_for_order_closed(TIMEOUT_IN_SECONDS, txid)
        if not success:
            self._cancel_order(txid)
            self._order_exec_status(txid)
            print(f"Warn: order {txid} has been canceled.")
            exit()

        self._order_exec_status(txid)

        strategy_id = self._get_strategy_id(base)
        self._earn_allocate(base, strategy_id)

    def _get_price(self, pair, base2, quote2):
        print(f"> Fetching current {base2} price:")
        price = KrankenApiWrap.get_price(pair)
        print(f"    Ask:  {price['ask']} {quote2}")
        print(f"    Bid:  {price['bid']} {quote2}")
        print(f"    Last: {price['last']} {quote2}")
        return price

    def _get_limit_price(self, price, precision, quote2):
        # Set the limit price to mid price
        limit_price = price['ask']
        print(f"> Set limit price to:")
        print(f"          {limit_price} {quote2}")
        return limit_price

    def _get_volume(self, fiat_to_spend, limit_price, base2):
        # Calculate the volume of BTC to buy
        volume = fiat_to_spend / limit_price
        print(f"> Calculated volume of {base2} to buy:")
        print(f"          {volume:.5f} {base2}")
        return volume

    def _get_quote_balance(self, quote, quote2, fiat_to_spend):
        # Check EUR balance
        print(f"> Available {quote2} balance:")
        quote_balance = KrankenApiWrap.get_balance(quote)
        print(f"          {quote_balance:.2f} {quote2}")
        if quote_balance < fiat_to_spend:
            print("Error: Insufficient balance to complete the purchase.")
            exit()
        return quote_balance

    def _place_limit_order(self, pair, volume, limit_price):
        # Place limit order
        print("> Place limit order...")
        result = KrankenApiWrap.place_limit_order(pair, volume, limit_price, True)
        txid = result['txid'][0]
        return txid

    def _get_strategy_id(self, base):
        strategies = KrankenApiWrap.earn_strategies(base)
        strategy_id = strategies['items'][0]['id']
        return strategy_id

    def _earn_allocate(self, base, strategy_id):
        print(f"> Earn/Allocate {base} ...")
        print(f"          Balance available for staking: ", end='')
        base_balance = KrankenApiWrap.get_balance(base)
        print(f"{base_balance} {base}")
        if base_balance > 0.0:
            KrankenApiWrap.earn_allocate(base_balance, strategy_id)
        else:
            print(f"          Balance insufficient.")

    def _wait_for_order_closed(self, timeout_seconds, txid):
        print(f"> Wait for order {txid} to be closed ...")
        timeout = time.time() + timeout_seconds
        closed_cancelled_expired = True
        while True:
            result = KrankenApiWrap.get_order_info(txid)
            if not txid in result:
                return False
            if result[txid]["status"] in ["closed", "canceled", "expired"]:
                break
            if time.time() > timeout:
                print(f"          Timeout")
                closed_cancelled_expired = False
                break
            time.sleep(5)
        return closed_cancelled_expired

    def _cancel_order(self, txid):
        print(f"> Cancel order {txid} ...")
        result = KrankenApiWrap.cancel_order(txid, True)
        if result['count'] == 1:
            print(f"          successful")
        else:
            print(f"          failed")
        return result

    def _order_exec_status(self, txid):
        result = KrankenApiWrap.get_order_info(txid)
        cost = result[txid]["cost"]
        fee = result[txid]["fee"]
        vol_exec = result[txid]["vol_exec"]
        status = result[txid]["status"]
        if not txid in result:
            return
        print(f"> Status of Order {txid} ...")
        print(f"          Status:     {status}") 
        print(f"          Vol. exec.: {vol_exec}", end='')
        print(" (partially executed)") if result[txid]["misc"] == "partial" else print("")
        print(f"          Cost:       {cost}")
        print(f"          Fee:        {fee}")
        print(f"          Total:      {float(fee) + float(cost)}")

# python recurring_buy.py --pair XXBTZEUR --fiat_to_spend 70
# python recurring_buy.py --pair XETHZEUR --fiat_to_spend 30

def main():
    parser = argparse.ArgumentParser(description="Buy and stake a coin on Kraken.")
    parser.add_argument("--pair", type=str, required=True, help="Trading pair, e.g., XXBTZEUR for BTC/EUR or XETHZEUR for ETH/EUR")
    parser.add_argument("--fiat_to_spend", type=Decimal, required=True, help="Amount in fiat money to spend on coin")
    args = parser.parse_args()

    pair = args.pair
    fiat_to_spend = args.fiat_to_spend

    BuyOnce(pair, fiat_to_spend)

if __name__ == '__main__':
    main()