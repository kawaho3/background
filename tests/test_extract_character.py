"""Unit checks requiring Python standard library only (no model downloads)."""
import importlib.util
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "scripts" / "extract_character.py"
spec = importlib.util.spec_from_file_location("extract_character", PATH)
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


class EncoderTests(unittest.TestCase):
    def test_webm_alpha_and_silence(self):
        command = extractor.encode_command("frame_%06d.png", Path("out.webm"), "25/1")
        self.assertIn("yuva420p", command)
        self.assertIn("libvpx-vp9", command)
        self.assertIn("-an", command)
        self.assertIn("-auto-alt-ref", command)

    def test_mov_alpha_and_silence(self):
        command = extractor.encode_command("frame_%06d.png", Path("out.mov"), "30000/1001")
        self.assertIn("argb", command)
        self.assertIn("qtrle", command)
        self.assertIn("-an", command)

    def test_reject_mp4_without_alpha(self):
        with self.assertRaises(ValueError):
            extractor.encode_command("frame_%06d.png", Path("out.mp4"), "30")


if __name__ == "__main__":
    unittest.main()
