#!/usr/bin/python
import socket 
from socket import *
import sys	#handling arguments
import datetime #converting dates to different formats for headers
import os	#file operations
import os.path	
import time		#if modified since header
import logging	#log file
from threading import Thread #multithreading
from config import *	#config file
import base64
import random	#random values for cookies and retry after
from urllib.parse import *	
import gzip		#compressing the log files
import shutil
from datetime import timedelta  #request timed out
import threading

months = {'1':'Jan', '2':'Feb', '3':'Mar', '4':'Apr','5':'May','6':'Jun',
		'7':'Jul','8':'Aug','9':'Sep','10':'Oct','11':'Nov','12':'Dec'}

months_to_numbers = {'Jan':'1', 'Feb':'2', 'Mar':'3','Apr':'4','May':'5','Jun':'6',
					'Jul':'7','Aug':'8','Sep':'9','Oct':'10','Nov':'11','Dec':'12'}

status_codes = {200:'OK', 201: 'Created', 204: 'No Content', 301: 'Moved Permanently',304: 'Not Modified',
				400:'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404:'Not Found', 408: 'Request Timeout',
				411: 'Length Required', 413: 'Payload Too Large', 414: 'URI Too Long', 
				415: 'Unsupported Media Type', 500: 'Internal Server Error', 501:'Not Implemented', 
				503: 'Service Unavailable',	505:'HTTP Version not Supported'	
}

content_types ={
	'html': 'text/html', 'txt': 'text/plain', 'pdf': 'application/pdf', 'mp3': 'audio/mpeg',
	'jpg': 'image/jpeg', 'png': 'image/png', 'csv': 'text/csv', 'mp4': 'video/mp4'
}

direct_extensions = ['jpg', 'jpeg', 'png', 'mp3', 'mp4', 'pdf']

versions = ['1.1', '1.0']

serverSocket = socket(AF_INET,SOCK_STREAM)
s = socket(AF_INET, SOCK_DGRAM)

def findip():
	try:
		s.connect(('8.8.8.8', 8000))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	s.close()
	return IP

ip = str(findip())

#logfile compression after 1 day
if(os.path.isfile(LOGFILE)):
	ct = time.ctime(os.path.getctime(LOGFILE))
	st=os.stat(LOGFILE)    
	mtime=st.st_mtime
	age = time.time() - mtime
	if(int(age) > LOGFILE_TIME):
		if(os.path.isdir(LOG_DIRECTORY)):
			with open(LOGFILE, 'rb') as f_in:
				number = len(os.listdir(LOG_DIRECTORY)) +1
				logfile_compress = LOG_DIRECTORY + f"/logfile{number}.gz"
				with gzip.open(logfile_compress, 'wb') as f_out:
					shutil.copyfileobj(f_in, f_out)
			os.remove(LOGFILE)
		else:
			os.mkdir(LOG_DIRECTORY)
			with open(LOGFILE, 'rb') as f_in:
				logfile_compress = LOG_DIRECTORY + "/logfile1.gz"
				with gzip.open(logfile_compress, 'wb') as f_out:
					shutil.copyfileobj(f_in, f_out)
			os.remove(LOGFILE)


logging.basicConfig(filename=LOGFILE, format='[%(asctime)s]: %(message)s', level=logging.DEBUG)
host_address = ip

