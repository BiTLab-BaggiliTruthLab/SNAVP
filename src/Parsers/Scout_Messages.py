from .Depedencies.WorksheetData import WorksheetData
import sqlite3
import json
import datetime

sqlquery = '''   SELECT publish_utc_timestamp,
                           publisher_user_id,
                           message_data,
                           message_meta_notify_type,
                           chatSessionStore.data,
                           userStore.data,
                           meetUpStore.data
                    FROM message_table
                        LEFT JOIN userStore
                            ON userStore.id = publisher_user_id
                        LEFT JOIN chatSessionStore
                            ON chatSessionStore.id = channel_id
                        LEFT JOIN meetUpStore
                            ON meetUpStore.id = message_meta_meetupid'''
# -------------------------------------------------------------------------------------------------
def checkValid(filePath):
    try:
        conn = sqlite3.connect(filePath)
        c = conn.cursor()
        c.execute(sqlquery)
        print("RUNNING SCOUT MESSAGES")
        print(filePath)
        return True
    except:
        pass
    return False
# messages ----------------------------------------------------------------------------------------
def runParser(filePath, outputLoc):
    scoutMessage = WorksheetData()
    scoutMessage.appName = 'Scout_Messages'
    scoutMessage.worksheetName = 'Scout_Messages'
    scoutMessage.headers = ['Time', 'Type', 'Participants', 'To', 'From', 'Message', 'Meet Up Name', 'Meet Up Creation Time', 'Meet Up Time', 'Meet Up Location']

    conn = sqlite3.connect(filePath)
    c = conn.cursor()
    c.execute(sqlquery)

    TIME_COL_IDX = 0
    FROM_COL_IDX = 1
    MESSAGE_COL_IDX = 2
    TYPE_COL_IDX = 3
    PARTICIPANTS_COL_IDX = 4
    NAME_COL_IDX = 5
    MEETUP_COL_IDX = 6

    userNames = {}  # for user id to name conversions

    row = c.fetchone()
    while row:

        rowData = ['']*10

        if row[TIME_COL_IDX]:
            rowData[0] = datetime.datetime.fromtimestamp(row[TIME_COL_IDX]/1000).strftime('%Y-%m-%d %H:%M:%S')
        if row[TYPE_COL_IDX]:
            rowData[1] = (row[TYPE_COL_IDX])
        if row[PARTICIPANTS_COL_IDX]:
            decodedData = json.loads(row[PARTICIPANTS_COL_IDX].decode("UTF-8"))
            party = decodedData["members"]

        if row[NAME_COL_IDX]:
            decodedName = json.loads(row[NAME_COL_IDX].decode("UTF-8"))
            name = decodedName["user_firstName"] + " " + decodedName["user_LastName"]
            userNames[row[FROM_COL_IDX]] = name
            for idx, val in enumerate(party):
                if val in userNames:
                    party[idx] = userNames[val]
            rowData[4] = userNames[row[FROM_COL_IDX]]
        if row[MESSAGE_COL_IDX]:
            decodedMessage = json.loads(row[MESSAGE_COL_IDX])
            if row[TYPE_COL_IDX] == "meetup_invite":
                rowData[9] = decodedMessage["notification_data"]["meetup_data"]["entity"]
            elif row[TYPE_COL_IDX] == "chat_receive":
                rowData[5] = decodedMessage["text_data"]
        if row[MEETUP_COL_IDX]:
            decodedMeetUp = json.loads(row[MEETUP_COL_IDX].decode("UTF-8"))
            rowData[7] = datetime.datetime.fromtimestamp(decodedMeetUp["created_time"]/1000).strftime('%Y-%m-%d %H:%M:%S')
            rowData[6] = decodedMeetUp["meetup_name"]
            rowData[8] = datetime.datetime.fromtimestamp(decodedMeetUp["meetup_time"]/1000).strftime('%Y-%m-%d %H:%M:%S')


        rowData[2] = ", ".join(party)  # convert party to string for display
        if rowData[4] in party:
            party.remove(rowData[4]) # remove the sender from participants to determine to
        rowData[3] = ", ".join(party)

        scoutMessage.appData.append(rowData)

        row = c.fetchone()

    return scoutMessage