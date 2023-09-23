from msc.utils.file_utils import _get_checksum


def test_get_checksum():
    with open("tests/resources/test_icon_base64_string.txt", "r") as file:
        image_base64_string = file.read()

    checksum = _get_checksum(image_base64_string)
    checksum_2 = _get_checksum(image_base64_string)

    assert checksum == checksum_2 == "1b28f993c9d2852b501e852d90a3e36b"


def test_get_checksum_difference():
    with open("tests/resources/test_icon_base64_string.txt", "r") as file:
        icon_base64_string = file.read()

    with open("tests/resources/test_image_base64_string.txt", "r") as f:
        banner_base64_string = f.read()

    icon_checksum = _get_checksum(icon_base64_string)
    banner_checksum = _get_checksum(banner_base64_string)

    assert icon_checksum != banner_checksum
    assert icon_checksum == "1b28f993c9d2852b501e852d90a3e36b"
    assert banner_checksum == "a8711334dc49933d0ead43512e8c3d17"
