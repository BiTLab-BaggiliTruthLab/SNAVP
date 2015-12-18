from .Depedencies.WorksheetData import WorksheetData
import json
import sqlite3
import datetime
import pygmaps
import os
import copy
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        conn = sqlite3.connect(filePath) # connect to database
        c = conn.cursor() # create cursor object
        c.execute('SELECT ctime, atime, display_name, json FROM search') # query required data
        print("RUNNING MAPQUEST")
        print(filePath)
        return True
    except:
        pass
    return False
# -------------------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):
    # print('ran MapQuest')
    mapQuest = WorksheetData()
    mapQuest.appName = 'MapQuest'
    mapQuest.headers = ['Created Time', 'Accessed Time', 'Name', 'Street', 'City', 'State', 'Zip', 'Latitude', 'Longitude', 'User Input']
    mapQuest.worksheetName = 'MapQuest'
    mapQuest.mapsPlotted = True
    mapQuest.appColor = '#ADD8E6'
    mapQuest.appColorText = 'Light Blue'

    conn = sqlite3.connect(filePath) # connect to database
    c = conn.cursor() # create cursor object
    c.execute('SELECT ctime, atime, display_name, json FROM search') # query required data

    # column indicies
    CREATED_TIME_IDX = 0
    ACCESSED_TIME_IDX = 1
    NAME_IDX = 2
    ADDRESS_INFO_IDX = 3

    allCoordinates = [] # for latitude latitude points

    row = c.fetchone()
    rowCount = 0
    while row:

        rowData = ['']*10

        if row[CREATED_TIME_IDX]:
            rowData[0] = datetime.datetime.fromtimestamp(row[CREATED_TIME_IDX]/1000).strftime('%Y-%m-%d %H:%M:%S')

        if row[ACCESSED_TIME_IDX]:
            rowData[1] = datetime.datetime.fromtimestamp(row[ACCESSED_TIME_IDX]/1000).strftime('%Y-%m-%d %H:%M:%S')

        if row[NAME_IDX]:
            rowData[2] = row[NAME_IDX]

        if row[ADDRESS_INFO_IDX]:
            decodedAddress = json.loads(row[ADDRESS_INFO_IDX])
            rowData[3] = decodedAddress["street"]
            rowData[4] = decodedAddress["locality"]
            rowData[5] = decodedAddress["region"]
            rowData[6] = decodedAddress["postalCode"]
            rowData[7] = decodedAddress["latLng"]["lat"]
            rowData[8] = decodedAddress["latLng"]["lng"]
            rowData[9] = decodedAddress["userInput"]

        if rowData[7] != '' and rowData[8] != '':
            # map center
            point = [float(rowData[7]), float(rowData[8]), "#0000FF", rowData[1]]
            # populates map
            mymap = pygmaps.maps(point[0], point[1], 12)
            mymap.addpoint(point[0], point[1], point[2], point[3])
            # create map file
            mymap.draw(outputLoc + "/MapQuest" + str(rowCount) + '.html')
            # append point to list to map all points
            allCoordinates.append(point)
            # path to map file
            mapPath = os.path.join(outputLoc + "/MapQuest" + str(rowCount) + '.html')
            mapQuest.pointMapPaths.append(mapPath)
        else:
            # append '' if no map so that the row count remains correct when writing
            mapQuest.pointMapPaths.append('')

        if allCoordinates:
            # list containing points for all applications map
            mapQuest.allApplicationPoints = copy.deepcopy(allCoordinates)
            for point in mapQuest.allApplicationPoints:
                point[2] = mapQuest.appColor
            try:
                mymap = pygmaps.maps(allCoordinates[0][0], allCoordinates[0][1], 10)
                for point in allCoordinates:
                    mymap.addpoint(point[0], point[1], point[2], point[3])

                mymap.draw(outputLoc + "/MapQuest_all_points.html")
                mapPath = os.path.join(outputLoc + "/MapQuest_all_points.html")
                mapQuest.allCoordinatesPath = mapPath
            except:
                pass

        mapQuest.appData.append(rowData)

        rowCount += 1
        row = c.fetchone()

    return mapQuest