class HTTPRequest:
	def __init__(self, data):
		self.method = None
		self.uri = None
		self.http_version = '1.1' # default to HTTP/1.1 if request doesn't provide a version
		self.headers = {} # a dictionary for headers
		self.server = 'Apache/2.4.41 (Ubuntu)' #default server apache
		self.user_data = None #for form data 
		self.language = 'en-US,en;q=0.9' 
		self.encoding = None
		self.request_line = None
		self.if_modified = None #if-modified-since header
		self.cookie = None 
		self.content_length = None # for status code 411 Length required
		self.authorization = None
		self.handle_request(data)


	def handle_request(self, request):
		lines = request.split('\r\n')
		# print(lines)
		request_headers = {}

		if_modified_since_substring = "If-Modified-Since"
		if any(if_modified_since_substring in line for line in lines):
			if_modified_header = [s for s in lines if if_modified_since_substring in s]
			if_modified_header = " ".join(if_modified_header)
			if_modified_header = if_modified_header.replace(if_modified_since_substring, "")
			self.if_modified = if_modified_header
		
		if len(lines) > 2 :
			for line in lines[1:]:
				header = line.split(':')
				request_headers[header[0]] = header[1]
			
			self.server = request_headers['User-Agent']
			if('Accept-Language' in request_headers.keys()):
				self.language = request_headers['Accept-Language']
			if('Cookie' in request_headers.keys()):
				self.cookie = request_headers['Cookie']
			if('Content-Length' in request_headers.keys()):
				self.content_length = request_headers['Content-Length'][1:]
			if('Authorization' in request_headers.keys()):
				self.authorization = request_headers['Authorization'][1:]
			self.encoding = request_headers['Accept-Encoding']

		self.request_line = lines[0]
		request_line_copy = self.request_line
		words = request_line_copy.split(' ')
		
		self.method = words[0]
		self.uri = words[1]
				
		if(self.method == 'POST' or self.method == 'PUT'):
			self.user_data = lines[-1]
			# print(lines)

		if len(words) > 2:
        		self.http_version = words[2]
	
		
'''
	Args:
		date_time(str) of last modified file
	Returns:
		parsed date_time(str) for the Last Modified header response
'''
def parse_modified_date(s):
	form = s.split(' ')
	modified_date = form[0]
	modified_date += ","
	modified_date += form[2]
	modified_date += " "
	modified_date += form[1]
	modified_date += " "
	modified_date += form[4]
	modified_date += " "
	modified_date += form[3]
	modified_date += " GMT"
	return modified_date

'''
	Args:
		None
	Returns:
		Parsed current date-time(str) for the Date header response
'''
def parse_date_time():
	day = datetime.datetime.today().strftime("%A")
	day = day[:3]
	now = datetime.datetime.now()
	month = months[now.strftime("%m")]
	string = day
	string += ", "
	string += now.strftime("%d ")
	string += month
	string += now.strftime(" %Y %H:%M:%S")
	string += " GMT\n"
	return string

'''
	Args:
		status_code(int) of the request recieved by the server
		file_name(str) 
		method(str) GET/HEAD for returning the response accordingly
		server(str) 
		language(str), encoding, cookie_flag(int)
	Returns:
		Response of the request recieved(str)
'''
def get_headers(status_code, file_name, method, server, language, encoding, cookie_flag, version):
	
	ToSend = f"HTTP/{version} {status_code} {status_codes[status_code]}\nDate: "
	date_time = parse_date_time()
	ToSend += date_time
	ToSend += "Server: "
	ToSend += "Apache/2.4.41 (Ubuntu)"
	ToSend += "\r\nLast_Modified: "
	s = time.ctime(os.path.getmtime(file_name))
	last_modified = parse_modified_date(s)
	ToSend += last_modified
	if(status_code == 501):
		ToSend += "\nAllow: HEAD,GET, POST, PUT, DELETE"
	file_name_copy = file_name
	spl = file_name_copy.split('.')
	extension = spl[1]
	if(extension in direct_extensions):
		f = open(file_name, "rb")
		text = f.read()
	else:
		f = open(file_name)
		text = f.read()
	ToSend += "\n"
	ToSend += "Accept-Ranges: bytes"
	if(method != 'POST'):
		ToSend += "\nContent-Language: "
		ToSend += language
	content_type = get_content_type(file_name, method)
	ToSend += "\nContent-Type: "
	ToSend += content_type
	ToSend += "\nContent-Length: "
	ToSend += str(len(text))
	if(cookie_flag == 0):
		n = len(COOKIE_IDS)-1
		index = random.randint(0, n) 
		ToSend += f"\n{COOKIE}{COOKIE_IDS[index]}{MAXAGE}"
	if(status_code == 408):
		ToSend += "\nConnection:close\n\n"
	else:
		ToSend += "\nConnection: keep-alive\n\n"
	if(extension not in direct_extensions):
		if(method != "HEAD"):
			if(status_code != 304):
				ToSend += text
				return ToSend
			else:
				return ToSend
		else:
			return ToSend
	else:
		if(method != "HEAD"):
			if(status_code != 304):
				return ToSend,text
			else:
				return ToSend
		else:
			return ToSend
	
