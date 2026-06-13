import unittest
import xml.etree.ElementTree as ET

import timestamps


class ParseFCPTimeSecondsTests(unittest.TestCase):
    def test_parses_whole_seconds(self):
        self.assertEqual(timestamps.parse_fcp_time_seconds('12s'), 12.0)

    def test_parses_fractional_seconds(self):
        self.assertEqual(timestamps.parse_fcp_time_seconds('300/25s'), 12.0)


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


if __name__ == '__main__':
    unittest.main()
