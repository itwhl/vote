import pymysql
import os
import celery
#
# from celery.schedules import crontab
# from django.conf import settings
# # pymysql配置成myslqclien
pymysql.install_as_MySQLdb()

# 注册环境变量（在Django项目中使用Celery需要先注册Djang配置文件）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vote.settings')

# 创建Celery对象，指定模块名、消息代理（消息队列服务）
# app = celery.Celery(
#     # 模块的名字
#     main='vote',
#     # 消息代理（消息队列提供者）
#     broker='redis//:password@47.104.31.138:5489/0',
#     # 持久化（储存异步或定时任务执行结果）
#     backend='redis//:password@47.104.31.138:5489/1',
# )
#
# # # 通过一个字典对象传入Celery对象的配置参数
# # app.conf.updata({})
# # # 从Django项目的配置文件中读取Celery相关配置
# # app.config_from_object('django.conf:settings')
# # # 从指定的文件（例如celery_config.py）中读取Celery配置信息
# # app.config_from_object('celery_config')
#
# # # 自动从指定的应用中发现任务（异步任务/定时任务） 被@app.task装饰器标注的函数就是异步任务或定时任务
# # app.autodiscover_tasks(('polls', ))
# # # 自动从注册的应用中发现任务（异步任务/定时任务）
# # app.autodiscover_tasks(settings.INSTALLED_APPS)
#
#
# # 配置定时任务
# # 定时任务时消息的生产者，需要通过下面命令来激活定时任务
# # celery -A vote beat -l debug(显示日志) -P eventlet(windows事件循环)
# #  如果只有生产者没有消费者，那么消息就会积压在消息队列中
# # celery -A vote worker -l debug(显示日志) -P eventlet(windows事件循环)
# app.conf.update(
# 配置celery对象，指定接受json序列化和pickle序列化
#     accept_content=['json', 'pickle'],
#     timezone=settings.TIME_ZONE,
#     enable_utc=True,
#     beat_schedule={
#         'work-at-midnight': {
#             'task': 'polls.tasks.reset_users_counter',
#             # Linux操作系统中可以用crontab -e 编辑克龙表达式
#             # Linux操作系统中 ---> 分 时 日 月 周
#             # celery中的crontab构造器 ---> 默认是 分 时 周 日 月
#             'schedule': crontab(hour='0', minute='0'),  # 每天的0时0分执行
#         },
#         # 'work-at-friday': {
#         #     'task': 'polls.tasks.check_inactive_users',
#         #     'schedule': crontab( day_of_week='5', hour='23', minute='0'),  # 周五的23时0分执行
#         # },
#     },
# )