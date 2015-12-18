from Parsers.Depedencies.WorksheetData import WorksheetData
from Parsers.Depedencies import FileCheck, Mount
import xlsxwriter
import os
import argparse
import pygmaps

# First sheet of Excel file that shows what parsers were ran and what file they were ran on
def parsersRanSheet(parserRanList, allAppsMapPath):
    rowNum = 2
    headers = ["Name", "File Path", "Color Key"]
    parsersRan.write_row("A1", headers, bold)
    for data in parserRanList:
        excelRow = "A" + str(rowNum)
        parsersRan.write_row(excelRow, data)
        rowNum += 1
    if allAppsMapPath:
        parsersRan.write_url(rowNum - 1, len(headers), 'external:' + allAppsMapPath, link_format, "Map All Points")

# Plot all applications Map ---------------------------------------------------------------
def allAppsMap(pointsFromAll):
    mymap = pygmaps.maps(pointsFromAll[0][0][0], pointsFromAll[0][0][1], 10)
    for singleApp in pointsFromAll:
        for point in singleApp:
            mymap.addpoint(point[0], point[1], point[2], point[3])

    mymap.draw(outputLoc + "/all_applications.html")
    return os.path.join(outputLoc + "/all_applications.html")

# Writes out data from parsers ------------------------------------------------------------
def writeOut(outData):
    count = 0
    worksheet = workbook.add_worksheet(outData.worksheetName)
    worksheet.write_row("A1", outData.headers, bold)
    rowNum = 2

    for row in outData.appData:
        # write out parser data to Excel sheet
        excelRow = 'A' + str(rowNum)
        worksheet.write_row(excelRow, row)
        if outData.mapsPlotted:
            if outData.pointMapPaths[count]:
                try:
                    worksheet.write_url(rowNum - 1, len(outData.headers), 'external:' + outData.pointMapPaths[count], link_format, "See On Map")
                except:
                    continue
        count += 1
        rowNum += 1
    # write url to all points map
    if outData.allCoordinatesPath:
        try:
            worksheet.write_url(rowNum - 1, len(outData.headers), 'external:' + outData.allCoordinatesPath, link_format, "Map All Points")
        except:
            pass

def executeParser(filePath, outputLoc):
    try:
        if parserAttr.checkValid(filePath):
            outData = parserAttr.runParser(filePath, outputLoc)
            parseData = [outData.appName, filePath, outData.appColorText]
            if outData.allApplicationPoints:
                pointsFromAll.append(outData.allApplicationPoints)
            parserRanList.append(parseData)
            writeOut(outData)
    except:
        pass


if __name__ == "__main__":
    commArg = argparse.ArgumentParser(description='This tool retrieves and organizes data from mobile phone mapping applications')
    commArg.add_argument('-i', action='store', dest='inputFolder', required=True, help='The folder root of your input')
    commArg.add_argument('-o', action='store', dest='outputFolder', default='.', help='Output folder, defaults to current folder')

    argResults = commArg.parse_args()
    inputLoc = argResults.inputFolder
    outputLoc = argResults.outputFolder
    extractedRoot = os.path.join(outputLoc, 'extracted')
    tempRoot = os.path.join(outputLoc, 'uncompressed')

    # make directories if needed
    if not os.path.isdir(outputLoc):
        os.makedirs(outputLoc)
    if not os.path.isdir(extractedRoot):
        os.makedirs(extractedRoot)

    newInput = False
    if not os.path.isdir(inputLoc):
        # will attempt to mount an image file or extract a tar file
        newInput = Mount.tryAllInputs(inputLoc, extractedRoot)
        if newInput:
            if newInput != inputLoc:
                inputLoc = extractedRoot

    # Generic xlsx file set up ------------------------------------------------
    workbook = xlsxwriter.Workbook(os.path.join(outputLoc,"GPSAppParse.xlsx"))
    parsersRan = workbook.add_worksheet("Parsers Ran")
    bold = workbook.add_format({'bold': True})
    link_format = workbook.add_format({'color': 'blue', 'underline': 1})
    #--------------------------------------------------------------------------
    progPath = os.path.split(os.path.abspath(__file__))[0]
    parserPathList = os.listdir(os.path.join(progPath, 'Parsers'))
    parserList = []
    # import all parsers for use ----------------------------------------------
    for parser in parserPathList:
        if parser[-3:] == '.py' and parser != '__init__.py':
            parserRoot = __import__('Parsers.' + parser[:-3])
            parserAttr = getattr(parserRoot, parser[:-3])
            parserList.append(parserAttr)

    # list to see which parsers were ran
    parserRanList = []
    # list containing points of all applications
    pointsFromAll = []
    # if single file
    if inputLoc == newInput:
        file = open(inputLoc, 'rb')
        for parserAttr in parserList:
            executeParser(inputLoc, outputLoc)
    # walk through input location to discover any files that are to be parsed -
    else:
        for subdir, dirs, files in os.walk(inputLoc):
            for file in files:
                filePath = os.path.join(subdir, file)
                file = open(filePath, 'rb')
                if FileCheck.checkAll(filePath, file):
                    for parserAttr in parserList:
                        executeParser(filePath, outputLoc)

    allAppsMapPath = ''
    if pointsFromAll:
        allAppsMapPath = allAppsMap(pointsFromAll)

    parsersRanSheet(parserRanList, allAppsMapPath)
    workbook.close()