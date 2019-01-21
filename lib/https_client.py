import usocket as _socket
import ussl


def read_line(s, encoding="ascii"):
    data = []
    while True:
        c = s.read(1)
        if c is None:
            raise RuntimeError("IO Error while reading line")
        try:
            c = str(c, encoding)
        except UnicodeError:
            raise RuntimeError(
                "Error while converting char %s to %s" % (str(c), encoding))
        data.append(c)
        if c == "\n" or c == "":
            return "".join(data)


def read_headers(s):
    headers = []
    while True:
        line = read_line(s)
        if line == "\n" or line == "\r\n" or line == "":
            return headers
        headers.append(line)


def parse_headers(lines):
    headers = {}
    for line in lines:
        k, _, v = line.partition(":")
        headers[k.lower()] = v.strip()
    return headers


def write_header(socket, method, path, host, content_type, datalen):
    socket.write(b"%s /%s HTTP/1.1\r\n" % (method, path))
    socket.write(b"Host: %s\r\n" % host)
    socket.write(b"Connection: close\r\n")
    socket.write(b"Content-Type: %s\r\n" % content_type)
    socket.write(b"User-Agent: micropython / 1.0 \r\n")
    if datalen is not None:
        socket.write(b"Content-Length: %d\r\n" % datalen)
    socket.write(b"\r\n")


def write_body(socket, data):
    socket.write(bytes(data, 'utf8'))
    socket.write(b"\r\n\r\n")


def url_parse(url):
    proto, _, url = url.partition("/")
    _, _, url = url.partition("/")
    host, _, path = url.partition("/")
    host, _, port = host.partition(":")

    if not port:
        if proto == "https:":
            port = 443
        else:
            port = 80

    if not path:
        path = ""

    return (proto, host, port, path)

def read_body(socket):
    dataStr = bytes()
    while True:
        data = socket.read(1024)
        if data:
            dataStr += data
            if(dataStr.endswith("\r\n\r\n")):
                break
        else:
            break
    return dataStr


def request(url, method="GET", data="", cert=None, content_type="application/octet-stream"):

    proto, host, port, path = url_parse(url)

    # list index out of range when no internet
    addr = _socket.getaddrinfo(host, port)[0][-1]

    s = _socket.socket()

    s.connect(addr)

    if cert is not None:
        with open(cert, "rb") as f:
            cert = f.read()

    print(s)

    if proto == "https:":
        if cert is None:
            s = ussl.wrap_socket(s)
        else:
            s = ussl.wrap_socket(s, ca_certs=cert, server_hostname=host)

    write_header(s, method, path, host, content_type, len(data))

    write_body(s, data)

    headers = parse_headers(read_headers(s))

    content_encoding = "ascii"

    if "content-type" in headers:
        for item in headers["content-type"].split(";"):
            key,_ , value = item.strip().partition("=")
            if(key=="charset"): content_encoding = value.lower()

    body = read_body(s)

    s.close()
    s = None

    return body
