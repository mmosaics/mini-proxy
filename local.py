#!/usr/bin/env python
# -*- coding: utf-8 -*-


import select
import threading
import sys
from util import *

BUF_SIZ = 8192

Local = "127.0.0.1"
GoogleCloud = "34.92.243.123"

remote_host = GoogleCloud
remote_port = 8081
local_host = "127.0.0.1"
local_port = 8090


class LocalProxy(threading.Thread):
    """client 对应浏览器的socket， server对应于目标服务器"""
    def __init__(self, client, addr):
        super().__init__()
        self.client = client
        self.addr = addr
        self.server = None

    def get_lists(self):
        """
            一个工具函数，用于与select协同工作
        """
        rlist, wlist, xlist = [self.client.conn], [], []
        if self.client.has_buffer():
            wlist.append(self.client.conn)
        if self.server and not self.server.closed:
            rlist.append(self.server.conn)
        if self.server and not self.server.closed and self.server.has_buffer():
            wlist.append(self.server.conn)
        return rlist, wlist, xlist

    def handle_rlist(self, r):
        """
            处理数据并缓存，检验连接是否关闭
        """
        if self.client.conn in r:
            data = self.client.recv()
            if not data:
                return True
            self.server.queue(data)
            return False

        if self.server.conn in r:
            data = self.server.recv()
            if not data:
                return True
            self.client.queue(data)
            return False

    def handle_wlist(self, w):
        """
            处理写请求，加解密在此处完成
        """
        if self.client.conn in w:
            self.client.buffer = decrypt(self.client.buffer)
            self.client.flush()
        if self.server and not self.server.closed and self.server.conn in w:
            self.server.buffer = encrypt(self.server.buffer)
            self.server.flush()

    def handle(self):
        """
            每当获取一个新的浏览器连接，就创建到server端的连接，并准备传送数据
            local所做的所有工作即为 加/解密，转发
            来自浏览器的请求，完成加密并转发到server
            来自server端的响应，完成解密并转发到浏览器
        """
        self.server = Server(remote_host, remote_port)
        self.server.connect()
        while True:
            read_list, write_list, excep_list = self.get_lists()
            r, w, x = select.select(read_list, write_list, excep_list)
            self.handle_wlist(w)
            if self.handle_rlist(r):
                break

    def run(self) -> None:
        self.handle()


def main():
    """
       local端打开一个端口进行监听，浏览器配置后所有流量都经过此处进行转发
    """
    local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_socket.bind((local_host, local_port))
    local_socket.listen(1024)
    print("Listening: (%s, %d)" % (str(local_host), local_port))
    while True:
        conn, addr = local_socket.accept()
        client = Client(conn, addr)
        proxy = LocalProxy(client, addr)
        proxy.start()


def parse_arg():
    global local_port, remote_host, remote_port
    if has_param('-l'):
        local_port = int(get_value('-l'))
    if has_param('-p'):
        remote_port = int(get_value('-p'))
    if has_param('-s'):
        remote_host = get_value('-s')


if __name__ == '__main__':
    parse_arg()
    main()





