# returns the content type of a file
def get_content_type(file_name, method):
	if(len(file_name) == 0):
		content_type = 'text/html'
		return content_type
	spl = file_name.split('.')
	extension = spl[1]
	content_type = content_types[extension]
	return content_type

#authorization credentials for delete request
def authorization(credentials):
	cred_list = credentials.split(' ')
	auth_type = cred_list[0]
	cred_list = base64.decodebytes(cred_list[1].encode()).decode()
	username = cred_list.split(':')[0]
	password = cred_list.split(':')[1]
	if(username == USERNAME and password == PASSWORD):
		return True
	return False
	


# Response of delete requests
def delete_headers(status_code, file_name, method, server, cookie_flag, version):
	ToSend = f"HTTP/{version} {status_code} {status_codes[status_code]}\nDate: "
	date_time = parse_date_time()
	ToSend += date_time
	os.remove(file_name)
	if(cookie_flag == 0):
		n = len(COOKIE_IDS)-1
		index = random.randint(0, n) 
		ToSend += f"{COOKIE}{COOKIE_IDS[index]}{MAXAGE}\n"
	fd = open("delete.html")
	text = fd.read()
	ToSend += "\n" 
	ToSend += text
	ToSend += "\n"
	return ToSend

# Checking if-modified-since condition for a file
def if_modified_since(header_day, file_name):
	header_day = header_day[1:]
	header_day = header_day.split(' ')
	day = int(header_day[2])
	month = header_day[3]
	month_number = months_to_numbers[month]
	month_number = int(month_number)
	year = int(header_day[4])
	time_list = header_day[5].split(':')
	time_list[0], time_list[1], time_list[2] = int(time_list[0]), int(time_list[1]), int(time_list[2])
	datetime_req = datetime.datetime(year, month_number, day, time_list[0], time_list[1], time_list[2])
	hsec = int(time.mktime(datetime_req.timetuple()))
	fsec = int(os.path.getmtime(file_name))
	if(hsec<fsec):
		status_code = 200
	else:
		status_code = 304
	return status_code

