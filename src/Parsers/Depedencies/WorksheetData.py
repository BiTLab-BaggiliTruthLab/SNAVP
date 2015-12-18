class WorksheetData(object):

    def __init__(self):
        self.appData = [] # each row of data is a list within appData
        self.appName = '' # name of Application
        self.worksheetName = '' # name of worksheet in Excel file
        self.headers = [] # header labels for Excel column
        self.pointMapPaths = [] # to store path to map of single Excel line
        self.allCoordinatesPath = '' # to store path to all points map
        self.mapsPlotted = False # set to true if drawing maps
        self.appColor = '#FFFFFF' # app color for map points, defaulted to white, http://www.computerhope.com/htmcolor.htm for list of colors
        self.appColorText = 'NA' # plain text for app color
        self.allApplicationPoints = [] # list to store all points for map of all applications
