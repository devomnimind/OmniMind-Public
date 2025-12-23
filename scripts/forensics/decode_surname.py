import base64
import binascii

b64_str = "MjQ9P7cEdL+3Kp5Mwlyv"

try:
    decoded = base64.b64decode(b64_str)
    print(f"Decoded (Bytes): {decoded}")
    print(f"Decoded (Hex): {binascii.hexlify(decoded)}")
    try:
        print(f"Decoded (UTF-8): {decoded.decode('utf-8')}")
    except:
        print("Decoded (UTF-8): <Not valid UTF-8>")
except Exception as e:
    print(f"Error: {e}")