# Response for put requests
def put_headers(connectionSocket, status_code, file_name, file_data, f_flag, cookie_flag, content_length, version):
	ToSend = f"HTTP/{version} {status_code} {status_codes[status_code]}\nDate: "
	date_time = parse_date_time()
	ToSend += date_time
	ToSend += "Server: Apache/2.4.41 (Ubuntu)\n"
	content_type = get_content_type(file_name, "PUT")
	ToSend += "Content-Type: "
	ToSend += content_type
	ToSend += "\nContent-Location: /"
	filedata = b""
	file_name = file_name[1:]
	ToSend += file_name

	if f_flag == 0:
		with open(file_name, 'w') as fp:
			fp.write(file_data)
		fp.close()

	else:
		if content_length:
			length = content_length
			q = int(int(length) // 8192)
			r = int(length) % 8192

			try:
				filedata = filedata + file_data
			except TypeError:
				file_data = file_data.encode()
				filedata = filedata + file_data	

			i = len(file_data)
			size = int(length) - i

			while size > 0:
				file_data = connectionSocket.recv(8192)
				try:
					filedata = filedata + file_data
				except TypeError:
					file_data = file_data.encode()
					filedata = filedata + file_data
				size = size - len(file_data)

			fp = open(file_name, "wb")
			fp.write(filedata)
			fp.close()

		if(cookie_flag == 0):
			n = len(COOKIE_IDS)-1
			index = random.randint(0, n) 
			ToSend += f"\n{COOKIE}{COOKIE_IDS[index]}{MAXAGE}"

	ToSend += "\nConnection:close\n\n"
	return ToSend



'''
	Args:
		post_data(str) The form data filled by the user in a POST request
	Returns:
		None
		parses the form data and prints it(later transfer it to log file)
'''
def print_post_data(post_data):
	lines = post_data.split('&')
	string = ""
	for line in lines:
		line = line.replace('=', ': ')
		line = line.replace('+', ' ')
		line = line.replace('%40', '@')
		string += line
		string += "\n"
	logging.info(f"{host_address}: POST Data: \n{string} ")

# getting file length for logfile
def get_file_length(file_name):
	spl = file_name.split('.')
	extension = spl[1]
	if(extension not in direct_extensions):
		f = open(file_name, 'r')
	else:
		f = open(file_name, 'rb')
	data = f.read()
	length = len(data)
	return length

# Client thread to recieve HTTP request and return a response
def clientfun(connectionSocket, serverPort, addr):

	filedata = b""
	conn = True
	thread = []
	while conn:
		try:
			sentence = connectionSocket.recv(8192)
			try:
				sentence = sentence.decode('utf-8')
				req_list = sentence.split('\r\n\r\n')
				f_flag = 0
			except UnicodeDecodeError:
				req_list = sentence.split(b'\r\n\r\n')
				req_list[0] = req_list[0].decode(errors = 'ignore')
				request = HTTPRequest(req_list[0])
				f_flag = 1
						
			if(f_flag == 0):
				sentence = req_list[0]
				if req_list[-1] == '\r\n':
					sentence += "\r\n"
				
				if len(req_list)>1:
					ent_body = req_list[1]
					# print(ent_body)
				request = HTTPRequest(sentence)
				
			if(f_flag == 1):
				ent_body = req_list[1]
				
			start_time = datetime.datetime.now()
			thread.append(connectionSocket)
			version = request.http_version.split('/')[1]

			try:
				cookie_flag = 0
				if(request.cookie != None):
					cookie_flag = 1

				if(len(thread)>1):
					
					diff = end_time - start_time
					minutes = diff / timedelta(minutes=1)
					if(abs(minutes) > 0.3):
						status_code = 408
						file_name = "408_error.html"
						ToSend = get_headers(status_code, file_name, request.method, request.server, request.language, request.encoding, cookie_flag, version)
						connectionSocket.send(ToSend.encode())
						file_length = get_file_length(file_name)
						logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")
						connectionSocket.close()
				
				
				if version not in versions:
					status_code = 505
					ToSend = f"{status_code} {status_codes[status_code]}\n\n"
					connectionSocket.send(ToSend.encode())
					logging.info(f"{host_address}: \"{request.request_line}\" {status_code} \"{request.server}\"\n")
					logging.error(f"{host_address}: [client {addr}] HTTP Version not Supported in Request {request.request_line} \n")

				else:	
					if(request.method == 'GET' or request.method == 'HEAD' or request.method == 'POST'):
						try:
							if('/' in request.uri):
								
								if((len(request.uri) - MAX_URI_LENGTH)<0):						
									PATH = os.getcwd()
									PATH += request.uri
									
									#redirection
									if(PATH == REDIRECTED_PAGE):
										status_code = 301
										logging.info(f"{host_address}: \"{request.request_line}\" {status_code} \"{request.server}\"\n")
										ToSend = f"HTTP/{version} {status_code} {status_codes[status_code]}\n"
										ToSend += f"Location: http://127.0.0.1:{serverPort}/website/new.html \n"										
										connectionSocket.send(ToSend.encode())

									else:
										if(os.path.isfile(PATH) or (request.uri == '/')):
											if(os.access(PATH, os.R_OK) and os.access(PATH, os.W_OK)):		
												#success
												status_code = 200
												file_name = request.uri.strip('/')
												if request.uri == '/':
													file_name = "index.html"
												spl = file_name.split('.')
												extension = spl[1]

												if(request.if_modified != None):
													status_code = if_modified_since(request.if_modified, file_name)

												if(request.method == "POST"):
													# print_post_data(request.user_data)
													print_post_data(ent_body)

												if(content_types.get(extension) == None):
													status_code = 415
													file_name = "415_error.html"
													ToSend = f"HTTP/{version} {status_code} {status_codes[status_code]} \n"
													ToSend += "Connection:close\n\n"
													# ToSend += "<h1> Unsupported Media Type </h1>"
													fr = open(file_name, 'r')
													data = fr.read()
													ToSend += data
													connectionSocket.send(ToSend.encode())
													

												else:
													#other than html and txt
													if(extension in direct_extensions):
														if(request.method != "HEAD"):
															# modified
															if(status_code != 304):
																ToSend, data = get_headers(status_code, file_name, request.method, request.server, request.language, request.encoding, cookie_flag, version)
																connectionSocket.send(ToSend.encode())
																connectionSocket.send(data)
															else:
																ToSend = get_headers(status_code, file_name, request.method, request.server, request.language, request.encoding, cookie_flag, version)
																connectionSocket.send(ToSend.encode())																
														else:
															ToSend = get_headers(status_code, file_name, request.method, request.server, request.language, request.encoding, cookie_flag, version)
															connectionSocket.send(ToSend.encode())													
													#html files
													else:
														ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
														connectionSocket.send(ToSend.encode())

											else:
												#forbidden file
												status_code = 403
												file_name = "403_error.html"	
												ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
												connectionSocket.send(ToSend.encode())
										else:
											#file not found
											status_code = 404
											file_name = "404_error.html"
											ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
											connectionSocket.send(ToSend.encode())
								else:
									#URI too long
									status_code = 414
									file_name = "414_error.html"
									ToSend = get_headers(status_code, file_name, request.method, request.server, request.language, request.encoding, cookie_flag, version)
									connectionSocket.send(ToSend.encode())
							
							file_length = get_file_length(file_name)
							logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")

						except:					
							#Bad request
							status_code = 400
							file_name = "400_error.html"
							ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)	
							connectionSocket.send(ToSend.encode())

							file_length = get_file_length(file_name)
							logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")


					elif(request.method == "DELETE"):
						try:
							if('/' in request.uri):
								if(len(request.uri) < MAX_URI_LENGTH):
									PATH = os.getcwd()
									PATH += request.uri
									if(os.path.isfile(PATH)):
										if(os.access(PATH, os.R_OK) and os.access(PATH, os.W_OK)):
											file_name = request.uri.strip('/')
											spl = file_name.split('.')
											extension = spl[1]
											
											if extension in direct_extensions:
												f = open(file_name, 'rb')
											else:
												f = open(file_name, 'r')
											text = f.read()
											file_length = get_file_length(file_name)
											
											#if user is authorized
											if(authorization(request.authorization)):
												if(int(len(text)) == 0):
													# No Content
													status_code = 204
													ToSend = f"HTTP/{version} {status_code} {status_codes[status_code]}\n\n"
													os.remove(file_name)
													connectionSocket.send(ToSend.encode())				
												else:
													#success
													status_code = 200
													ToSend = delete_headers(status_code, file_name, request.method, request.server, cookie_flag, version)
													connectionSocket.send(ToSend.encode())
											#user not authorized
											else:
												status_code = 401
												ToSend = f"HTTP/{version} {status_code} {status_codes[status_code]}\nDate:"
												date_time = parse_date_time()
												ToSend += date_time
												ToSend += "WWW-Authenticate: Basic realm=\"Access to staging site\", charset=\"UTF-8\""
												connectionSocket.send(ToSend.encode())		

										else:
											#forbidden file
											status_code = 403
											file_name = "403_error.html"	
											file_length = get_file_length(file_name)

											ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
											connectionSocket.send(ToSend.encode())

									else:									
										#file not found
										status_code = 404
										file_name = "404_error.html"
										file_length = get_file_length(file_name)

										ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
										connectionSocket.send(ToSend.encode())
								
								else:
									#URI too long
									status_code = 414
									file_name = "414_error.html"
									file_length = get_file_length(file_name)

									ToSend = get_headers(status_code, file_name, request.method, request.server, request.language, request.encoding, cookie_flag, version)

									connectionSocket.send(ToSend.encode())
							
							logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")
							connectionSocket.close()
					
						except:
							#Bad request
							# print("except")
							status_code = 400
							file_name = "400_error.html"
							ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)			
							connectionSocket.send(ToSend.encode())

							file_length = get_file_length(file_name)
							logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")

					
					elif(request.method == "PUT"):

						try:
							if('/' in request.uri):
								if(len(request.uri) < MAX_URI_LENGTH):

									PATH = os.getcwd()
									PATH += request.uri
									data = request.user_data
									file_name = request.uri.strip('/')

									if(request.content_length != None):										
										if(int(request.content_length) < MAX_PAYLOAD):
											if(os.path.isfile(PATH)):
												if(os.access(PATH, os.R_OK) and os.access(PATH, os.W_OK)):
													#success
													status_code = 200
													os.remove(file_name)
													ToSend = put_headers(connectionSocket, status_code, request.uri, ent_body, f_flag, cookie_flag, request.content_length, version)
													connectionSocket.send(ToSend.encode())

												else:
													#forbidden file
													status_code = 403
													file_name = "403_error.html"
													ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
													connectionSocket.send(ToSend.encode())
											
											else:
												#new file created
												status_code = 201
												ToSend = put_headers(connectionSocket, status_code, request.uri, ent_body, f_flag, cookie_flag, request.content_length, version)
												connectionSocket.send(ToSend.encode())
										else:
											#payload too large
											status_code = 413
											file_name = "413_error.html"
											ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
											connectionSocket.send(ToSend.encode())
									else:
										#length required
										status_code = 411
										file_name = "411_error.html"
										ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
										connectionSocket.send(ToSend.encode())
										
								else:
									#URI too long
									status_code = 414
									file_name = "414_error.html"
									ToSend = get_headers(status_code, file_name, request.method, request.server, request.language, request.encoding, cookie_flag, version)
									connectionSocket.send(ToSend.encode())
									file_length = get_file_length(file_name)
									logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")
								

								file_length = get_file_length(file_name)
								logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")
								# print("logging")

						except:
							#Bad request
							status_code = 400
							file_name = "400_error.html"
							ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)			
							connectionSocket.send(ToSend.encode())
							
							file_length = get_file_length(file_name)
							logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")

						connectionSocket.close()
			
					else:

						status_code = 501
						file_name = "501_error.html"
						ToSend = get_headers(status_code, file_name, request.method, request.server,  request.language, request.encoding, cookie_flag, version)
						connectionSocket.send(ToSend.encode())

						file_length = get_file_length(file_name)
						logging.info(f"{host_address}: \"{request.request_line}\" {status_code} {file_length} \"{request.server}\"\n")
						logging.error(f"{host_address}: [client {addr}] Invalid method in request {request.request_line} \n")

				if(version == '1.0'):
					connectionSocket.close()

			except:
				status_code = 500
				ToSend = f"HTTP/1.1 {status_code} {status_codes[status_code]}\n"
				connectionSocket.send(ToSend.encode())

				logging.info(f"{host_address}: {status_code} \n")
				logging.error(f"{host_address}: [client {addr}] Internal Server Error in request\n")

		except:
			
			conn = False
		
		end_time = datetime.datetime.now()

