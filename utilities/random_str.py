import string
import secrets


def secure_string(length: int) -> str:
	uppercase_letters = string.ascii_uppercase
	digits = string.digits
	special_characters = "#@$%*-_=+~"

	random_string = [
		secrets.choice(uppercase_letters),
		secrets.choice(digits),
		secrets.choice(special_characters),
		secrets.choice(special_characters)
	]
	for _ in range(length - 4):
		random_string.append(secrets.choice(uppercase_letters + digits + special_characters))
	secrets.SystemRandom().shuffle(random_string)
	return ''.join(random_string)

