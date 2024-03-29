from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse
import urllib.request


class HTTPHandler(BaseHTTPRequestHandler):
    post_handler=None
    get_handler=None
    
    def text_to_html(self, req_head):
        r""" 将请求头包装成 html，便于返回给 http 客户端 """
        html = '<html><head><title>Echo HTTP Header</title></head>' 
        html += '<body><div>'
        html += '<font color="blue">%s - %s - %s</font><br/><br/>'
        html = html % (self.client_address, self.request_version, self.path)
        for line in req_head.split('\n'):
            line = line.strip()
            if line.startswith('Via:') or line.startswith('X-Forwarded-For:'):
                line = '<font color="red">%s</font><br/>' % line
            else:
                line = '<font color="black">%s</font><br/>' % line
            html += line
        html += '</div></body></html>'

        return html
    
    def do_GET(self):
        r""" 响应 get 请求，打印 http 头，并返回给 http 客户端 """
        # print('%s - %s - %s' % (self.client_address, self.request_version, self.path))
        # print(type(self.client_address))
        # print('### request headers ###')
        # req_head = str(self.headers)
        # # print('req_head: %s' % req_head)
        # for line in req_head.split('\n'):
        #     line = line.strip()
        #     if line.startswith('Via:') or line.startswith('X-Forwarded-For:'):
        #         line = '%s%s%s' % (fg('red'), line, attr('reset'))
        #     print(line)
        

        '''
        可选返回 text，html
        '''
        # text = '%s - %s - %s\n---\n%s' % (self.client_address, 
        #                                     self.request_version, 
        #                                     self.path, 
        #                                     req_head)
        # text = text.encode('utf8')
        # html = self.text_to_html(req_head).encode('utf8')
        path_data= urllib.request.unquote(self.path)
        
        
        # if text:
        #     text=text.encode('utf8')
        #     self.send_response(200)
        #     self.end_headers()
        #     #self.send_header('Access-Control-Allow-Origin', '*')

        #     self.wfile.write(text)

    def do_POST(self):
        r""" 响应 post 请求，返回 json """
        # POST 有 Content-Length，GET 无 Content-Length
        #content_len = int(self.headers.getheader('content-length'))
        # parsed_path = urlparse(self.path)
        # self.wfile.write(json.dumps({
        #     'method': self.command,
        #     'path': self.path,
        #     'real_path': parsed_path.query,
        #     'query': parsed_path.query,
        #     'request_version': self.request_version,
        #     'protocol_version': self.protocol_version,
        #     'body': response
        # }).encode())
        print(f'POST: client address ---{self.address_string()}')

        content_len = int(self.headers['Content-Length'])   
        # print(f'POST: headers---{str(self.headers)}')
        post_body = self.rfile.read(content_len)
        print(f'POST: {self.path},{post_body}')
        data={}
        response=''
        if len(post_body)!=0:
            print(f'POST body:{post_body}')
        else:
            print('post body is empty')
        # if response:
        self.send_response(200)
        self.end_headers()
        self.wfile.write('')
        
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Allow', 'GET, OPTIONS')
        #self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'X-Request, X-Requested-With')
        
        self.send_header('Content-Length', '0')
        self.end_headers()
  
if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Echo HTTP server.')
    # parser.add_argument('-a', '--address', help='default: 0.0.0.0')
    # parser.add_argument('-p', '--port', help='default: 5678', type=int)
    # args = parser.parse_args()
    ip = '0.0.0.0'
    port = 8081
    server = HTTPServer((ip, port), HTTPHandler)
    server.serve_forever()
