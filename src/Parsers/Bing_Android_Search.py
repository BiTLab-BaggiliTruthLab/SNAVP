from .Depedencies.WorksheetData import WorksheetData
import sqlite3
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        conn = sqlite3.connect(filePath)
        c = conn.cursor()
        c.execute("SELECT _NAME, _LAST FROM SearchHistory")
        print("RUNNING BING ANDROID")
        print(filePath)
        return True
    except:
        pass
    return False
# messages ----------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):
    bingSearch = WorksheetData()
    bingSearch.appName = 'Bing_Search'
    bingSearch.worksheetName = 'Bing_Search'
    bingSearch.headers = ['Time', 'Search Text']

    conn = sqlite3.connect(filePath)
    c = conn.cursor()
    c.execute("SELECT _NAME, _LAST FROM SearchHistory")

    SEARCH_COL_IDX = 0
    TIME_COL_IDX = 1

    row = c.fetchone()
    while row:

        rowData = ['']*2

        if row[TIME_COL_IDX]:
            rowData[0] = row[TIME_COL_IDX]
        if row[SEARCH_COL_IDX]:
            rowData[1] = (row[SEARCH_COL_IDX])

        bingSearch.appData.append(rowData)

        row = c.fetchone()

    return bingSearch