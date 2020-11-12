# HTTP Server

## Team Members:

    Division 2
	Batch: T3
	111803157  Mrunal Kotkar
	111803168  Vrinda Ahuja
	
## Steps to run the project:

1. The main server file is **webserver.py**
2. Run **python3 webserver.py <port_no>**
3. For testing, three test files namely test1, test2 and test3 are present
4. For combined testing, run **python3 testing.py <port_no>**
5. Configuration file of the server is **config.py**
6. Log file of server is **access.log** and will get updated as you make new requests.
7. Snapshots of some cases of project are present in **Screenshots folder**
8. Way to stop and restart the server by typing *stop* and *restart* respectively.

## Project features:  

1. **HTTP Request Methods Implemented**:
- *GET* 
- *HEAD*
- *POST*
- *PUT*
- *DELETE*
2. **Config file**: Implemented configuration file with Document Root for some functionalities of server.
3. **Multithreading in server**: Implemented multithreading in server to run multiple requests simultaneously
4. **Logging**:
- *Levels of Logging* - Implemented INFO and ERROR levels of logging for the log file 
- *Folder (Logfiles)* - Compression of logfiles and moving them to a folder sequentially after a      particular time
5. **Automated Tests**: 
- *Test1* - Implemented different tests using multithreading and requests module 
- *Test2* - Implemented different tests for sample website using webbrowser module
- *Test3* - Implemented different tests using socket programming and threading by manually creating requests.
- *Testing* - Combined tests of all the three testfiles.
6. **Implemented Cookies and handled Persistent and non-Persistent connections**
