from .Depedencies.WorksheetData import WorksheetData
import ccl_bplist
import re

# list of the state abbreviations for regEx purposes
STATEABBR = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'ND', 'NC', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
COUNTRIES = ['United States']
rows = []
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        f = open(filePath, "rb")
        plist = ccl_bplist.load(f)
        if plist['MSPHistory']:
            print("RUNNING APPLE MAPS")
            print(filePath)
            return True

    except:
        pass
    return False
# -------------------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):

    apple_maps = WorksheetData()
    apple_maps.appName = "Apple_Maps"
    apple_maps.worksheetName = "Apple_Maps_GeoHistory"
    apple_maps.headers = ['Street', 'State', 'Zip', 'Country']

    f = open(filePath, "rb")
    plist = ccl_bplist.load(f)

    results = []
    count  = 0
    for item in plist['MSPHistory']:
        decoded_results = item.decode('utf-8', 'ignore')
        if count == 0:
            if "yelp" in decoded_results:
                results.append(decoded_results.partition("com")[0])
            else:
                results.append(decoded_results)
        elif "yelp" in decoded_results:
            results.append(decoded_results.partition("com")[0])
        else:
            try:
                if "yelp" not in plist['MSPHistory'][count - 1].decode('utf-8', 'ignore'):
                    results.append(decoded_results)
            except:
                continue
        count += 1

    for elem in results:
        rowData = ['']*4

        elem = re.sub(r'\$\S+', '', elem)
        elem = re.sub(r'\D\@\S+', '', elem)
        elem = re.sub(r'\\x.{0,2}', ' ', elem)

        streetAddress = re.search(r"(\d{1,5}(\ 1\/[234])?(\x20[A-Z]([a-z])+)+.?,? )", elem)
        if streetAddress:
            rowData[0] = streetAddress.group(1)

        stateAbb = re.search(r'\b(' + '|'.join(STATEABBR) + r')\b', elem)
        if stateAbb:
            rowData[1] = stateAbb.group(1)

        areaCode = re.search(r'(\d{5})', elem)
        if areaCode:
            rowData[2] = areaCode.group(1)

        countryLoc = re.search(r'\b(' + '|'.join(COUNTRIES) + r')\b', elem)
        if countryLoc:
            rowData[3] = countryLoc.group(1)

        apple_maps.appData.append(rowData)

    return apple_maps

