import requests, json, logging
from decimal import Decimal, getcontext


def convert_xmr_usd(amount):
    """
    Convert a given XMR amount to its USD equivalent.
    :param amount:
    :return:
    """
    api = "https://min-api.cryptocompare.com/data/price?fsym=XMR&tsyms=USD"
    usd = 0
    try:
        resp = requests.get(url=api, timeout=10).json()
        exchange_rate = resp["USD"]
        getcontext().prec = 28
        usd = Decimal(amount) * Decimal(exchange_rate)
        usd = round(usd, 2)
    except Exception as e:
        print(e)
    return usd


def wallet_balance(account_index):
    """
    Retrieve an account's balance using the account's index.
    :param account_index: Index of the account.
    :return: Balance of the account.
    """
    balance = 0.0
    url = "http://127.0.0.1:18083/json_rpc"
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "get_balance",
        "params": {
            "account_index": account_index
        }
    }
    try:
        resp = requests.post(url=url, headers=headers, data=json.dumps(data), timeout=10).json()
        balance = resp["result"]["balance"] / 1e12
    except Exception as e:
        print(e)
    return convert_xmr_usd(balance)


def gen_wallet(account_name):
    """
    Generate a new account with the given name and return the address along with its account_index.
    :param account_name: Name of the new account.
    :return: Dictionary with account index and primary address of the new account.
    """
    account_info = {}
    url = "http://127.0.0.1:18083/json_rpc"
    data = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": "create_account",
        "params": {
            "label": account_name
        }
    }
    headers = {'Content-Type': 'application/json'}
    try:
        resp = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=10).json()
        account_info = {
            "address_index": resp["result"]["account_index"],
            "wallet_address": resp["result"]["address"]
        }
    except Exception as e:
        print(e)
    return account_info




