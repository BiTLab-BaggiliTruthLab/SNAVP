from .Depedencies.WorksheetData import WorksheetData
import sqlite3
import datetime
import os, pygmaps
import copy
# -------------------------------------------------------------------------------------------------
# Add decimal to lat coords (US Only)
def addDecimalLat(point):
    return point[:2] + "." + point[2:]
# -------------------------------------------------------------------------------------------------
# Add decimal to lng coords (US only)
def addDecimalLng(point):
    if point[1] == "1":										# add necessary decimal for longitude (only accurate for united states currently)
        return point[:4] + "." + point[4:]
    else:
        return point[:3] + "." + point[3:]
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        conn = sqlite3.connect(filePath)
        c = conn.cursor()
        c.execute('''   SELECT time,
                            dest_lat,
                            dest_lng,
                            dest_title,
                            dest_address,
                            source_lat,
                            source_lng
                        FROM destination_history''')
        return True
    except:
        pass
    return False
# -------------------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):
    google_maps = WorksheetData()
    google_maps.appName = "Google_Maps_Nav"
    google_maps.worksheetName = "Google_Maps_Nav"
    google_maps.headers = ['Start Time', 'Latitude Start', 'Longitude Start', 'Dest Title', 'Dest Address', 'Dest Latitude', 'Dest Longitude']
    google_maps.mapsPlotted = True
    google_maps.coordsPerRow = 2
    google_maps.appColor = '#FFA500'
    google_maps.appColorText = 'Orange'

    conn = sqlite3.connect(filePath)
    c = conn.cursor()
    c.execute('''   SELECT time,
                        dest_lat,
                        dest_lng,
                        dest_title,
                        dest_address,
                        source_lat,
                        source_lng
                    FROM destination_history''')

    TIME_COL_IDX = 0
    DEST_LAT_COL_IDX = 1
    DEST_LNG_COL_IDX = 2
    TITLE_COL_IDX = 3
    ADDR_COL_IDX = 4
    START_LAT_COL_IDX = 5
    START_LNG_COL_IDX = 6

    rowCount = 0
    allCoordinates = []

    row = c.fetchone()
    while row:
        rowData = ['']*7
        startPoint = None
        destPoint = None

        if row[TIME_COL_IDX]:
            rowData[0] = datetime.datetime.fromtimestamp(row[TIME_COL_IDX]/1000).strftime('%Y-%m-%d %H:%M:%S')

        if row[START_LAT_COL_IDX]:
            rowData[1] = addDecimalLat(str(row[START_LAT_COL_IDX]))

        if row[START_LNG_COL_IDX]:
            rowData[2] = addDecimalLng(str(row[START_LNG_COL_IDX]))

        if rowData[1] != '' and rowData[2] != '':
            startPoint = [float(rowData[1]), float(rowData[2]), "#00FF00", rowData[0]]
            allCoordinates.append(startPoint)

        if row[TITLE_COL_IDX]:
            rowData[3] = row[TITLE_COL_IDX]

        if row[ADDR_COL_IDX]:
            rowData[4] = row[ADDR_COL_IDX]

        if row[DEST_LAT_COL_IDX]:
            rowData[5] = addDecimalLat(str(row[DEST_LAT_COL_IDX]))

        if row[DEST_LNG_COL_IDX]:
            rowData[6] = addDecimalLng(str(row[DEST_LNG_COL_IDX]))

        if rowData[5] != '' and rowData[6] != '':
            destPoint = [float(rowData[5]), float(rowData[6]), "#FF0000", rowData[0]]
            allCoordinates.append(destPoint)

        if startPoint and destPoint:
            mymap = pygmaps.maps(startPoint[0], startPoint[1], 12)
            mymap.addpoint(startPoint[0], startPoint[1], startPoint[2], startPoint[3])
            mymap.addpoint(destPoint[0], destPoint[1], destPoint[2], destPoint[3])
            mymap.draw(outputLoc + "/Google_Maps_Nav" + str(rowCount) + '.html')
            mapPath = os.path.join(outputLoc + "/Google_Maps_Nav" + str(rowCount) + '.html')
            google_maps.pointMapPaths.append(mapPath)
        elif startPoint:
            mymap = pygmaps.maps(startPoint[0], startPoint[1], 12)
            mymap.addpoint(startPoint[0], startPoint[1], startPoint[2], startPoint[3])
            mymap.draw(outputLoc + "/Google_Maps_Nav" + str(rowCount) + '.html')
            mapPath = os.path.join(outputLoc + "/Google_Maps_Nav" + str(rowCount) + '.html')
            google_maps.pointMapPaths.append(mapPath)
        elif destPoint:
            mymap = pygmaps.maps(destPoint[0], destPoint[1], 12)
            mymap.addpoint(destPoint[0], destPoint[1], destPoint[2], destPoint[3])
            mymap.draw(outputLoc + "/Google_Maps_Nav" + str(rowCount) + '.html')
            mapPath = os.path.join(outputLoc + "/Google_Maps_Nav" + str(rowCount) + '.html')
            google_maps.pointMapPaths.append(mapPath)
        else:
            google_maps.pointMapPaths.append('')

        google_maps.appData.append(rowData)
        row = c.fetchone()

    if allCoordinates:
        try:
            mymap = pygmaps.maps(allCoordinates[0][0], allCoordinates[0][1], 10)
            for point in allCoordinates:
                mymap.addpoint(point[0], point[1], point[2], point[3])

            mymap.draw(outputLoc + "/Google_Maps_Nav_all_points.html")
            mapPath = os.path.join(outputLoc + "/Google_Maps_Nav_all_points.html")
            google_maps.allCoordinatesPath = mapPath
        except:
            pass

        # list containing points for all applications map
        google_maps.allApplicationPoints = copy.deepcopy(allCoordinates)
        for point in google_maps.allApplicationPoints:
            point[2] = google_maps.appColor

    return google_maps