import socket
import ssl


class URL:
    def __init__(self, url):
        # URL 파싱
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]
        
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
            
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        
    def request(self):
        ctx = ssl.create_default_context()
        
        s = socket.socket(
            family=socket.AF_INET, # 다른 컴퓨터를 찾는 방법 (address family)
            type=socket.SOCK_STREAM, # 어떤 종류의 대화가 이루어질지
            proto=socket.IPPROTO_TCP # 두 컴퓨터가 연결을 설정하는 단계 (Protocol)
        )        
        s.connect((self.host, self.port))
        
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        s.send(request.encode("utf8"))
        
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
            
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        
        body = response.read()
        s.close()
        
        return body
    
def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")
            
def load(url):
    body = url.request()
    show(body)
    
if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))