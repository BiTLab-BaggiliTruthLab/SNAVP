from .Depedencies.WorksheetData import WorksheetData
import sqlite3
import datetime
import pygmaps, os
import copy
# -------------------------------------------------------------------------------------------------------------
# Add decimal to lat coords (US Only)
def addDecimalLat(point):
    return point[:2] + "." + point[2:]
# -------------------------------------------------------------------------------------------------------------
# Add decimal to lng coords (US only)
def addDecimalLng(point):
    # add necessary decimal for longitude (only accurate for united states currently)
    if point[1] == "1":
        return point[:4] + "." + point[4:]
    else:
        return point[:3] + "." + point[3:]
# -------------------------------------------------------------------------------------------------------------
def checkValid(filePath):
    # validity = validityCheck
    try:
        conn = sqlite3.connect(filePath)
        c = conn.cursor()
        c.execute('''    SELECT  data1,
                                        displayQuery,
                                        latitude,
                                        longitude,
                                        timestamp
                                FROM    suggestions''')
        # validity.run = validityCheck.PASS
        print("RUNNING GOOGLE MAPS SEARCH")
        print(filePath)
        return True
    except:
        return False
    # return validity
# Search sheet -------------------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):
    google_maps = WorksheetData()
    google_maps.appName = 'Google_Maps_Search'
    google_maps.worksheetName = 'Google_Maps_Search'
    google_maps.headers = ['Search Time', 'Search Text', 'Displayed Text', 'Latitude', ' Longitude']
    google_maps.mapsPlotted = True
    google_maps.appColor = '#808000'
    google_maps.appColorText = 'Olive'

    searchConn = sqlite3.connect(filePath)
    searchCursor = searchConn.cursor()
    searchCursor.execute('''    SELECT  data1,
                                        displayQuery,
                                        latitude,
                                        longitude,
                                        timestamp
                                FROM    suggestions''')

    SEARCH_COL_IDX = 0
    DISPLAY_COL_IDX = 1
    LAT_COL_IDX = 2
    LNG_COL_IDX = 3
    TIME_COL_IDX = 4

    allPoints = []

    rowCount = 0
    row = searchCursor.fetchone()
    while row:
        rowData = ['']*5

        if row[TIME_COL_IDX]:
            rowData[0] = datetime.datetime.fromtimestamp(row[TIME_COL_IDX]/1000).strftime('%Y-%m-%d %H:%M:%S')

        if row[SEARCH_COL_IDX]:
            rowData[1] = row[SEARCH_COL_IDX]

        if row[DISPLAY_COL_IDX]:
            rowData[2] = row[DISPLAY_COL_IDX]

        if row[LAT_COL_IDX]:
            rowData[3] = addDecimalLat(str(row[LAT_COL_IDX]))

        if row[LNG_COL_IDX]:
            rowData[4] = addDecimalLng(str(row[LNG_COL_IDX]))

        if rowData[3] != '' and rowData[4] != '':
            point = [float(rowData[3]), float(rowData[4]), "#0000FF", rowData[0]]
            mymap = pygmaps.maps(point[0], point[1], 12)
            mymap.addpoint(point[0], point[1], point[2], point[3])
            mymap.draw(outputLoc + "/Google_Maps_Search" + str(rowCount) + '.html')
            mapPath = os.path.join(outputLoc + "/Google_Maps_Search" + str(rowCount) + '.html')
            google_maps.pointMapPaths.append(mapPath)
            allPoints.append(point)
        else:
            google_maps.pointMapPaths.append('')

        google_maps.appData.append(rowData)
        rowCount += 1
        row = searchCursor.fetchone()

    if allPoints:
         # list containing points for all applications map
        google_maps.allApplicationPoints = copy.deepcopy(allPoints)
        for point in google_maps.allApplicationPoints:
            point[2] = google_maps.appColor

        try:
            mymap = pygmaps.maps(allPoints[0][0], allPoints[0][1], 10)
            for point in allPoints:
                mymap.addpoint(point[0], point[1], point[2], point[3])

            mymap.draw(outputLoc + "/Google_Maps_Nav_all_points.html")
            mapPath = os.path.join(outputLoc + "/Google_Maps_Nav_all_points.html")
            google_maps.allCoordinatesPath = mapPath
        except:
            pass

    return google_maps