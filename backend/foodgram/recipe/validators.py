import webcolors


def validate_hex(value):
    if webcolors.normalize_hex(value):
        return value
