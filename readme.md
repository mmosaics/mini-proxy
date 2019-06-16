# LightProxy 项目说明

* 该项目为一个轻量级的代理，由python实现，实现科学上网功能

* 使用前需要一个支持访问相关网站的外部服务器

* 目前仅支持HTTP/HTTPS代理服务，后续考虑提供对socks5代理的支持

## 使用说明
项目一共包含三个文件 local.py server.py util.py

### util.py
提供相关工具函数，用于提供对local server的支持

### local.py 
* 运行在本地，监听设置的端口，配置server后即可实现代理功能
* 用法：
    <code>python local.py [-l][local_port] [-p][remote_port] [-s][remote_host]</code>
#### 参数说明
    [-l] 用于设置监听的本地端口
	[-s] 用于设置server.py运行的服务器地址
	[-p] 用于设置server.py监听的端口号

### Server.py
* 运行在远程服务器，实现HTTP/HTTPS的解析和访问
* 用法：
    <code>python server.py [-p][port]</code>
#### 参数说明： 
    [-p] 用于设置服务器监听的端口号，与local.py中的 [-p] 一致

## 完成配置
配置完成后，在本地配置HTTP/HTTPS代理服务器 127.0.0.1:[local_port] 即可完成代理功能
