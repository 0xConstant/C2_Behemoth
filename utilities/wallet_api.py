import requests


def wallet_api(wallet_address):
	# send request to API and retrieve amount of money inside wallet_address
	url = "http://10.0.0.115:3000/payment.php"
	data = {'data': wallet_address}
	response = requests.post(url=url, data=data, timeout=2)
	return int(response.text.strip())

