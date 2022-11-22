import hashlib
import random
import re
from concurrent.futures.thread import ThreadPoolExecutor

import jwt
import qiniu
import requests
from django.utils import timezone
from jwt import InvalidTokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


# 验证码数
from polls.models import User
# from vote import app
# from vote import app
from vote.settings import SECRET_KEY

ALL_CHARS = '0123456789QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuioplkjhgfdsazxcvbnm'


# 认证类
class LoginRequiredAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token = request.META.get('HTTP_TOKEN')
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY)
                user = User()
                user.no = payload['userid']
                # 如果验证通过，authenticate方法会返回一个二元组，二元组中的第一个参数是user对象，它会跟request对象进行绑定，后面的代码可以通过request.user获取到用户相关信息，二元组中的第二个参数是用户的身份令牌，稍后可能还会用到该令牌，所以要返回它
                return user, token
            # 如果令牌是伪造的，篡改过的或者过期的，那么都会出现InvalidTokenError，认证失败，抛出异常
            except InvalidTokenError:
                raise AuthenticationFailed('请重新登录')
        else:
            raise AuthenticationFailed('请先登录')


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
# @app.task
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
    return len(password) >= 6


# 检查手机号
def check_tel(tel):
    return TEL_PATTERN.fullmatch(tel) is not None


# 更新登陆时间函数
# @app.task
def update_last_visit(user):
    user.last_visit = timezone.now()
    user.save()


# # 七牛云配置
QINIU_ACCESS_KEY = 'AK码'
QINIU_SECRET_KEY = 'SK码'
QINIU_BACKET_NAME = '仓库名字'

# 创建七牛云的认证对象,需要指定AK和SK
# 通过认证对象可以获取服务器提供的令牌,有了令牌才能上传文件
AUTH = qiniu.Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)


def upload_file_to_qiniu(file_path, filename):
    """将文件上传到七牛云存储"""
    token = AUTH.upload_token(QINIU_BACKET_NAME, filename)
    # 返回的是一个二元组
    result, *_ = qiniu.put_file(token, filename, file_path)
    return result


def upload_stream_to_qiniu(file_stream, filename, size):
    """将数据流上传到七牛云存储"""
    token = AUTH.upload_token(QINIU_BACKET_NAME, filename)
    result, *_ = qiniu.put_stream(token, filename,file_stream, None, size)
    return result


# 创建线程池对象(池化技术 ---> 空间换时间(线程池,数据库连接池))
POOL = ThreadPoolExecutor(max_workers=32)