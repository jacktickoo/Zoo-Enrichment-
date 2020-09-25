import gspread
import csv
import sys
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import http.client as httplib

sys.excepthook = sys.__excepthook__

class Logger:
    
    def __init__(self):
        # TODO change sheet names!
        # Name of the Google Sheets document
        self.DOCNAME = "DOC_NAME"
        # These are the two worksheets that are used
        self.LOGSHEET = "LOG_SHEET"
        self.ALIVESHEET = "ALIVE_SHEET"
        # The actual connection instances (set by self.sheet())
        self.sheet = None
        self.alive = None

        self.tempdata = []
        self.prev_log_time = datetime.now()

        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	# TODO needs client secret for API
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        self.client = gspread.authorize(self.creds)§
        self.client.login()

        self.sheets()
        
        # reset sheet rows if empty (since rows are appended and default sheet already has empty rows)
        if 1 == len(self.sheet.get_all_values()):
            self.sheet.resize(rows=1)
            
    def internet_connected(self):
        # Try to connect to Google to see if there is internet
        conn = httplib.HTTPConnection("www.google.fi", timeout=2)
        try:
            conn.request("HEAD", "/")
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(e)
            return False
            
    def log_local(self, data):
        # add data to tempdata to wait uploading to google sheets and write to local csv
        self.tempdata.append(data)
        with open('log.csv', 'a', newline='') as logfile:
            logwriter = csv.writer(logfile, delimiter=',')
            logwriter.writerow(data)

    def sheets(self):
        # Login and connect to the sheets if not already connected
        if not self.creds.access_token_expired and self.sheet and self.alive:
            print('All good already')
            return
        if self.creds.access_token_expired:
            self.client.login()

        self.sheet = self.client.open(self.DOCNAME).worksheet(self.LOGSHEET)
        self.alive = self.client.open(self.DOCNAME).worksheet(self.ALIVESHEET)
    
    def log_drive(self, time):       
        diff = (time - self.prev_log_time).total_seconds()
        # Log online every two seconds
        log_interval = 2
        if diff >= log_interval:

            # If there is no internet connection only log locally
            if not self.internet_connected():
                # This row should be useless. Can't debug now so if something breaks 
                # try uncommenting? 
                #self.prev_log_time = time + timedelta(0, 120)
                with open('logfail.csv', 'a', newline='') as logfile:
                    logwriter = csv.writer(logfile, delimiter=',')
                    logwriter.writerow(['Logging to Google Drive failed: no Internet connection', time.strftime("%Y-%m-%d %H:%M:%S")])
                return
            
            # The number of rows to be logged at once was determined 
            # by the log_interval, frequency of sensor readings, and/or Google API quota.
            # Thus might require tweaking if something changes!
            nof_rows = int(log_interval + log_interval / 2)
            #print(nof_rows)
            try:
                #print('Data to be logged before:', len(self.tempdata) )
                self.sheets()
                for row in self.tempdata[0:nof_rows]:
                    self.sheet.append_row(row)
                self.tempdata = self.tempdata[nof_rows:]
                self.prev_log_time = time
                #print('Data to be logged after:', len(self.tempdata) )
            except Exception as e: 
                print('Logging to Google Drive failed at', time)
                print('Exception {}'.format(type(e).__name__))
                # Failures to connect/write to the Google sheet are logged in logfail.csv
                with open('logfail.csv', 'a', newline='') as logfile:
                    logwriter = csv.writer(logfile, delimiter=',')
                    logwriter.writerow(['Logging to Google Drive failed: {}'.format(type(e).__name__), time.strftime("%Y-%m-%d %H:%M:%S")])

        
    def log_alive(self):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.sheets()
            print('Try to insert')
            self.alive.insert_row([time])
            print('Insert successful')
        except TypeError as e:
            print('Error logging alive: weird buffering error:', e)
        except:
            print('Error logging alive: something else')
        
    def get_all(self):
        return self.sheet.get_all_values()
