import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import unittest


spec = importlib.util.spec_from_file_location(
    "check_windows7", Path(__file__).with_name("check-windows7.py"))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def binary(dll, names, delay=False):
    pe = NS(FILE_HEADER=NS(Machine=0x8664), OPTIONAL_HEADER=NS(
        MajorOperatingSystemVersion=6, MinorOperatingSystemVersion=1,
        MajorSubsystemVersion=6, MinorSubsystemVersion=1))
    entry = NS(dll=dll.encode(), imports=[NS(name=n.encode()) for n in names])
    setattr(pe, "DIRECTORY_ENTRY_DELAY_IMPORT" if delay else "DIRECTORY_ENTRY_IMPORT", [entry])
    return pe


class Windows7CompatibilityTests(unittest.TestCase):
    def test_windows7_synchronization_is_accepted(self):
        pe = binary("KERNEL32.dll", ["SleepConditionVariableSRW", "WakeConditionVariable"])
        self.assertEqual(checker.compatibility_errors(pe), [])

    def test_reported_wake_by_address_error_is_rejected(self):
        pe = binary("api-ms-win-core-synch-l1-2-0.dll", ["kernel32.WakeByAddressSingle"])
        self.assertIn(
            "unsupported API: api-ms-win-core-synch-l1-2-0.dll!kernel32.WakeByAddressSingle",
            checker.compatibility_errors(pe))

    def test_newer_delayed_dependency_and_subsystem_are_rejected(self):
        pe = binary("bcryptprimitives.dll", ["ProcessPrng"], delay=True)
        pe.OPTIONAL_HEADER.MajorSubsystemVersion = 10
        errors = checker.compatibility_errors(pe)
        self.assertIn("unsupported DLL: bcryptprimitives.dll", errors)
        self.assertIn("subsystem version 10.1 requires a newer Windows", errors)


if __name__ == "__main__":
    unittest.main()
