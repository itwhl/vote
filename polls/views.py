import io
import json
import os.path
import re
import uuid
from datetime import timedelta
from urllib.parse import quote

import jwt
import xlwt
import redis
from django.core.cache import cache, caches
from django.db import DatabaseError
from django.db.models import Q
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection
from rest_framework.decorators import api_view, authentication_classes, throttle_classes
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from polls.captcha import Captcha
from polls.models import Teacher, Subject, User
from polls.serializers import SubjectSerializer, TeacherSerializer, SubjectSimpleSerializer
from polls.utils import to_md5_hex, random_captcha_code, send_message_by_sms, random_mobile_code, check_username, \
    check_password, check_tel, LoginRequiredAuthentication, update_last_visit, upload_stream_to_qiniu, POOL
from vote.settings import SECRET_KEY, BASE_DIR


def show_index(request):
    # 显示首页（开发测试使用）
    return redirect('/static/html/subjects.html')


# CBV方式定制数据接口(ListAPIView支持查询列表)
# class HostSubjectView(ListAPIView):
#     queryset = Subject.objects.filter(is_hot=True)
#     serializer_class = SubjectSerializer


# # CBV方式定制数据接口(ModelViewSet支持增删改查,ReadOnlyModelViewSet只支持查询)
# @method_decorator(decorator=cache_page(timeout=3600, cache='api', name='list'))  # # 通过Django框架提供的method_decorator装饰器对类实现声明式缓存
# @method_decorator(decorator=cache_page(timeout=3600, cache='api', name='retrie'))
# class SubjectViewSet(ModelViewSet):
#     queryset = Subject.objects.all()  # 如何取数据
#     serializer_class = SubjectSerializer  # 如何序列化数据
#     authentication_classes = (LoginRequiredAuthentication, )  # CBV通过authentication_classes属性来指定身份认证类


# #   FBV方式定制数据接口(添加编程式缓存)
# @api_view(('GET', ))  # 通过装饰器限制请求方法
# # @cache_page(timeout=3600, cache='api')  # 通过装饰器设置声明式缓存
# def show_subjects(request: HttpRequest) -> HttpResponse:
#     # 获取学科数据
#     # 通过Django-Redis封装的get_redis_connection函数直接获得Redis对象,可以使用Redis所有命令操作缓存
#     # 提醒:在实际的商业项目中,必须对Redis操作进行二次封装,以避免程序员发出危险操作(如flushall/flushdb)
#     redis_cli = get_redis_connection(alias='api')
#     data = redis_cli.get('vote:polls:subject')
#     if data:
#         data = json.loads(data)  # json.loads为反序列化,json格式转换字典格式,json.dumps为序列化,字典格式转换json格式
#     else:
#         queryset = Subject.objects.all()
#         data = SubjectSerializer(queryset, many=True).data  # many=True多个对象
#         redis_cli.set('vote:polls:subject', json.dumps(data), ex=3600)
#     # 通过DRF定制的Response来返回JSON格式的数据
#     return Response(data)  # data装在列表（多个对象）或者字典里


# FBV方式定制数据接口
@api_view(('GET', ))  # 通过装饰器限制请求方法
# @cache_page(timeout=3600, cache='api')  # 通过装饰器设置声明式缓存
def show_subjects(request: HttpRequest) -> HttpResponse:
    # 获取学科数据
    queryset = Subject.objects.all()
    seri = SubjectSerializer(queryset, many=True)  # many=True多个对象
    # 通过DRF定制的Response来返回JSON格式的数据
    return Response({'subjects': seri.data})  # data装在列表（多个对象）或者字典里


# FBV方式定制数据接口
@api_view(('GET', ))
def show_teachers(request: HttpRequest) -> HttpResponse:
    # 获取指定学科老师数据
    sno = int(request.GET['sno'])  # 通过request对象的GET属性可以获取来自于URL的参数（是个字典）
    subject = Subject.objects.only('name').get(no=sno)
    sub_seri = SubjectSimpleSerializer(subject)
    queryset = Teacher.objects.filter(subject__no=sno).defer('subject')
    tea_seri = TeacherSerializer(queryset, many=True)
    return Response({'subject': sub_seri.data, 'teachers': tea_seri.data})


