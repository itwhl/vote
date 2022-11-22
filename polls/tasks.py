# from datetime import timedelta
#
# from django.db.models import Q
# from django.utils import timezone
#
# from polls.models import User
# from vote import app
#
#
# # 给用户重置票数
# @app.task
# def reset_users_counter():
#     User.objects.filter(is_locked=False).update(counter=5)
#
#
# # # 检查活跃用户
# # @app.task
# # def check_inactive_users():
# #     thirty_days_ago = timezone.now() - timedelta(days=30)  # 30天以前的时间
# #     User.objects,filter(
# #         Q(last_visit__isnull=True) | Q(last_visit__lt=thirty_days_ago)
# #     ).filter(is_locked=False).updata(is_locked=True)