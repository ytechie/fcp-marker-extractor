import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile

import timestamps


class ParseFCPTimeSecondsTests(unittest.TestCase):
    def test_parses_whole_seconds(self):
        self.assertEqual(timestamps.parse_fcp_time_seconds('12s'), 12.0)

    def test_parses_fractional_seconds(self):
        self.assertEqual(timestamps.parse_fcp_time_seconds('300/25s'), 12.0)

    def test_errors_on_invalid_input(self):
        with self.assertRaises(ValueError):
            timestamps.parse_fcp_time_seconds('')

        with self.assertRaises(ValueError):
            timestamps.parse_fcp_time_seconds('bad-value')

        with self.assertRaises(ValueError):
            timestamps.parse_fcp_time_seconds(None)

        with self.assertRaises(ValueError):
            timestamps.parse_fcp_time_seconds(123)

        with self.assertRaises(ValueError):
            timestamps.parse_fcp_time_seconds('10/20/30s')

    def test_errors_on_zero_denominator(self):
        with self.assertRaises(ValueError):
            timestamps.parse_fcp_time_seconds('1/0s')


class MarkerTimestampTests(unittest.TestCase):
    def test_calculate_marker_seconds_rounds_result(self):
        seconds = timestamps.calculate_marker_seconds(
            parent_offset=10.0,
            parent_start=2.0,
            marker_start=9.6,
        )
        self.assertEqual(seconds, 18)

    def test_extract_marker_lines_preserves_output_format(self):
        root = ET.fromstring(
            '<fcpxml><sequence offset="10s" start="5s"><marker start="9s" value="A"/></sequence></fcpxml>'
        )

        lines = timestamps.extract_marker_lines(root)

        self.assertEqual(lines, ['0:00:14 A'])

    def test_extract_marker_lines_errors_on_missing_parent_offset(self):
        root = ET.fromstring(
            '<fcpxml><sequence start="5s"><marker start="9s" value="A"/></sequence></fcpxml>'
        )

        with self.assertRaises(ValueError) as ctx:
            timestamps.extract_marker_lines(root)

        self.assertIn("offset", str(ctx.exception))

    def test_extract_marker_lines_errors_on_missing_marker_value(self):
        root = ET.fromstring(
            '<fcpxml><sequence offset="10s" start="5s"><marker start="9s"/></sequence></fcpxml>'
        )

        with self.assertRaises(ValueError) as ctx:
            timestamps.extract_marker_lines(root)

        self.assertIn("value", str(ctx.exception))


class LoadXmlRootTests(unittest.TestCase):
    def test_load_xml_root_errors_for_missing_file(self):
        missing_path = Path(tempfile.gettempdir()) / "definitely_missing.fcpxml"

        with self.assertRaises(FileNotFoundError):
            timestamps.load_xml_root(str(missing_path))

    def test_load_xml_root_errors_for_malformed_xml(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        malformed_path = Path(tmp_dir.name) / "malformed.fcpxml"
        malformed_path.write_text("<fcpxml><broken></fcpxml>", encoding="utf-8")

        with self.assertRaises(ValueError):
            timestamps.load_xml_root(str(malformed_path))


if __name__ == '__main__':
    unittest.main()
