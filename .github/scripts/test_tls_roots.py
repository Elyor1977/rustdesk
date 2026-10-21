import unittest

from check_tls_roots import REGISTRY, WRAPPER_CHECKSUM, check_roots


class TlsRootsTests(unittest.TestCase):
    def test_only_the_verified_wrapper_can_use_the_fixed_root_store(self):
        fixed = dict(name="webpki-roots", version="1.0.10", source=REGISTRY)
        wrapper = dict(name="webpki-roots", version="0.26.11", source=REGISTRY,
                       checksum=WRAPPER_CHECKSUM, dependencies=["webpki-roots 1.0.10"])
        check_roots([wrapper, fixed])
        for change in [dict(version="0.26.10"), dict(checksum="unknown"),
                       dict(source="git+https://example.invalid/roots"),
                       dict(dependencies=["webpki-roots 1.0.9"])]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                check_roots([wrapper | change, fixed])

    def test_downgraded_real_roots_are_never_exempted(self):
        with self.assertRaises(ValueError):
            check_roots([dict(name="webpki-roots", version="1.0.9", source=REGISTRY)])


if __name__ == "__main__":
    unittest.main()
