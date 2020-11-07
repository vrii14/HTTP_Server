import os

'''
    Thread Request Timeout Time in seconds
'''
TIMEOUT = 50

'''
    Maximum Thread requests to the server
'''
MAX_REQUESTS = 50

'''
    Maximum URI length of the request
'''
MAX_URI_LENGTH = 80

'''
    Document Root of the server
'''
ROOT = os.getcwd()

'''
    Request URI which has moved permanently to a new URI
'''
REDIRECTED_PAGE = ROOT + "/website/old.html"

'''
    New URI for the redirection
'''
NEW_URI = ROOT + "/website/new.html"

'''
    Logfile location and name
'''
LOGFILE = ROOT + "/access.log"

'''
    Directory for moving expired compressed log files 
'''
LOG_DIRECTORY = ROOT + "/logFiles"

'''
    Expiry time for logfile    
'''
LOGFILE_TIME = 86400

favicon = "/favicon.ico"
FAVICON = ROOT + favicon

'''
    Cookie header details
'''
COOKIE = 'Set-Cookie: id='
MAXAGE = '; max-age=60'
COOKIE_IDS = ['abcd', '1234', 'user', 'cook', 'mrun', 'vrii', 'wxyz']