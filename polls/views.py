from django.db import DatabaseError
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from polls.captcha import Captcha
from polls.models import Teacher, Subject, User
from polls.utils import to_md5_hex, random_captcha_code, send_message_by_sms, random_mobile_code, check_username, check_password, check_tel



def show_subjects(request: HttpRequest) -> HttpResponse:
    queryset = Subject.objects.all()
    return render(request, 'subjects.html', {'subjects': queryset})


def show_teachers(request: HttpRequest) -> HttpResponse:
    try:
        sno = int(request.GET['sno'])  # 通过request对象的GET属性可以获取来自于URL的参数（是个字典）
        queryset = Teacher.objects.filter(subject__no=sno )  # 筛选数据
        return render(request, 'teachers.html', {'teachers': queryset})
    except(KeyError, ValueError, Teacher.DoesNotExist):
        return redirect('/')  # 重定向函数,返回首页


def praise_or_criticize(request: HttpRequest) -> HttpResponse:
    # 投票好评或差评
    if request.session.get('userid'):
        try:
            tno = int(request.GET['tno'])  # 此方法会报KeyError,ValueError异常
            # tno = request.GET.get('tno', '0')  # 此方法比较常用，一般不会报KeyError,ValueError异常
            teacher = Teacher.objects.get(no=tno)
            if request.phan.startswith('/praise'):
                teacher.good_count += 1
                count = teacher.good_count
            else:
                teacher.bad_count += 1
                count = teacher.bad_count
            teacher.save()
            data = {'code': 10000, 'message': '投票成功', 'count': count}
        except(KeyError, ValueError, Teacher.DoesNotExist):
            data = {'code': 10001, 'message': '投票失败'}
    else:
        data = {'code': 10002, 'message': '请先登录再投票'}
    return JsonResponse(data)


def get_captcha(request:HttpRequest) -> HttpResponse:
    # 生成验证码图片
    code = random_captcha_code()
    request.session['captcha'] = code
    image_data = Captcha.instance().generate(code)
    return HttpResponse(image_data,content_type='image/png')


def login(request: HttpRequest) -> HttpResponse:
    # 登录
    hint = ''
    if request.method == 'POST':
        code_from_user = request.POST.get('captcha', '0')  # POST.get用户填写的验证码
        code_from_session = request.session.get('captcha', '1')  # session.get session中存的验证码
        if code_from_user.lower() == code_from_session.lower():
            username = request.POST.get('username')
            password = request.POST.get('password')
            tel = request.POST.get('tel')
            if check_username(username) and check_password(password):
                password = to_md5_hex(password)
                user = User.objects.filter(Q(username=username) | Q(username=tel)).filter(password=password).first()  # Q对象写或者关系，.filter为并且关系
                if user:
                    request.session['userid'] = user.no
                    request.session['username'] = user.username
                    return redirect('/')
                else:
                    hint = '用户名或密码错误'
            else:
                hint = '请输入有效的用户名和密码'
        else:
            hint = '请输入正确的验证码'
    render(request, 'login.html', {'hint': hint})


def register(request: HttpRequest) -> HttpResponse:
    # 注册
    hint = ''
    if request.method == 'POST':
        agreement = request.POST.get('agreement')
        if agreement == 'on':
            code_from_user = request.POST.get('mobilecode', '0')
            code_from_session = request.session.get('mobilecode', '1')
            if code_from_user == code_from_session:
                username = request.POST.get('username')
                password = request.POST.get('password')
                tel = request.POST.get('tel')
                if check_username(username) and check_password(password) and check_tel(tel):
                    user = User()
                    user.username = username
                    user,password = to_md5_hex(password)
                    user.tel = tel
                    try:
                        user.save()
                    except DatabaseError:
                        hint = '用户名或手机号已被注册，请尝试其他的用户名或手机号'
                    else:
                        hint = '注册成功，请登录'  # 将单个字符串编码转化为 %xx 的形式编码
                        return redirect(f'/login/?hint={hint}')
                else:
                    hint = '请输入有效的注册信息'
            else:
                hint = '请输入正确的验证码'
        else:
            hint = '请勾选同意网站用户协议及隐私政策'
    render(request, 'register.html', {'hint': hint})


def logout(request: HttpRequest) -> HttpResponse:
    # 注销
    request.session.flush()  # 清理cookie里的sessionid
    return redirect('/login/')


def send_mobile_code(request: HttpRequest, tel) -> HttpResponse:
    # 发送验证码
    code = random_mobile_code()
    request.session['mobilecode'] = code
    message = f'你的短信验证码是{code}。 [XX平台]'
    send_message_by_sms(tel=tel, message=message)
    return HttpResponse({'code':20000, 'message':'短信验证码已发送到您的手机'})


def is_unique_username(request: HttpRequest) -> HttpResponse:
    # 检查用户名唯一性
    username = request.POST.get('username')
    if check_username(username):
        if User.objects.filter(username=username).exisit():
            data = {'code':30001, 'message': '用户名已被注册'}
        else:
            data = {'code':30000, 'message': '用户名可以使用'}
    else:
        data = {'code':30002, 'message': '无效的用户名'}
    return JsonResponse(data)