def byte_to_variation_selector(byte: int) -> str:
    if byte < 16:
        return chr(0xFE00 + byte)
    else:
        return chr(0xE0100 + (byte - 16))
   
def emoji_encode(base: str, plain_string: str) -> str:
    result = base
    for byte in bytes(plain_string, encoding="utf-8"):
        result += byte_to_variation_selector(byte)
    return result
 
def variation_selector_to_byte(char: str) -> int:
    code_point = ord(char)
    if 0xFE00 <= code_point <= 0xFE0F:
        return code_point - 0xFE00
    elif 0xE0100 <= code_point <= 0xE01EF:
        return (code_point - 0xE0100) + 16
    else:
        raise ValueError("Invalid variation selector")
   
def emoji_decode(encoded_string: str) -> str:
    if not encoded_string:
        return ""
   
    base = encoded_string[0]
    bytes_list = [variation_selector_to_byte(c) for c in encoded_string[1:]]
    return base + bytes(bytes_list).decode("utf-8")