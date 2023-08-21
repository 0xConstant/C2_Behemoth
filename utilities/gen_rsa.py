import base64
import xml.etree.ElementTree as ET
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from Crypto.PublicKey import RSA
from Crypto.Util import number


def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_key_pem, public_key_pem


def to_base64(input_data):
    return base64.b64encode(input_data).decode('utf-8')


def pub_to_xml(public_key_pem):
    publicKey = RSA.import_key(public_key_pem)
    xml_format = '''<RSAKeyValue><Modulus>{modulus}</Modulus><Exponent>{exponent}</Exponent></RSAKeyValue>'''

    return xml_format.format(
        modulus=to_base64(number.long_to_bytes(publicKey.n)),
        exponent=to_base64(number.long_to_bytes(publicKey.e))
    )


def priv_key_to_xml(private_key_pem):
    private_key_bytes = private_key_pem.encode('utf-8')
    private_key = serialization.load_pem_private_key(
        private_key_bytes, password=None, backend=default_backend()
    )
    numbers = private_key.private_numbers()

    xml_root = ET.Element("RSAKeyValue")
    components = [
        ("Modulus", numbers.public_numbers.n),
        ("Exponent", numbers.public_numbers.e),
        ("D", numbers.d),
        ("P", numbers.p),
        ("Q", numbers.q),
        ("DP", numbers.dmp1),
        ("DQ", numbers.dmq1),
        ("InverseQ", numbers.iqmp)
    ]

    for tag, component in components:
        element = ET.SubElement(xml_root, tag)
        element.text = to_base64(component.to_bytes((component.bit_length() + 7) // 8, 'big'))

    return ET.tostring(xml_root).decode("utf8").replace('\n', '').replace(' ', '')


def gen_keys():
    private_key_pem, public_key_pem = generate_rsa_keys()
    user_priv_key = priv_key_to_xml(private_key_pem)
    user_pub_key = pub_to_xml(public_key_pem)
    return user_priv_key, user_pub_key


#print(gen_keys())