@api_view(('GET', ))
@authentication_classes((LoginRequiredAuthentication, ))  # FBV通过装饰器调用写好的身份认证类
def praise_or_criticize(request: HttpRequest) -> HttpResponse:
    # 投票
        try:
            user = User.objects.only('counter').get(no=request.user.no)
            if user.counter > 0:
                tno = int(request.GET['tno'])  # 此方法会报KeyError,ValueError异常
                teacher = Teacher.objects.get(no=tno)
                user.counter -= 1
                if request.phan.startswith('/praise'):
                    teacher.good_count += 1
                    count = teacher.good_count
                else:
                    teacher.bad_count += 1
                    count = teacher.bad_count
                # Django提供的事务原子性操作，要么全成功要么全失败
                with atomic():  # atomic函数返回一个Atomic对象
                    teacher.save()
                    user.save()
                data = {'code': 10000, 'message': '投票成功', 'count': count}
            else:
                data = {'code': 10002, 'message': '每天只能投5票'}
        except(KeyError, ValueError, Teacher.DoesNotExist, User.DoesNotExist, DatabaseError):
                data = {'code': 10001, 'message': '投票失败'}
        return Response(data)


def get_captcha(request:HttpRequest) -> HttpResponse:
    # 生成验证码图片
    code = random_captcha_code()
    request.session['captcha'] = code
    image_data = Captcha.instance().generate(code)
    return HttpResponse(image_data,content_type='image/png')


@api_view(('POST', ))  # 只接受POST请求
@throttle_classes(())  # 登录不限速
def login(request: HttpRequest) -> HttpResponse:
    # 登录
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        if check_username(username) and check_password(password):
            password = to_md5_hex(password)
            user = User.objects.filter(Q(username=username) | Q(tel=username)).filter(password=password).first()  # Q对象写或者关系，.filter为并且关系
            if user:
                # 如果函数的参数不是JSON序列化的对象，那么这里通过serializer参数指定其他的序列化方式，可以使用pickle序列化（序列化成字节串）
                update_last_visit.apply_async((user, ), serializer='pickle')
                # 用户登陆成功，向用户签发身份令牌（JWT）
                payload = {
                    'userid': user.no,
                    'exp': timezone.now() + timedelta(days=1)  # 当前时间+一天
                }
                # 通过三方库pyJWT生成Json Web Token作为给用户签发的身份令牌
                # 这个令牌要通过返回JSON格式的数据返回到用户浏览器中，用户浏览器保存token
                # 后续请求可以在请求头中带上token，服务器通过token确认用户身份
                token = jwt.encode(payload, SECRET_KEY)
                data = {
                    'code': 20000, 'message': '登陆成功',
                    'token': token, 'username': user.username
                }
            else:
                data = {'code': 20001, 'message': '用户名或密码错误'}
        else:
            data = {'code': 20002, 'message': '无效的用户名和密码'}
        return Response(data)


@api_view(('POST', ))
def register(request: HttpRequest) -> HttpResponse:
    # 注册
    agreement = request.data.get('agreement')
    if agreement == 'true':
        # code_from_user = request.data.get('mobilecode', '0')
        # code_from_session = request.session.get('mobilecode', '1')
        # request.session['moblecode'] = ''  # 拿到后失效
        # if code_from_user == code_from_session:
        username = request.data.get('username')
        password = request.data.get('password')
        tel = request.data.get('tel')
        # 从HTTP请求消息体中获取上传的文件
        photo = request.FILES.get('photo')
        if photo.size <= 2621440:
            if check_username(username) and check_password(password) and check_tel(tel):
                user = User()
                user.username = username
                user,password = to_md5_hex(password)
                user.tel = tel
                if photo:
                    # 从上传文件的文件名中获取文件后缀名（元组第一个元素是文件名，第二个元素是后缀名）
                    ext = os.path.splitext(photo.name)[1]
                    # 生成UUID充当文件名
                    filename = f'{uuid.uuid1().hex}{ext}'
                    # 调用线程池的submit方法 可以指定把什么样的任务放到线程中执行
                    # 调用submit方法会返回Future对象,可以在将来的某个时候获取线程的执行结果
                    future = POOL.submit(upload_stream_to_qiniu, photo, filename, photo.size)
                    # Future对象的add_done_callback方法可以绑定线程执行完成后要执行的回调函数
                    # 这样的话在线程执行结束时,可以指定需要自动执行的代码
                    # future.add_done_callback(...)
                    # 把文件储存到七牛云
                    # upload_stream_to_qiniu(photo, filename, photo.size)
                    # 数据库储存文件域名
                    user.photo = f'http://qfcgif559.hn-bkt.clouddn.com/{filename}'
                try:
                    user.save()
                    data = {'code': 30000, 'message': '注册成功，请登录'}
                except DatabaseError:
                    data = {'code': 30001, 'message': '用户名或手机号已被注册'}
            else:
                data = {'code': 30002, 'message': '请输入有效的注册信息'}
        else:
            data = {'code': 30004, 'message': '上传的图片大小超过了2.5M'}
    else:
        data = {'code': 30003, 'message': '请勾选同意网站用户协议及隐私政策'}
    return Response(data)