lthread = []

# Utility to stop and restart server
def take_input():
	while True:
		string = input()
		string = string.lower()
		if(string == "stop"):
			print("Server stopped")
			serverSocket.close()
			os._exit(os.EX_OK)
			break
		elif(string == 'restart'):
			lthread = []
			print("Server is restarting...")
			serverSocket.close()

#Main function
def main():			
	serverPort = int(sys.argv[1])
	serverSocket = socket(AF_INET,SOCK_STREAM)
	serverSocket.bind(('',serverPort))
	serverSocket.listen(5)
	print(f'The server is ready to receive on http://127.0.0.1:{serverPort}')
	input_thread = Thread(target=take_input)
	input_thread.start()
		
	while True:
		connectionSocket, addr = serverSocket.accept()
		lthread.append(connectionSocket)
		print("Connected by: ", addr)
		
		if(threading.active_count()<MAX_REQUESTS):
			th = Thread(target=clientfun, args=(connectionSocket,serverPort, addr))
			th.start()
		else:
			status_code = 503
			random_time = random.randint(100, 500)

			ToSend = f"HTTP/1.1 {status_code} {status_codes[status_code]} \n"
			ToSend += f"Retry After: {random_time}"
			ToSend += "\nConnection:close\n\n"

			connectionSocket.send(ToSend.encode())
			logging.error(f"{host_address}: {status_code}: [client {addr}] Service Unavailable for request.\n")
			connectionSocket.close()
			break

if __name__ == "__main__":
	main()