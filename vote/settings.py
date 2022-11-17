"""
Django settings for vote project.

Generated by 'django-admin startproject' using Django 2.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'akjf49ryh+4+=9r&0ve@g$@ngs#q5&swesd77wi%xn(pq#sm%m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'debug_toolbar',  # 开发测试性能
    'rest_framework',  # DRF模型
    'polls',
]

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',  # 开发测试性能
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #添加自定义中间件(注意要写在SessionMiddleware配置下面)
    # 'polls.middlewares.check_login_middleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# # 开发测试性能
# DEBUG_TOOLBAR_CONFIG = {
#     # 引入jQuery库
#     'JQUERY_URL': 'http://cdn.bootcss.com/jquery/3.3.1/jquery.min.js',
#     # 工具栏是否折叠
#     'SHOW_COLLAPSED': True,
#     # 是否显示工具栏
#     'SHOW_TOOLBAR_CALLBACK': lambda x: True,
# }

ROOT_URLCONF = 'vote.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vote.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'edw',
        'HOST': 'rm-bp172xk000fzkol57to.mysql.rds.aliyuncs.com',
        'PORT': '3306',
        'USER': 'sa',
        'PASSWORD': 'Ab123456-',
        'CHARSET': 'utf-8',
        'TIME_ZONE': 'Asia/Chongqing',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Chongqing'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]

# # 接入redis缓存服务(调用缓存方法有两个,cache[]为默认缓存caches[]可以选择其他缓存)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         # 服务器的地址
#         'LOCATION': [
#             'redis:redis//47.104.31.138.5489/0',
#         ],
#         # 缓存中键的前缀(解决命名冲突的问题)
#         'KEY_PREFIX': 'vote',
#         # 缓存服务的配置参数
#         'OPTIONS': {
#             'CLIENT_CLASS':'django.redis.client.DefaultClient',
#             # 配置连接池(减少频繁的创建和释放Redis连接造成的网络开销)
#             'CONNECTION_POOL_KWARGS': {
#                 'max_connections': 512,
#             },
#             'PASSWORD':'Luohao.618',
#         }
#     },
#     'api': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         # 服务器的地址
#         'LOCATION': [
#             'redis:redis//47.104.31.138.5489/1',
#         ],
#         # 缓存中键的前缀(解决命名冲突的问题)
#         'KEY_PREFIX': 'vote:api',
#         # 缓存服务的配置参数
#         'OPTIONS': {
#             'CLIENT_CLASS':'django.redis.client.DefaultClient',
#             # 配置连接池(减少频繁的创建和释放Redis连接造成的网络开销)
#             'CONNECTION_POOL_KWARGS': {
#                 'max_connections': 512,
#             },
#             'PASSWORD':'Luohao.618',
#         }
#     },
# }

# # 使用缓存保存用户跟踪的session对象
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# # 指定使用那一组缓存服务来保存session对象
# SESSION_CACHE_ALIAS = 'default'
# # 指定session对象的过期时间(Redis键过期时间)
# SESSION_COOKIE_AGE = 1209600
# # 关闭浏览器窗口session自动过期(cookie自动消失)
# # SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# 日志级别：DEBUG < INFO < WARNING < ERROR < CRITICAL 日志级别越低，日志输出越详细
# 可以通过官方文档搜索logging查看日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # 日志处理器
    'handlers': {
        # 配置通过控制台输出日志（StreamHandler）
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    # 日志记录器,django.db为查看数据库日志
    'loggers': {
        'django.db': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}


# 自定义的路径名
LOGIN_REDIRECT_URLS = {
    '/praise/',
    '/criticize/',
    '/data/',
    '/export/',
}