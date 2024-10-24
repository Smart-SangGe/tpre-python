import sys
import os
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from tpre import (
    hash2,
    hash3,
    hash4,
    multiply,
    g,
    sm2p256v1,
    GenerateKeyPair,
    Encrypt,
    Decrypt,
    GenerateReKey,
    Encapsulate,
    ReEncrypt,
    DecryptFrags,
    MergeCFrag,
)
import random
import unittest


class TestHash2(unittest.TestCase):
    def setUp(self):
        self.double_G = (
            multiply(g, random.randint(0, sm2p256v1.N - 1)),
            multiply(g, random.randint(0, sm2p256v1.N - 1)),
        )

    def test_digest_type(self):
        digest = hash2(self.double_G)
        self.assertEqual(type(digest), int)

    def test_digest_size(self):
        digest = hash2(self.double_G)
        self.assertLess(digest, sm2p256v1.N)


class TestHash3(unittest.TestCase):
    def setUp(self):
        self.triple_G = (
            multiply(g, random.randint(0, sm2p256v1.N - 1)),
            multiply(g, random.randint(0, sm2p256v1.N - 1)),
            multiply(g, random.randint(0, sm2p256v1.N - 1)),
        )

    def test_digest_type(self):
        digest = hash3(self.triple_G)
        self.assertEqual(type(digest), int)

    def test_digest_size(self):
        digest = hash3(self.triple_G)
        self.assertLess(digest, sm2p256v1.N)


class TestHash4(unittest.TestCase):
    def setUp(self):
        self.triple_G = (
            multiply(g, random.randint(0, sm2p256v1.N - 1)),
            multiply(g, random.randint(0, sm2p256v1.N - 1)),
            multiply(g, random.randint(0, sm2p256v1.N - 1)),
        )
        self.Zp = random.randint(0, sm2p256v1.N - 1)

    def test_digest_type(self):
        digest = hash4(self.triple_G, self.Zp)
        self.assertEqual(type(digest), int)

    def test_digest_size(self):
        digest = hash4(self.triple_G, self.Zp)
        self.assertLess(digest, sm2p256v1.N)


class TestGenerateKeyPair(unittest.TestCase):
    def test_key_pair(self):
        public_key, secret_key = GenerateKeyPair()
        self.assertIsInstance(public_key, tuple)
        self.assertEqual(len(public_key), 2)
        self.assertIsInstance(secret_key, int)
        self.assertLess(secret_key, sm2p256v1.N)
        self.assertGreater(secret_key, 0)


# class TestEncryptDecrypt(unittest.TestCase):
#     def setUp(self):
#         self.public_key, self.secret_key = GenerateKeyPair()
#         self.message = b"Hello, world!"

#     def test_encrypt_decrypt(self):
#         encrypted_message = Encrypt(self.public_key, self.message)
#         # 使用 SHA-256 哈希函数确保密钥为 16 字节
#         secret_key_hash = hashlib.sha256(self.secret_key.to_bytes((self.secret_key.bit_length() + 7) // 8, 'big')).digest()
#         secret_key_int = int.from_bytes(secret_key_hash[:16], 'big')  # 取前 16 字节并转换为整数

#         decrypted_message = Decrypt(secret_key_int, encrypted_message)
#         self.assertEqual(decrypted_message, self.message)


class TestGenerateReKey(unittest.TestCase):
    def test_generate_rekey(self):
        sk_A = random.randint(0, sm2p256v1.N - 1)
        pk_B, _ = GenerateKeyPair()
        id_tuple = tuple(random.randint(0, sm2p256v1.N - 1) for _ in range(5))
        rekey = GenerateReKey(sk_A, pk_B, 5, 3, id_tuple)
        self.assertIsInstance(rekey, list)
        self.assertEqual(len(rekey), 5)


class TestEncapsulate(unittest.TestCase):
    def test_encapsulate(self):
        pk_A, _ = GenerateKeyPair()
        K, capsule = Encapsulate(pk_A)
        self.assertIsInstance(K, int)
        self.assertIsInstance(capsule, tuple)
        self.assertEqual(len(capsule), 3)


class TestReEncrypt(unittest.TestCase):
    def test_reencrypt(self):
        sk_A = random.randint(0, sm2p256v1.N - 1)
        pk_B, _ = GenerateKeyPair()
        id_tuple = tuple(random.randint(0, sm2p256v1.N - 1) for _ in range(5))
        rekey = GenerateReKey(sk_A, pk_B, 5, 3, id_tuple)
        pk_A, _ = GenerateKeyPair()
        message = b"Hello, world!"
        encrypted_message = Encrypt(pk_A, message)
        reencrypted_message = ReEncrypt(rekey[0], encrypted_message)
        self.assertIsInstance(reencrypted_message, tuple)
        self.assertEqual(len(reencrypted_message), 2)


# class TestDecryptFrags(unittest.TestCase):
#     def test_decrypt_frags(self):
#         sk_A = random.randint(0, sm2p256v1.N - 1)
#         pk_B, sk_B = GenerateKeyPair()
#         id_tuple = tuple(random.randint(0, sm2p256v1.N - 1) for _ in range(5))
#         rekey = GenerateReKey(sk_A, pk_B, 5, 3, id_tuple)
#         pk_A, _ = GenerateKeyPair()
#         message = b"Hello, world!"
#         encrypted_message = Encrypt(pk_A, message)
#         reencrypted_message = ReEncrypt(rekey[0], encrypted_message)
#         cfrags = [reencrypted_message]
#         merged_cfrags = MergeCFrag(cfrags)

#         self.assertIsNotNone(merged_cfrags)

#         sk_B_hash = hashlib.sha256(sk_B.to_bytes((sk_B.bit_length() + 7) // 8, 'big')).digest()
#         sk_B_int = int.from_bytes(sk_B_hash[:16], 'big')  # 取前 16 字节并转换为整数

#         decrypted_message = DecryptFrags(sk_B_int, pk_B, pk_A, merged_cfrags)
#         self.assertEqual(decrypted_message, message)


if __name__ == "__main__":
    unittest.main()
