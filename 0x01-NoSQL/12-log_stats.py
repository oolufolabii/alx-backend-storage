#!/usr/bin/env python3
'''Python script that provides some stats about Nginx logs
stored in MongoDB
'''

from pymongo import MongoClient


def print_nginx_request_logs(nginx_collection):
    '''Prints stats about Nginx request logs.
    '''
    client = MongoClient()
    collec_nginx = client.logs.nginx

    num_of_docs = collec_nginx.count_documents({})
    print("{} logs".format(num_of_docs))
    print("Methods:")
    methods_list = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    for method in methods_list:
        method_count = collec_nginx.count_documents({"method": method})
        print("\tmethod {}: {}".format(method, method_count))
    status = collec_nginx.count_documents({"method": "GET", "path": "/status"})
    print("{} status check".format(status))


if __name__ == '__main__':
    print_nginx_request_logs
