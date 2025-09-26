import sys

bytes_text = sys.stdin.buffer.read()
print(type(bytes_text)) # 其实接收的就是字节流
print(bytes_text) # 做了自动解码