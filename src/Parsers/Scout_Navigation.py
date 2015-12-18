from .Depedencies.WorksheetData import WorksheetData
import sqlite3
import json
import pygmaps, os
import copy
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        conn = sqlite3.connect(filePath)
        c = conn.cursor()
        c.execute('SELECT data FROM userEntityStore')
        print("RUNNING SCOUT NAVIGATION")
        print(filePath)
        return True
    except:
        pass
    return False
# userEntityStore ----------------------------------------------------------------------------------
def runParser(filePath, outputLoc):

    scout = WorksheetData()
    scout.appName = "Scout_Navigation"
    scout.headers = ['Phone Number', 'Name', 'House Number', 'Street', 'City', 'State', 'Zip Code', 'Country', 'Longitude', 'Latitude']
    scout.mapsPlotted = True
    scout.worksheetName = "Scout_Navigation"
    scout.appColor = '8D38C9'
    scout.appColorText = 'Violet'

    #'/Users/Jay/Dropbox/Thesis/scoutAppDatabase.db'
    conn = sqlite3.connect(filePath)
    c = conn.cursor()
    c.execute('SELECT data FROM userEntityStore')

    DATA_COL_IDX = 0

    allPoints = []    # list to hold all coordinates for mapping purposes
    rowCount = 0

    row = c.fetchone()
    while row:

        rowData = ['']*10   # order : phone number, name, house num, street, city, zip, country, longitude, latitude
        point = ['']*4

        if row[DATA_COL_IDX] is not None:
            decoded = row[DATA_COL_IDX].decode("UTF-8")
            decodedData = json.loads(decoded)
            rowData[0] = decodedData["phone_number"]                                    # phone number
            rowData[1] = decodedData["name"]                                            # name
            rowData[2] = decodedData["display_address"]["house_number"]                 # house number
            rowData[3] = decodedData["display_address"]["street"]["formatted_name"]     # street
            rowData[4] = decodedData["display_address"]["city"]                         # city
            rowData[5] = decodedData["display_address"]["state"]                        # state
            rowData[6] = decodedData["display_address"]["postal_code"]                  # zip
            rowData[7] = decodedData["display_address"]["country"]                      # country
            rowData[8] = decodedData["rooftop_geocode"]["lon"]                          # longitude
            rowData[9] = decodedData["rooftop_geocode"]["lat"]                          # latitude

        if rowData[8] != '' and rowData[9] != '':
            point = [float(rowData[9]), float(rowData[8]), "#0000FF", rowData[2] + ' ' + rowData[3]]
            # map creation
            mymap = pygmaps.maps(point[0], point[1], 12)
            mymap.addpoint(point[0], point[1], point[2], point[3])
            mymap.draw(outputLoc + "/Scout_Navigation" + str(rowCount) + '.html')
            # create map path and append to pointMapPaths
            scout.pointMapPaths.append(os.path.join(outputLoc + "/Scout_Navigation" + str(rowCount) + '.html'))
            allPoints.append(point) # to map all points
        else:
            scout.pointMapPaths.append('')

        scout.appData.append(rowData)
        rowCount += 1
        row = c.fetchone()


    if allPoints:
        # list containing points for all applications map
        scout.allApplicationPoints = copy.deepcopy(allPoints)
        for point in scout.allApplicationPoints:
            point[2] = scout.appColor
        try:
            mymap = pygmaps.maps(allPoints[0][0], allPoints[0][1], 10)
            for point in allPoints:
                mymap.addpoint(point[0], point[1], point[2], point[3])

            mymap.draw(outputLoc + "/Scout_Navigation_all_points.html")
            scout.allCoordinatesPath = os.path.join(outputLoc + "/Scout_Navigation_all_points.html")
        except:
            pass

    return scout
