import random
import string


def pic_id(length):
	generated_strings = set()
	while True:
		result = ''.join(random.choice(string.ascii_uppercase) for _ in range(length))
		result += ''.join(random.choice(string.digits) for _ in range(length))

		if result not in generated_strings:
			generated_strings.add(result)
			return result

