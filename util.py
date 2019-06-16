import socket
import sys
import base64

method = 'xor'


class Connection(object):
    """TCP 连接 抽象"""

    def __init__(self, what):
        self.conn = None
        self.buffer = b''
        self.closed = False
        self.what = what  #指定是 服务端套接字 还是 客户端套接字

    def send(self, data):
        return self.conn.send(data)

    def recv(self, bufsiz=8192):
        try:
            data = self.conn.recv(bufsiz)
            if len(data) == 0:
                return None
            return data
        except Exception as e:
            print(e)

    def close(self):
        self.conn.close()
        self.closed = True

    def buffer_size(self):
        return len(self.buffer)

    def has_buffer(self):
        return self.buffer_size() > 0

    # 提供缓存功能
    def queue(self, data):
        self.buffer += data

    def flush(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]


class Server(Connection):
    """服务端socket的封装"""

    def __init__(self, host, port):
        super(Server, self).__init__(b'server')
        self.addr = (host, int(port))

    def __del__(self):
        if self.conn:
            self.close()

    def connect(self):
        self.conn = socket.create_connection((self.addr[0], self.addr[1]))


class Client(Connection):
    """对客户端socket的封装"""

    def __init__(self, conn, addr):
        super(Client, self).__init__(b'client')
        self.conn = conn
        self.addr = addr


# 简单的加密模块，对每一个字节做异或运算
def encrypt(data):
    if method == 'xor':
        res = b''
        for i in data:
            res += bytes([i ^ 1])
        return res

    if method == 'base64':
        return base64.b64encode(data)

    if method == 'displace':
        displace_table = [105, 195, 81, 43, 75, 107, 124, 47, 62, 234, 45, 207, 187, 184, 192, 77, 191, 145, 213, 138,
                          210, 132, 238, 15, 104, 198, 78, 39, 165, 117, 233, 136, 157, 229, 115, 73, 214, 80, 51, 227,
                          22, 180, 125, 194, 86, 189, 146, 220, 67, 168, 159, 106, 72, 44, 16, 239, 68, 225, 208, 93,
                          142, 155, 69, 235, 172, 199, 33, 88, 196, 41, 49, 169, 26, 29, 65, 126, 137, 7, 11, 201, 166,
                          249, 144, 0, 66, 10, 204, 42, 96, 71, 111, 242, 231, 139, 121, 4, 253, 251, 171, 9, 114, 149,
                          197, 23, 183, 240, 90, 70, 83, 109, 193, 245, 36, 122, 178, 31, 102, 170, 63, 25, 153, 52,
                          218, 188, 215, 243, 57, 174, 95, 24, 14, 217, 13, 230, 100, 46, 158, 202, 17, 18, 181, 228,
                          35, 82, 119, 20, 160, 176, 232, 131, 97, 37, 219, 112, 205, 118, 91, 3, 163, 27, 32, 76, 134,
                          162, 148, 141, 212, 133, 143, 50, 246, 203, 161, 179, 120, 147, 92, 151, 6, 152, 74, 216, 244,
                          156, 101, 53, 2, 177, 79, 12, 150, 221, 30, 59, 54, 223, 182, 94, 154, 200, 58, 85, 164, 60,
                          87, 224, 84, 222, 19, 113, 110, 40, 135, 190, 185, 241, 89, 55, 103, 254, 175, 34, 99, 255,
                          209, 38, 116, 140, 130, 211, 98, 64, 48, 247, 56, 61, 252, 28, 128, 206, 173, 5, 8, 127, 250,
                          237, 186, 167, 248, 21, 236, 123, 226, 108, 1, 129]
        res = b''
        for i in data:
            res += bytes([displace_table[i]])
        return res


# 同上
def decrypt(data):
    if method == 'xor':
        res = b''
        for i in data:
            res += bytes([i ^ 1])
        return res

    if method == 'base64':
        return base64.b64decode(data)

    if method == 'displace':
        displace_table = [105, 195, 81, 43, 75, 107, 124, 47, 62, 234, 45, 207, 187, 184, 192, 77, 191, 145, 213, 138,
                          210, 132, 238, 15, 104, 198, 78, 39, 165, 117, 233, 136, 157, 229, 115, 73, 214, 80, 51, 227,
                          22, 180, 125, 194, 86, 189, 146, 220, 67, 168, 159, 106, 72, 44, 16, 239, 68, 225, 208, 93,
                          142, 155, 69, 235, 172, 199, 33, 88, 196, 41, 49, 169, 26, 29, 65, 126, 137, 7, 11, 201, 166,
                          249, 144, 0, 66, 10, 204, 42, 96, 71, 111, 242, 231, 139, 121, 4, 253, 251, 171, 9, 114, 149,
                          197, 23, 183, 240, 90, 70, 83, 109, 193, 245, 36, 122, 178, 31, 102, 170, 63, 25, 153, 52,
                          218, 188, 215, 243, 57, 174, 95, 24, 14, 217, 13, 230, 100, 46, 158, 202, 17, 18, 181, 228,
                          35, 82, 119, 20, 160, 176, 232, 131, 97, 37, 219, 112, 205, 118, 91, 3, 163, 27, 32, 76, 134,
                          162, 148, 141, 212, 133, 143, 50, 246, 203, 161, 179, 120, 147, 92, 151, 6, 152, 74, 216, 244,
                          156, 101, 53, 2, 177, 79, 12, 150, 221, 30, 59, 54, 223, 182, 94, 154, 200, 58, 85, 164, 60,
                          87, 224, 84, 222, 19, 113, 110, 40, 135, 190, 185, 241, 89, 55, 103, 254, 175, 34, 99, 255,
                          209, 38, 116, 140, 130, 211, 98, 64, 48, 247, 56, 61, 252, 28, 128, 206, 173, 5, 8, 127, 250,
                          237, 186, 167, 248, 21, 236, 123, 226, 108, 1, 129]
        res = b''
        for i in data:
            res += bytes([displace_table.index(i)])
        return res


def has_param(target):
    args = sys.argv
    arg_len = len(args)
    if target in args:
        return True
    else:
        return False


def get_value(target):
    args = sys.argv
    arg_len = len(args)
    return args[args.index(target)+1]
