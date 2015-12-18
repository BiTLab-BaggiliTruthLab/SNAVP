from .Depedencies.WorksheetData import WorksheetData

import ccl_bplist
import datetime

UNIXTS = 978307200 # Needed to add to iOS timestamp to get correct date
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    # validity = validityCheck
    try:
        f = open(filePath, "rb")
        plist = ccl_bplist.load(f)
        indexes = []
        # Retrieves all indexes that hold the data we want
        for item in plist['$objects']:
            if 'NS.objects' in item:
                for elem in item['NS.objects']:
                    indexes.append(int(str(elem)[5:]))
        if indexes and filePath[-14:] == 'Historys.plist':
            # validity.run = validityCheck.PASS
            print("RUNNING BING IOS")
            print(filePath)
            return True
    except:
        return False
# -------------------------------------------------------------------------------------------------

def runParser(filePath, outputLoc):
    bing_iOS = WorksheetData()
    bing_iOS.appName = "Bing"
    bing_iOS.headers = ['Time', 'Searched Text', 'Directions Received', 'URL']
    bing_iOS.worksheetName = 'Bing_History'

    f = open(filePath, "rb")
    plist = ccl_bplist.load(f)

    indexes = []

    # Retrieves all indexes that hold the data we want
    for item in plist['$objects']:
        if 'NS.objects' in item:
            for elem in item['NS.objects']:
                indexes.append(int(str(elem)[5:]))

    # rowNum = 2
    titles = []

    for index in indexes:

        rowData = ['']*4
        # excelRow = 'A' + str(rowNum)

        title = int(str(plist['$objects'][index]['title'])[5:])
        time = int(str(plist['$objects'][index]['lastUsed'])[5:])
        url = int(str(plist['$objects'][index]['url'])[5:])

        rowData[0] = datetime.datetime.fromtimestamp(UNIXTS + plist['$objects'][time]['NS.time']).strftime('%Y-%m-%d %H:%M:%S')
        rowData[1] = plist['$objects'][title]

        # Determine if duplicate title, if so mark as directions received
        if int(str(plist['$objects'][index]['title'])[5:]) in titles:
            rowData[2] = "Yes"
        else:
            rowData[2] = "No"
        titles.append(int(str(plist['$objects'][index]['title'])[5:]))

        rowData[3] = plist['$objects'][url]

        bing_iOS.appData.append(rowData)
        # worksheet.write_row(excelRow, rowData)
        # rowNum += 1
    return bing_iOS
# workbook.close()