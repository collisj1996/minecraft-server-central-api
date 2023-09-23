import base64
import hashlib


def _get_checksum(base64_string: str) -> str:
    """Returns the checksum of a base64 string"""

    # Remove metadata from base64 string
    base64_data = base64_string.split("base64,")[1]

    # Decode the base64 image
    decoded_data = base64.b64decode(base64_data.encode() + b"==")

    return hashlib.md5(decoded_data).hexdigest()
