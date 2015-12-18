from .Depedencies.WorksheetData import WorksheetData
from xml.etree import ElementTree
import datetime
import pygmaps, os
import copy
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        with open(filePath, 'r') as file_in:	# alters XML file so that it may be parsed
            with open('file_out.xml', 'w') as file_out:
                data = file_in.read()
                data = data.replace("UNICODE", "UTF-8", 1)	# changes encoding name to UTF-8
                while data.endswith('\x00'):				# removes all NUL characters at the end of the file
                    data = data[:-1]
                file_out.write(data)

        file_out.close()

        with open("file_out.xml", "rt") as f:
            tree = ElementTree.parse(f)

        routeNumbers = []
        root = tree.getroot()

        if root.iter('Routes'):
            return True

    except:
        pass
    return False
# --------------------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):
    scoutRoute = WorksheetData()
    scoutRoute.appName = "Scout_" + filePath[-14:-4]
    scoutRoute.worksheetName = "Scout_" + filePath[-14:-4]
    scoutRoute.headers = ["Time", "Position", "Latitude", "Longitude"]
    scoutRoute.appColor = '#B87333'
    scoutRoute.appColorText = 'Copper'

    time = datetime.datetime.fromtimestamp(int(filePath[-14:-4])).strftime('%Y-%m-%d %H:%M:%S')

    with open(filePath, 'r') as file_in:	# alters XML file so that it may be parsed
        with open('file_out.xml', 'w') as file_out:
            data = file_in.read()
            data = data.replace("UNICODE", "UTF-8", 1)	# changes encoding name to UTF-8
            while data.endswith('\x00'):				# removes all NUL characters at the end of the file
                data = data[:-1]
            file_out.write(data)

    file_out.close()

    with open("file_out.xml", "rt") as f:
        tree = ElementTree.parse(f)

    routeNumbers = []
    root = tree.getroot()

    for child in root.iter('Routes'):							# finds the used route for trip
        selectedRoute = child.attrib['Selected_route_id']
        for subchild in child:
            if subchild.attrib['ID'] == selectedRoute:			# finds the correct route from the list of routes in the XML file
                for child in subchild.iter('Edge_id_list'):		# iterates through all segments of the route
                    routeNumbers.append(child.text.split(","))	# adds segments to the routeNumbers list

    finalRoute = []
    for segment in routeNumbers:	# goes through all lists in routeNumbers and joins them to create one list
        finalRoute += segment

    coords = []
    for child in root.iter('Edges'):
        for subchild in child:
            if subchild.attrib['ID'] in finalRoute:
                 coords.append(subchild[0].text.split(",")[:2])

    count = 0
    for coordPair in coords:
        rowData = [time, '', '', '']
        rowData[2] = coordPair[0] = float(coordPair[0][:2] + "." + coordPair[0][2:])	# add necessary decimal for latitude (only accurate for united states currently)
        if coordPair[1][1] == "1":										# add necessary decimal for longitude (only accurate for united states currently)
            rowData[3] = coordPair[1] = float(coordPair[1][:4] + "." + coordPair[1][4:])
        else:
            rowData[3] = coordPair[1] = float(coordPair[1][:3] + "." + coordPair[1][3:])
        if count == 0:
            coordPair.append("#00FF00")
            rowData[1] = "Start"
        elif count == len(coords) - 1:
            coordPair.append("#FF0000")
            rowData[1] = "Destination"
        else:
            coordPair.append("#0000FF")
            rowData[1] = "En Route"
        coordPair.append(time)
        count += 1
        scoutRoute.appData.append(rowData)

    if coords:
        # list containing points for all applications map
        scoutRoute.allApplicationPoints = copy.deepcopy(coords)
        for point in scoutRoute.allApplicationPoints:
            point[2] = scoutRoute.appColor
        try:
            mymap = pygmaps.maps(coords[0][0], coords[0][1], 10)
            for point in coords:
                mymap.addpoint(point[0], point[1], point[2], point[3])

            mymap.draw(outputLoc + "/" + scoutRoute.appName + "all_points.html")
            scoutRoute.allCoordinatesPath = os.path.join(outputLoc + "/" + scoutRoute.appName + "all_points.html")
        except:
            pass

    return scoutRoute