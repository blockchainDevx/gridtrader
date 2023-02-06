# from policies.GridTraderHttp import *
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from GridManager import GridManager 
import urllib.request
from common.common import http_response,Record,LOG_STORE
from common.configer.config import Config
from common.common import LOGIN,ADD,CALC,START,STOP,INIT,DEL,UPDATE,QUERY,ADDAPI,CHKST,GROUPS,ADDAPIGROUP,ADDSYMBOL,SYMBOLS,DELSYMBOL

from common.logger.Log import log
from common.ws.WebPush import WebPush

import traceback

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
        clientip=self.address_string()
        grid_mgr=GridManager()
        text=grid_mgr.get_handler(path_data,clientip)
        
        if text:
            text=text.encode('utf8')
            self.send_response(200)
            self.end_headers()
            #self.send_header('Access-Control-Allow-Origin', '*')

            self.wfile.write(text)

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

        content_len = int(self.headers['Content-Length'])   
        post_body = self.rfile.read(content_len)
        response=''
        if len(post_body)!=0:
            try:
                grid_mgr=GridManager()
                response=grid_mgr.post_handler(self.path,post_body)
            except Exception as e:
                msg=traceback.format_exc()
                Record(msg,level=LOG_STORE)
                response=http_response(self.path,'',-1,'参数格式错误')
        else:
            Record('post body is empty!',level=LOG_STORE)
        if response:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(response.encode())
        
    
    def do_OPTIONS(self):
        if self.path in (LOGIN,ADD,CALC,START,STOP,INIT,DEL,UPDATE,QUERY,ADDAPI,CHKST,GROUPS,ADDAPIGROUP,ADDSYMBOL,SYMBOLS,DELSYMBOL):
            self.send_response(200)
            self.send_header('Allow', 'GET, OPTIONS')
            #self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'X-Request, X-Requested-With')
        else:
            self.send_response(404)
        self.send_header('Content-Length', '0')
        self.end_headers()
  
if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Echo HTTP server.')
    # parser.add_argument('-a', '--address', help='default: 0.0.0.0')
    # parser.add_argument('-p', '--port', help='default: 5678', type=int)
    # args = parser.parse_args()
    # ip = args.address or '0.0.0.0'
    # port = args.port or 8081
    config=Config()
    config.Init('config_copy.json')
    ip=config.glob['http_ip'] or '0.0.0.0'
    port=int(config.glob['http_port']) or 8081
    webport= int(config.glob['web_port']) or 8082
    
    # print('Listening %s:%d' % (ip, port))
    # log(f'Listening {ip}:{port}')
    Record(f'Listening {ip}:{port}',level=LOG_STORE)
    
    grid_mgr=GridManager()
    grid_mgr.init()
    webpush=WebPush()
    webpush.init(webport)
    webpush.start()
    server = HTTPServer((ip, port), HTTPHandler)
    server.serve_forever()
