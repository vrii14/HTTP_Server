from socket import *
import requests
import threading
import sys
import os
import time

port = sys.argv[1]

IP = '127.0.0.1'

same_url_part = "http://" + IP + ":" + port 

def get_requests():
    get_req_1 = requests.get(same_url_part + "/index.html")
    print("GET /index.html: " + str(get_req_1.status_code))
    get_req_2 = requests.get(same_url_part + "/website/demo.mp3")
    print("GET /website/demo.mp3: " + str(get_req_2.status_code))
    get_req_3 = requests.get(same_url_part + "/website/dashboard.html")
    print("GET /website/dashboard.html: " + str(get_req_3.status_code))
    get_req_4 = requests.get(same_url_part + "/website/demo.pdf")
    print("GET /website/demo.pdf: " + str(get_req_4.status_code))

    get_req_5 = requests.get(same_url_part + "/index.html", cookies = {'id': 'trying'})
    print("GET /index.html with cookies header: " + str(get_req_5.status_code))
  
    get_req_6 = requests.get(same_url_part + "/website/dashboard.html", headers={'If-Modified-Since': 'Wed, 4 Nov 2020 19:28:00 GMT'})
    print("GET /website/dashboard.html with If-Modified-Since header: " + str(get_req_6.status_code))

    get_req_7 = requests.get(same_url_part + "/website")
    print("GET /website: " + str(get_req_7.status_code))

    query = {'name':'Vrinda Ahuja', 'age':20, 'email':'vrii@gmail.com', 
         'password':'testing321', 'gender':'Female', 'game':'Badminton'}
    get_req_8 = requests.get(same_url_part + "/website/form_get.html", params=query)
    print("GET /website/form_get.html with url parameters of form data: " + str(get_req_8.status_code))


def post_requests():
    post_input_1 = {'name':'Vrinda Ahuja', 'age':20, 'email':'abc@gmail.com', 
         'password':'testing', 'gender':'Female', 'game':'Badminton'}
    post_url = same_url_part + "/website/dashboard.html"
    post_req_1 = requests.post(post_url, post_input_1)
    print("POST /website/dashboard.html: " + str(post_req_1.status_code))
    time.sleep(0.3)
    post_input_2 = {'name':'Mrunal Kotkar', 'age':20, 'email':'xyz@gmail.com', 
         'password':'test', 'gender':'Female', 'game':'Cricket'}
    post_url = same_url_part + "/website/dashboard.html"
    post_req_2 = requests.post(post_url, post_input_2)
    print("POST /website/dashboard.html: " + str(post_req_2.status_code))
    time.sleep(0.3)

def put_get_del_requests():
    data = "<h1>Hi</h1>"
    put_req = requests.put(same_url_part + "/new1.html", data =data)
    # time.sleep(0.3)
    print("PUT /new1.html: " + str(put_req.status_code))
    get_requ = requests.get(same_url_part + "/new1.html")
    print("GET /new1.html: " + str(get_requ.status_code))
    delete_req = requests.delete(same_url_part + "/new1.html")
    print("DELETE /new1.html: " + str(delete_req.status_code))
    get_requ_2 = requests.get(same_url_part + "/new1.html")
    print("GET /new1.html: " + str(get_requ_2.status_code))



def head_requests():
    head_req_1 = requests.head(same_url_part + "/website/login.html")
    print("HEAD /website/login.html: " + str(head_req_1.status_code))
    head_req_2 = requests.head(same_url_part + "/website/old.html")
    print("HEAD /website/old.html: " + str(head_req_2.status_code))
    head_req_3 = requests.head(same_url_part + "/try.pptx")
    print("HEAD /try.pptx: " + str(head_req_3.status_code))
    head_req_4 = requests.head(same_url_part + "/try.html")
    print("HEAD /try.html: " + str(head_req_4.status_code))

def downloading_image():
    req = requests.get(same_url_part + "/website/demo.jpg", stream=True)
    req.raise_for_status()
    with open('Download.jpg', 'wb') as fd:
        for chunk in req.iter_content(chunk_size=50000):
            print('Received a Chunk')
            fd.write(chunk)
    print("Downloaded image named Download.jpg in the document root")


def main():
    get_thread = threading.Thread(target=get_requests)
    get_thread.start()
    
    post_thread = threading.Thread(target=post_requests)
    post_thread.start()

    head_thread = threading.Thread(target=head_requests)
    head_thread.start()

    multiple_thread = threading.Thread(target=put_get_del_requests)    
    multiple_thread.start()

    downloading_thread = threading.Thread(target=downloading_image)
    downloading_thread.start()

    get_thread.join()
    post_thread.join()
    head_thread.join()
    multiple_thread.join()
    downloading_thread.join()
    
    
if __name__ == "__main__":
    main()