def logout(request: HttpRequest) -> HttpResponse:
    # 注销
    request.session.flush()  # 清理cookie里的sessionid
    return redirect('/login/')


def send_mobile_code(request: HttpRequest, tel) -> HttpResponse:
    # 发送验证码
    # 通过Django框架封装的cache对象，可以直接操作Redis，但是只能操作字符串类型，get表示通过键读取数据，set是放置键值对到Redis，可以使用timeout指定键过期时间，如果不使用默认缓存，可以使用caches对象caches[]
    if check_tel(tel):
        if cache.get(f'vote:polls:block:{tel}'):
            data = {'code':20002, 'message':'请不要在120秒内重复发送验证码'}
        else:
            code = random_mobile_code()
            request.session['mobilecode'] = code
            message = f'你的短信验证码是{code}。[XX平台]'
            # 异步化执行发送短信操作（消息的生产者，把任务放到消息队列）
            send_message_by_sms.delay(tel=tel, message=message)
            cache.set(f'vote:polls:block:{tel}', code, timeout=120)
            data = {'code': 20000, 'message': '短信验证码已发送到您的手机'}
    else:
        data = {'code':20001, 'message':'请输入正确的手机号'}
    return HttpResponse(data)


def is_unique_username(request: HttpRequest) -> HttpResponse:
    # 检查用户名唯一性
    username = request.POST.get('username')
    if check_username(username):
        if User.objects.filter(username=username).exisit():
            data = {'code':30001, 'message': '用户名已被注册'}
        else:
            data = {'code':30000, 'message': '用户名可以使用'}
    else:
        data = {'code': 30002, 'message': '无效的用户名'}
    return JsonResponse(data)


@api_view(('GET', ))
@authentication_classes((LoginRequiredAuthentication, ))  # 通过装饰器调用写好的身份认证类
def get_stat_date(request:HttpRequest) -> HttpResponse:
    # 测试导出数据接口
    teachers = Teacher.objects.all().only('name', 'good_count', 'bad_count').order_by('-good_count')[:10]
    x_data = [teacher.name for teacher in teachers]
    y1_data = [teacher.good_count for teacher in teachers]
    y2_data = [teacher.bad_count for teacher in teachers]
    return Response({'name': x_data, 'good_count': y1_data, 'bad_count': y2_data})


def export_excel(request: HttpRequest) -> HttpResponse:
    # 导出Excel报表文件
    # 创建工作簿
    wb = xlwt.Workbook()
    # 创建工作表
    sheet = wb.add_sheet('投票数据统计表')
    titles = ('姓名', '所属学科')
    for col, title in enumerate(titles):  # enumerate可以拿到下标和元素的二元组
        sheet.write(0, col,title)
    # select_related()查询teacher数据时顺便查询subject数据，避免sql重复
    queryset = Teacher.objects.all().only('name', 'subject__name').select_related('subject').order_by('-subject__name')
    props = ('name','subject')
    for row, teacher in enumerate(queryset):
        for col, prop in enumerate(props):
            # 通过getattr函数动态获取指定对象的属性
            value = str(getattr(teacher, prop, ''))
            sheet.write(row + 1, col, value)
    # 将工作簿的内容写入BytesIo中
    buffer = io.BytesIO()
    wb.save(buffer)
    # 通过BytesIo对象的getvalve方法获得bytes对象（字节串）写入HTTP响应
    resp = HttpResponse(buffer.getvalue())  # 把Workbook处理成字节串（bytes）放到HttpResponse中，然后还要告诉浏览器，给到的内容类型是Excel文件（MIME类型content_type）
    # 添加HTTP响应头（以键值对的方式写入）
    resp['Content-Type'] = 'application/vnd.ms-excel'
    # 使用urllib.parse模块的quote函数将中文处理成百分号编码
    filename = quote('投票数据统计。xls')
    # inline - 表示浏览器直接内联打开文件；attachment - 表示浏览器以附件的方式下载文件
    resp['Content-Disposition'] = f'attachment；filename*=utf-8\'\'{filename}'
    return resp



