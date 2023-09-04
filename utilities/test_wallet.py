import requests


def fake_balance(input):
	url = "http://10.0.0.113:3000/payment.php"
	data = {"data": input}
	resp = requests.post(url=url, json=data)
	json_resp = resp.json()
	return json_resp.get("amount")

