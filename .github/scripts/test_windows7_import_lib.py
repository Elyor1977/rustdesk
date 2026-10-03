import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "windows7_import_lib", Path(__file__).with_name("windows7-import-lib.py"))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class Windows7ImportLibraryTests(unittest.TestCase):
    def test_legacy_library_is_found_without_win7_build_script_support(self):
        with tempfile.TemporaryDirectory(prefix="win7 library ") as directory:
            cargo_home = Path(directory)
            library = cargo_home / "registry/src/index/windows_x86_64_msvc-0.42.2/lib/windows.lib"
            library.parent.mkdir(parents=True)
            library.touch()
            self.assertEqual(helper.find_import_library(cargo_home), library.parent.resolve())

    def test_missing_library_reports_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(FileNotFoundError, "cargo fetch"):
                helper.find_import_library(Path(directory))


if __name__ == "__main__":
    unittest.main()
