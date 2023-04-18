import xml.etree.ElementTree as ET
import datetime

# Parse the Final Cut Pro XML file
tree = ET.parse('./info.fcpxml')

# Get the root element of the XML tree
root = tree.getroot()

# Define the namespace used in the XML file
ns = {'fcpxml': 'http://www.apple.com/fcpxml-1.0/'}

# Find all marker elements in the XML tree
markerParents = root.findall('.//marker/..', ns)

def parseFCPTimeSeconds (timeString):
    vals = [float(n) for n in timeString.replace('s','').split('/')]
    if 1 == len(vals):
        val = vals[0]
    else:
        val = vals[0]/vals[1]
    return val

# Loop through the marker elements and extract the start attribute value
for parents in markerParents:
    offset = parseFCPTimeSeconds(parents.get('offset'))
    start = parseFCPTimeSeconds(parents.get('start'))

    # print("Parent offset: " + str(offset))
    markers = parents.findall(".//marker")
    for marker in markers:
        s = parseFCPTimeSeconds(marker.get('start'))
        s = round(s - start + offset)

        timeStr = str(datetime.timedelta(seconds=s))

        print(timeStr + " " + marker.get("value"))
