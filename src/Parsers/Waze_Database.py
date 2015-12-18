from .Depedencies.WorksheetData import WorksheetData
import sqlite3
import datetime
import pygmaps, os
import copy

sqlQuery = '''SELECT pl.name,
                     street,
                     city,
                     state,
                     country,
                     house,
                     longitude,
                     latitude,
                     venue_id,
                     pl.created_time,
                     fav.created_time,
                     fav.modified_time
              FROM PLACES AS pl
              LEFT JOIN FAVORITES AS fav
              ON (pl.id = fav.place_id)
              ORDER BY pl.created_time'''
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

# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        conn = sqlite3.connect(filePath)
        c = conn.cursor()
        c.execute(sqlQuery)
        return True
    except:
        return False
# -------------------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):

    waze = WorksheetData()
    waze.appName = "Waze_Database"
    waze.headers = ['Name', 'Street', 'City', 'State', 'Country', 'House', 'Longitude', 'Latitude', 'Venue_id', 'Created_time', 'Is_favorite', 'Favorite_created_time', 'Favorite_modified_time']
    waze.worksheetName = "Waze_Database"
    waze.mapsPlotted = True
    waze.appColor = '#FFDB58'
    waze.appColorText = 'Mustard'

    conn = sqlite3.connect(filePath)
    c = conn.cursor()
    c.execute(sqlQuery)

    # column indexes for desired info
    NAME_COL_IDX = 0
    STREET_COL_IDX = 1
    CITY_COL_IDX = 2
    STATE_COL_IDX = 3
    COUNTRY_COL_IDX = 4
    HOUSE_COL_IDX = 5
    LONGITUDE_COL_IDX = 6
    LATITUDE_COL_IDX = 7
    VENUE_COL_IDX = 8
    CREATEDTIME_COL_IDX = 9
    FAV_CREATEDTIME_COL_IDX = 10
    FAV_MODIFIED_COL_IDX = 11

    allPoints = []
    rowCount = 0
    row = c.fetchone()
    while row:

        rowData = ['']*13

        if row[NAME_COL_IDX]:
            rowData[0] = row[NAME_COL_IDX]

        if row[STREET_COL_IDX]:
            rowData[1] = row[STREET_COL_IDX]

        if row[CITY_COL_IDX]:
            rowData[2] = row[CITY_COL_IDX]

        if row[STATE_COL_IDX]:
            rowData[3] = row[STATE_COL_IDX]

        if row[COUNTRY_COL_IDX]:
            rowData[4] = row[COUNTRY_COL_IDX]

        if row[HOUSE_COL_IDX]:
            rowData[5] = row[HOUSE_COL_IDX]

        if row[LONGITUDE_COL_IDX]:
            rowData[6] = addDecimalLng(str(row[LONGITUDE_COL_IDX]))

        if row[LATITUDE_COL_IDX]:
            rowData[7] = addDecimalLat(str(row[LATITUDE_COL_IDX]))

        if row[VENUE_COL_IDX]:
            rowData[8] = row[VENUE_COL_IDX]

        if row[CREATEDTIME_COL_IDX]:
            rowData[9] = datetime.datetime.fromtimestamp(row[CREATEDTIME_COL_IDX]).strftime('%Y-%m-%d %H:%M:%S')

        if row[FAV_CREATEDTIME_COL_IDX]:
            rowData[10] = "YES"
            rowData[11] = datetime.datetime.fromtimestamp(row[FAV_CREATEDTIME_COL_IDX]).strftime('%Y-%m-%d %H:%M:%S')
        else:
            rowData[10] = "NO"

        if row[FAV_MODIFIED_COL_IDX]:
            rowData[12] = datetime.datetime.fromtimestamp(row[FAV_MODIFIED_COL_IDX]).strftime('%Y-%m-%d %H:%M:%S')

        # coordinate points
        if rowData[6] and rowData[7]:
            point = [float(rowData[7]), float(rowData[6]), "#0000FF", rowData[1]]
            mymap = pygmaps.maps(point[0], point[1], 12)
            mymap.addpoint(point[0], point[1], point[2], point[3])
            mymap.draw(outputLoc + "/" + waze.appName + "_" + str(rowCount) + '.html')
            mapPath = os.path.join(outputLoc + "/" + waze.appName + "_" + str(rowCount) + '.html')
            waze.pointMapPaths.append(mapPath)
            allPoints.append(point)
        else:
            waze.pointMapPaths.append('')

        rowCount += 1
        waze.appData.append(rowData)
        row = c.fetchone()


    # all Waze points map
    if allPoints:
        # for all applications map
        waze.allApplicationPoints = copy.deepcopy(allPoints)
        for point in waze.allApplicationPoints:
            point[2] = waze.appColor

        try:
            mymap = pygmaps.maps(allPoints[0][0], allPoints[0][1], 10)
            for point in allPoints:
                mymap.addpoint(point[0], point[1], point[2], point[3])

            mymap.draw(outputLoc + "/Google_Maps_Nav_all_points.html")
            mapPath = os.path.join(outputLoc + "/" + waze.appName + "_" + str(rowCount) + '.html')
            waze.allCoordinatesPath = mapPath
        except:
            pass

    return waze