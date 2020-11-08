import webbrowser, os, sys
from socket import *
import requests
import http
import urllib

port = sys.argv[1]

IP = '127.0.0.1'

same_url_part = "http://" + 	IP + ":" + port 

def starttab(url = (same_url_part)):
    webbrowser.open_new_tab(url)

def main():
    starttab(same_url_part + "/website/demo.mp3")
    starttab(same_url_part + "/website/demo.mp4")
    starttab(same_url_part + "/index.html")
    starttab(same_url_part + "/website/login.html")
    starttab(same_url_part + "/website/demo.jpg")
    starttab(same_url_part + "/dummy.pdf")
    starttab(same_url_part + "/website/old.html")
    starttab(same_url_part + "/website/form.html")

if __name__ == "__main__":
    main()