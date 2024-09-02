from tpre import hash2, hash3, hash4, multiply, g, sm2p256v1
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


if __name__ == "__main__":
    unittest.main()
