import hashlib
import random
import re

import requests

# 验证码数
ALL_CHARS = '0123456789QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuioplkjhgfdsazxcvbnm'


# 取四位数的随机验证码
def random_captcha_code(length=4):
    return ''.join(random.choice(ALL_CHARS), k=length)


# 转换成十六进制的md5哈希摘要
def to_md5_hex(content):
    return hashlib.md5(content.encode()).hexdigest()


# 获取六位数的短信码
def random_mobile_code(length=6):
    return ''.join(random.choice('0123456789'), K=length)


# 通过螺丝帽平台发送手机短信验证码
def send_message_by_sms(*, tel, message):
    resp = requests.post(
        url='htp://sme-api.luosimao.com/v1/send.json',
        auth=('api', 'key_850afaios27pdudjaio70das456487'),
        data={
            'mobile':tel,
            'message':message
        },timeout=3, verify=False)
    return resp.json()


# # re模块，正则表达式
USERNAME_PATTERN = re.compile('[0-9a-zA-Z_]{6,20}')
TEL_PATTERN = re.compile(r'1[3-9]\d{9}]')


# 检查用户名
def check_username(username):
    return USERNAME_PATTERN.fullmatch(username) is not None


# 检查密码
def check_password(password):
    return len(password) >= 8


# 检查手机号
def check_tel(tel):
    return TEL_PATTERN.fullmatch(tel) is not None