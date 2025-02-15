"""
Base 64 encoded text
"""

import binascii
import regex as re
import warnings

from typing import Dict, List, Tuple

HTML_ESCAPE_RE = rb'&#(?:x[a-fA-F0-9]{1,4}|\d{1,4});'
BASE64_RE = rb'(?:[A-Za-z0-9+/]{4,}(?:<\x00  \x00)?(?:&#13;|&#xD;)?(?:&#10;|&#xA)?\r?\n?){5,}' \
            rb'[A-Za-z0-9+/]{2,}={0,2}'

CAMEL_RE = rb'(?i)[a-z]+'
HEX_RE = rb'(?i)[a-f0-9]+'
MIN_B64_CHARS = 6


def base64_search(text: bytes) -> Dict[bytes, bytes]:
    """
    Find all base64 encoded sections in a text.
    Args:
        text: The text to search.
    Returns:
        A dictionary with the original base64 encoded sections as keys
        and the corresponding decoded data as values.
    """
    warnings.warn("base64_search is depricated, use find_base64 instead", DeprecationWarning)
    b64_matches = {}
    for b64_match in re.findall(BASE64_RE, text):
        if b64_match in b64_matches:
            continue
        b64_string = re.sub(HTML_ESCAPE_RE, b'', b64_match).replace(b'\n', b'').replace(b'\r', b'') \
            .replace(b'<\x00  \x00', b'')
        if re.fullmatch(HEX_RE, b64_string):
            # Hexadecimal characters are a subset of base64
            # Hashes commonly are hex and have multiple of 4 lengths
            continue
        if re.fullmatch(CAMEL_RE, b64_string):
            # Camel case text can be confused for base64
            # It is common in scripts as names
            continue
        uniq_char = set(b64_string)
        if len(uniq_char) > MIN_B64_CHARS and len(b64_string) % 4 == 0:
            try:
                b64_result = binascii.a2b_base64(b64_string)
                b64_matches[b64_match] = b64_result
            except binascii.Error:
                pass
    return b64_matches


def find_base64(data: bytes) -> List[Tuple[bytes, int, int]]:
    """
    Find all base64 encoded sections in some data.

    Args:
        data: The data to search.
    Returns:
        A list of decoded base64 sections and the location indexes of the section
        in the original data.
    """
    b64_matches = []
    for b64_match in re.finditer(BASE64_RE, data):
        b64_string = re.sub(HTML_ESCAPE_RE, b'', b64_match.group()).replace(b'\n', b'').replace(b'\r', b'') \
            .replace(b'<\x00  \x00', b'')
        if len(b64_string) % 4 != 0 or len(set(b64_string)) <= MIN_B64_CHARS:
            continue
        if re.fullmatch(HEX_RE, b64_string):
            # Hexadecimal characters are a subset of base64
            # Hashes commonly are hex and have multiple of 4 lengths
            continue
        if re.fullmatch(CAMEL_RE, b64_string):
            # Camel case text can be confused for base64
            # It is common in scripts as names
            continue
        if b64_string.count(b'/')/len(b64_string) > 3/32:
            # If there are a lot of / it as more likely a path
            continue
        try:
            b64_result = binascii.a2b_base64(b64_string)
            b64_matches.append((b64_result, b64_match.start(), b64_match.end()))
        except binascii.Error:
            pass
    return b64_matches
