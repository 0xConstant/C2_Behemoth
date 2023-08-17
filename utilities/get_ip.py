import requests


def user_geolocation(ip):
	location = {}
	try:
		url = f'https://ipapi.co/{ip}/json/'
		resp = requests.get(url=url, timeout=10).json()
		location = {
			"IP": ip,
			"city": resp.get("city"),
			"region": resp.get("region"),
			"country": resp.get("country_name"),
			"postal": resp.get("postal"),
			"latitude": resp.get("latitude"),
			"longitude": resp.get("longitude"),
		}
	except: pass
	return location


