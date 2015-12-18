from .Depedencies.WorksheetData import WorksheetData
import datetime
import re
import os, pygmaps
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        f = open(filePath, 'r')
        g = iter(f)
        for line in g:
            if line.startswith("***") or filePath[-12:] == 'waze_log.txt':
                return True
    except:
        return False
# -------------------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):
    wazeLog = WorksheetData()
    wazeLog.appName = 'Waze_Log'
    wazeLog.worksheetName = 'Waze_Log'
    wazeLog.headers = ['Day', 'Time', 'Current Location', 'Starting Location', 'Destination Location']
    wazeLog.mapsPlotted = True
    wazeLog.appColor = '#000000'
    wazeLog.appColorText = 'Black'

    f = open(filePath, 'r')
    g = iter(f)

    prevLine = ''
    prevPrevLine = ''

    dates = {}

    for line in g:
        if line.startswith("***"):
            date = re.search(r'(\d+/\d+/\d+)', line)
            formedDate = datetime.datetime.strptime(date.group(1), '%d/%m/%Y').strftime('%m/%d/%Y')
            dates[formedDate] = {}
        if "RoutingRequest" in line:
            # before = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', prevPrevLine) # find timestamp before RoutingRequest
            after = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', next(g)) # find timestamp after RoutingRequest
            coords = re.findall(r'(-?\d{8,15}\,\d{8,9})', line) # find all longitude and latitude coords

            if len(coords) > 3:
                del coords[1] # delete erroneaous data

            # split up longitude, latitude coords
            for i in range(len(coords)):
                coords[i] = coords[i].split(",")

            for coordPair in coords:
                coordPair[1] = coordPair[1][:2] + "." + coordPair[1][2:]  		# add necessary decimal for latitude (only accurate for united states currently)
                if coordPair[0][1] == "1":										# add necessary decimal for longitude (only accurate for united states currently)
                    coordPair[0] = coordPair[0][:4] + "." + coordPair[0][4:]
                else:
                    coordPair[0] = coordPair[0][:3] + "." + coordPair[0][3:]

            dates[formedDate][after.group(1)] = {}
            dates[formedDate][after.group(1)]['startingLoc'] = coords[0]
            dates[formedDate][after.group(1)]['destinationLoc'] = coords[1]

        if line.startswith("At"):
            currentLocDate = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', prevLine)
            currentLocCoords = re.findall(r'(-?\d{2,3}\.\d{6})', line)
            try:
                if currentLocDate:
                    dates[formedDate][currentLocDate.group(1)] = {}
                else:
                    currentLocDate = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', prevPrevLine)
                    dates[formedDate][currentLocDate.group(1)] = {}

                dates[formedDate][currentLocDate.group(1)]['currentLoc'] = currentLocCoords
            except:
                pass

        prevPrevLine = prevLine
        prevLine = line

    rowNum = 1
    counter = 0

    for key in sorted(dates):
        for date in sorted(dates[key]):
            rowData = [key,"","NA","NA","NA"]
            rowData[1] = date
            if date in dates[key]:
                try:
                    rowData[2] = ", ".join(dates[key][date]['currentLoc'])
                except:
                    pass
                try:
                    rowData[3] = ", ".join(dates[key][date]['startingLoc'])
                except:
                    pass
                try:
                    rowData[4] = ", ".join(dates[key][date]['destinationLoc'])
                except:
                    pass

                points = []
                # titles = []
                colors = []
                if rowData[2] != "NA":
                    points.append([float(i) for i in dates[key][date]['currentLoc']])
                    # titles.append("Current Location")
                    colors.append("#0000FF") # blue
                if rowData[3] != "NA":
                    points.append([float(i) for i in dates[key][date]['startingLoc']])
                    # titles.append("Starting Location")
                    colors.append("#00FF00") # green
                if rowData[4] != "NA":
                    points.append([float(i) for i in dates[key][date]['destinationLoc']])
                    # titles.append("Destination")
                    colors.append("#FF0000") # red

                mymap = pygmaps.maps(points[0][1], points[0][0], 12) # latitude, longitude
                marker = 0
                for point in points:
                    mymap.addpoint(point[1], point[0], colors[marker])
                    marker +=1
                    wazeLog.allApplicationPoints.append([point[1], point[0], wazeLog.appColor, wazeLog.appName])

                mymap.draw(outputLoc + '/Waze_Log_' + str(rowNum) + '.html')

                wazeLog.pointMapPaths.append(os.path.join(outputLoc + '/Waze_Log_' + str(rowNum) +'.html'))
                wazeLog.appData.append(rowData)

            rowNum += 1
            counter+= 1

    return wazeLog