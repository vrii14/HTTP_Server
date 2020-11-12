#!/usr/bin/python
from socket import *
import sys
import threading
import time

serverName = '127.0.0.1'
serverPort = int(sys.argv[1])


def get_request():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    request = "GET /index.html HTTP/1.1"
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)
    print('---GET /index.html HTTP/1.1---\n\n',response.decode())
    clientSocket.close()

def head_request():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    request = "HEAD /index.html HTTP/1.1"
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)
    print('---HEAD /index.html HTTP/1.1---\n\n',response.decode())
    clientSocket.close()

def delete_request():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    request = "DELETE /new7.html HTTP/1.1\r\nHost: 127.0.0.1:1234\r\nConnection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36\r\nCache-Control: no-cache\r\nAuthorization: Basic VkFNSzp2YW1rMTQxMA==\r\nPostman-Token: 87b2ab5a-38d9-0248-430f-34efb3e0a7f0\r\nAccept: */*\r\nOrigin: chrome-extension://fhbjgbiflinjbdggehcddcbncdddomop\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n"
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)
    print('---DELETE /new7.html HTTP/1.1---\n\n',response.decode())
    clientSocket.close()

def simple_put_request():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    request = "PUT /new8.html HTTP/1.1\r\nHost: 127.0.0.1:1234\r\nConnection: keep-alive\r\nContent-Length: 5\r\nAuthorization: Basic VkFNSzp2YW1rMTQxMA==\r\nPostman-Token: 0d50bc71-239b-7c7f-31d7-c246a410e788\r\nCache-Control: no-cache\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36\r\nContent-Type: text/plain;charset=UTF-8\r\nAccept: */*\r\nOrigin: chrome-extension://fhbjgbiflinjbdggehcddcbncdddomop\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\nHello"
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)
    print('---PUT /new8.html HTTP/1.1---\n\n',response.decode())
    clientSocket.close()

def file_put_request():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    request = "PUT /new9.html HTTP/1.1\r\nHost: 127.0.0.1:1234\r\nConnection: keep-alive\r\nContent-Length: 271\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36\r\nCache-Control: no-cache\r\nAuthorization: Basic VkFNSzp2YW1rMTQxMA==\r\nPostman-Token: bd79ce4d-dd00-9deb-ccc4-974ee9d8f405\r\nAccept: */*\r\nOrigin: chrome-extension://fhbjgbiflinjbdggehcddcbncdddomop\r\nSec-Fetch-Site: none\r\nSec-Fetch-Mode: cors\r\nSec-Fetch-Dest: empty\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML 2.0//EN\">\r\n<html>\r\n<head>\r\n<title>200 Ok</title>\r\n</head>\r\n<body>\r\n<h1>Ok</h1>\r\n<h4>The file was already present. The content is modified.</h4>\r\n<hr>\r\n<address>Apache/2.4.41 (Ubuntu) Server at 127.0.0.1</address>\r\n</body>\r\n</html>"
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)
    print('---PUT /new9.html HTTP/1.1 file data---\n\n',response.decode())
    clientSocket.close()
    
def non_persistent_request():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    request = "HEAD /index.html HTTP/1.0"
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)
    print('---HEAD /index.html HTTP/1.0---\n\n',response.decode())
    clientSocket.close()

def version_not_supported():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    request = "HEAD /index.html HTTP/2.1"
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)
    print('---HEAD /index.html HTTP/2.1---\n\n',response.decode())
    clientSocket.close()

def unsupported_media_type():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    request = "GET /try.pptx HTTP/1.1"
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)
    print('---GET /try.pptx HTTP/1.1---\n\n',response.decode())
    clientSocket.close()
    
def main():
    get_thread = threading.Thread(target=get_request)
    get_thread.start()

    head_thread = threading.Thread(target=head_request)
    head_thread.start()
    
    non_persistent_thread = threading.Thread(target=non_persistent_request)
    non_persistent_thread.start()

    delete_thread = threading.Thread(target=delete_request)
    delete_thread.start()

    simple_put_thread = threading.Thread(target=simple_put_request)
    simple_put_thread.start()

    file_put_thread = threading.Thread(target=file_put_request)
    file_put_thread.start()

    version_not_supported_thread = threading.Thread(target=version_not_supported)
    version_not_supported_thread.start()

    unsupported_media_type_thread = threading.Thread(target=unsupported_media_type)
    unsupported_media_type_thread.start()

    get_thread.join()
    non_persistent_thread.join()
    head_thread.join()
    delete_thread.join()
    simple_put_thread.join()
    file_put_thread.join()
    version_not_supported_thread.join()
    unsupported_media_type_thread.join()
    
    

if __name__ == "__main__":
    main()
