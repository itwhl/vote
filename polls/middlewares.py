from django.shortcuts import redirect
from django.http import JsonResponse
from vote.settings import LOGIN_REDIRECT_URLS


# 自定义中间件的写法就是装饰器的写法，只不过被装饰的是视图函数，第一个参数是HttpRequest对象，其他跟装饰器是完全一样的
def check_login_middleware(get_response):

    def middleware(request, *args, **kwargs):
        if request.path in LOGIN_REDIRECT_URLS and request.session.get('userid') is None:
            if request.is_ajxa():
                return JsonResponse({'code': 10002, 'message': '请先登录'})
            else:
                return redirect('/login/?hint=请先登录')
        response = get_response(request, *args, **kwargs)
        return response

    return middleware