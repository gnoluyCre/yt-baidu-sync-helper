import sys

# print(sys.stdin.encoding)
#
sys.stdin.reconfigure(encoding='gbk')
sys.stdout.reconfigure(encoding='gbk')
#
print(sys.stdin.encoding)
print(sys.stdout.encoding)
# 上述代码表名：和上述编码无关

#sys.stdout.reconfigure(encoding='utf-8')
# s = b'aaa123\xe4\xbd\xa0\xe5\xa5\xbd\n'
# print(s.decode("utf-8"))


while True:
    input_text = sys.stdin.buffer.read()
    # input_text = input()
    if input_text:
        # print(input_text)
        print(type(input_text))
        print(input_text)
        print(input_text.decode("utf8"))
    else: break


# import sys
# import locale
#
# print("stdin编码:", sys.stdin.encoding)
# print("默认编码:", sys.getdefaultencoding())
# print("系统区域编码:", locale.getpreferredencoding())
#
# # 测试输入
# text = input("请输入中文: ")
# print("输入内容:", text)
# print("字节表示:", text.encode(sys.stdin.encoding))