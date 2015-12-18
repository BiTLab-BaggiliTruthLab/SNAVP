# sqlite header
def sqliteTest(filePath, file):
    file.seek(0)
    header = file.read(13)
    return header == b'SQLite format'

# bplist header
def bplistTest(filePath, file):
    # result = filePath[-6:] == '.plist'
    # if result:
    file.seek(0)
    header = file.read(8)
    result = header == b'bplist00'
    return result

def xmlTest(filePath, file):
    return filePath[-4:] == '.xml'

def wazeLogTest(filePath, file):
    return filePath[-12:] == 'waze_log.txt'

def checkAll(filePath, file):
    if sqliteTest(filePath, file) or bplistTest(filePath, file) or xmlTest(filePath, file) or wazeLogTest(filePath, file):
        return True
    return False