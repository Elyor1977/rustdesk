import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "windows7_import_lib", Path(__file__).with_name("windows7-import-lib.py"))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class Windows7ImportLibraryTests(unittest.TestCase):
    def test_both_legacy_libraries_are_found_without_win7_build_script_support(self):
        with tempfile.TemporaryDirectory(prefix="win7 library ") as directory:
            cargo_home = Path(directory)
            directories = []
            for version, filename in (("0.42.2", "windows.lib"), ("0.48.5", "windows.0.48.5.lib")):
                library = cargo_home / f"registry/src/index/windows_x86_64_msvc-{version}/lib/{filename}"
                library.parent.mkdir(parents=True)
                library.touch()
                directories.append(library.parent.resolve())
            self.assertEqual(helper.find_import_libraries(cargo_home), directories)

    def test_missing_library_reports_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(FileNotFoundError, "cargo fetch"):
                helper.find_import_libraries(Path(directory))

    def test_missing_versioned_library_is_not_hidden_by_windows_lib(self):
        with tempfile.TemporaryDirectory() as directory:
            cargo_home = Path(directory)
            library = cargo_home / "registry/src/index/windows_x86_64_msvc-0.42.2/lib/windows.lib"
            library.parent.mkdir(parents=True)
            library.touch()
            with self.assertRaisesRegex(FileNotFoundError, r"windows\.0\.48\.5\.lib"):
                helper.find_import_libraries(cargo_home)


if __name__ == "__main__":
    unittest.main()
