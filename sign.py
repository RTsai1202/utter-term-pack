#!/usr/bin/env python3
"""Ed25519 簽章（和 App 的 CryptoKit Curve25519.Signing 相容）。
sign：私鑰從環境變數 TERM_PACK_KEY 讀（base64 的 32 bytes），寫出 <file>.sig。
verify：用公鑰（base64）驗 <file> 與 <file>.sig。"""
import base64, os, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

def main():
    cmd, path = sys.argv[1], sys.argv[2]
    data = open(path, "rb").read()
    if cmd == "sign":
        key = Ed25519PrivateKey.from_private_bytes(base64.b64decode(os.environ["TERM_PACK_KEY"]))
        open(path + ".sig", "w").write(base64.b64encode(key.sign(data)).decode())
    elif cmd == "verify":
        pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(sys.argv[3]))
        pub.verify(base64.b64decode(open(path + ".sig").read().strip()), data)
        print("簽章正確")
    else:
        sys.exit("用法：sign.py sign|verify <file> [公鑰]")

if __name__ == "__main__":
    main()
