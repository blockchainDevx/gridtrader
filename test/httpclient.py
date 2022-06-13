#coding=utf-8

import http.client,urllib.parse


def post_demo():
    params = urllib.parse.urlencode({'tokenId': 0, 'minter': '3423412dfasf','owner':'123adfs','collection':'asdfasdfasd','txhash':'asdfasdfasd'})
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}
    conn = http.client.HTTPSConnection("backend.ethmore.pro")
    conn.request("POST", "/api/v1/setNftData", params, headers)
    response = conn.getresponse()
    print(response.status, response.reason)

    if not response.closed:
        data = response.read()
        print(data, type(data.decode('utf-8')))

    conn.close()


if __name__=='__main__':
    post_demo()