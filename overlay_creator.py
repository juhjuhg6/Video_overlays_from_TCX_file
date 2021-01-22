import xml.etree.ElementTree as ET
import datetime


def parse_tcx(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    ns = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
          'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}

    trackpoints = []

    for trackpoint in root.findall('.//ns:Trackpoint', ns):
        trackpoint_dict = {}

        tp_time_elem = trackpoint.find('ns:Time', ns)
        tp_hr_elem = trackpoint.find('ns:HeartRateBpm/ns:Value', ns)
        tp_speed_elem = trackpoint.find('.//ns:Extensions/ns3:TPX/ns3:Speed', ns)

        if tp_time_elem is not None:
            trackpoint_dict['time'] = datetime.datetime.strptime(tp_time_elem.text, '%Y-%m-%dT%H:%M:%S.%fZ')
        if tp_hr_elem is not None:
            trackpoint_dict['hr'] = tp_hr_elem.text
        if tp_speed_elem is not None:
            trackpoint_dict['speed'] = tp_speed_elem.text

        trackpoints.append(trackpoint_dict)

    return trackpoints


def main():
    trackpoints = parse_tcx('test.tcx')
    print(trackpoints)


main()
