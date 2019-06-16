#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import select
import threading
from urllib import parse as urlparse
from util import *

BUF_SIZ = 8192

Local = "127.0.0.1"
GoogleCloud = "35.194.156.82"

remote_host = GoogleCloud
remote_port = 8081
local_host = "127.0.0.1"
local_port = 8090


class ServerProxy(threading.Thread):
    """代理端 client对应于本地连接代理的socket， server对应于HTTP请求的目标HOST"""
    def __init__(self, client, addr):
        super().__init__()
        self.client = client
        self.addr = addr
        self.is_http_tunnel = 0
        self.server = None

    def handle_request(self, request):
        """
            处理请求信息，并完成TCP的连接工作
        """
        if self.server and not self.server.closed:
            self.server.queue(request)
            return
        header_lines = request.split(b'\r\n')
        request_line_param = header_lines[0].split(b' ')

        method = request_line_param[0]
        url = urlparse.urlsplit(request_line_param[1])

        if method == b'CONNECT':
            host, port = url.path.split(b':')
        else:
            host, port = url.hostname, url.port if url.port else 80

        self.server = Server(host, port)

        try:
            self.server.connect()
        except Exception as e:
            self.server.closed = True

        if method == b'CONNECT':
            tunnel_ok_msg = b'HTTP/1.1 200 Connection Established\r\n\r\n'
            self.client.queue(tunnel_ok_msg)
            print("The Client [%s] CONNECT %s" % (self.client.addr[0], host))
        else:
            """
                此处完成了对HTTP请求的重建工作，需要把请求行重建为path的形式
            """
            request_line = b' '.join([request_line_param[0], url.path, request_line_param[2]])
            header_lines[0] = request_line
            request_data = b'\r\n'.join(header_lines)
            self.server.queue(request_data)
            print("The Client [%s] is visiting [%s]" % (self.client.addr[0], host))

    def get_lists(self):
        rlist, wlist, xlist = [self.client.conn], [], []
        if self.client.has_buffer():
            wlist.append(self.client.conn)
        if self.server and not self.server.closed:
            rlist.append(self.server.conn)
        if self.server and not self.server.closed and self.server.has_buffer():
            wlist.append(self.server.conn)
        return rlist, wlist, xlist

    def handle_rlist(self, r):
        if self.client.conn in r:
            data = self.client.recv()
            if not data:
                return True

            # 解密步骤，解密后进行解析
            data = decrypt(data)
            try:
                self.handle_request(data)
            except Exception as e:
                self.client.flush()
                return True

            return False

        if self.server and not self.server.closed and self.server.conn in r:
            data = self.server.recv()
            if not data:
                self.server.close()
            else:
                # print(b"========Recv from HOST======: " + data)
                self.client.queue(data)
            return False

    def handle_wlist(self, w):
        if self.client.conn in w:

            # 加密步骤，对响应信息进行加密
            self.client.buffer = encrypt(self.client.buffer)
            self.client.flush()
        if self.server and not self.server.closed and self.server.conn in w:
            self.server.flush()

    def handle(self):
        """
           每当有一个来自local端的连接，则首先对获取到的数据进行解密：
                对于HTTP协议，需要完成对协议的解析，打开到目标HOST的TCP连接，再转发相应的HTTP请求
                对于HTTPS协议，只需要解析CONNECT请求，打开相应的TCP连接，响应连接状态的报文给local端，并在之后完成盲转发
            对于HOST的响应信息，只需要完成加密，转发即可
        """
        while True:
            read_list, write_list, excep_list = self.get_lists()
            r, w, x = select.select(read_list, write_list, excep_list)
            self.handle_wlist(w)
            if self.handle_rlist(r):
                break

    def run(self) -> None:
        try:
            print("The Client [%s] has connected to the proxy server..." % (self.client.addr[0]))
            self.handle()
        finally:
            self.client.close()


def main():
    """
        server端打开一个端口监听，获取来自local端的连接
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', remote_port))
    server_socket.listen(1024)
    print("Listening: (%s, %d)" % (str(remote_host), remote_port))
    while True:
        conn, addr = server_socket.accept()
        client = Client(conn, addr)
        proxy = ServerProxy(client, addr)
        proxy.start()


def parse_arg():
    global remote_port
    if has_param('-p'):
        remote_port = int(get_value('-p'))


if __name__ == '__main__':
    main()

