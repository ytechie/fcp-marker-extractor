import argparse
import datetime
import sys
import xml.etree.ElementTree as ET

DEFAULT_INPUT_PATH = './info.fcpxml'
XML_NAMESPACE = {'fcpxml': 'http://www.apple.com/fcpxml-1.0/'}
MARKER_PARENT_XPATH = './/marker/..'
MARKER_XPATH = './/marker'


def parse_fcp_time_seconds(time_string):
    values = [float(value) for value in time_string.replace('s', '').split('/')]
    if len(values) == 1:
        return values[0]
    return values[0] / values[1]


def calculate_marker_seconds(parent_offset, parent_start, marker_start):
    return round(marker_start - parent_start + parent_offset)


def format_marker_output(seconds, marker_value):
    return f"{datetime.timedelta(seconds=seconds)} {marker_value}"


def _required_attribute(element, attribute_name, element_name):
    value = element.get(attribute_name)
    if value is None:
        raise ValueError(f"Missing required '{attribute_name}' attribute on {element_name} element")
    return value


def load_xml_root(xml_path):
    try:
        tree = ET.parse(xml_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input file not found: {xml_path}") from exc
    except ET.ParseError as exc:
        raise ValueError(f"Malformed XML in input file: {xml_path}") from exc
    return tree.getroot()


def extract_marker_lines(root):
    marker_parents = root.findall(MARKER_PARENT_XPATH, XML_NAMESPACE)
    lines = []

    for parent in marker_parents:
        parent_offset = parse_fcp_time_seconds(
            _required_attribute(parent, 'offset', 'parent')
        )
        parent_start = parse_fcp_time_seconds(
            _required_attribute(parent, 'start', 'parent')
        )

        for marker in parent.findall(MARKER_XPATH):
            marker_start = parse_fcp_time_seconds(
                _required_attribute(marker, 'start', 'marker')
            )
            marker_value = _required_attribute(marker, 'value', 'marker')
            seconds = calculate_marker_seconds(parent_offset, parent_start, marker_start)
            lines.append(format_marker_output(seconds, marker_value))

    return lines


def run(xml_path):
    root = load_xml_root(xml_path)
    return extract_marker_lines(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Extract and print Final Cut Pro marker timestamps.')
    parser.add_argument('input_path', nargs='?', default=DEFAULT_INPUT_PATH)
    args = parser.parse_args(argv)

    try:
        lines = run(args.input_path)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    for line in lines:
        print(line)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
