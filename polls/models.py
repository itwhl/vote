# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Subject(models.Model):
    no = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    intro = models.CharField(max_length=1000)
    is_hot = models.BooleanField(default=False)  # This field type is a guess.

    # 对象变成字符串形式
    def __str__(self):
        return self.name

    class Meta:    # 模型元信息
        managed = False
        db_table = 'tb_subject'


SEX_OPTIONS = ((True, '男'), (False, '女'))


class Teacher(models.Model):
    no = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    sex = models.BooleanField(choices=SEX_OPTIONS,default=True)
    intro = models.CharField(max_length=1000)
    good_count = models.IntegerField(default=0, verbose_name='好评数')
    bad_count = models.IntegerField(default=0, verbose_name='差评数')
    sno = models.ForeignKey(to=Subject, on_delete=models.DO_NOTHING, verbose_name='所属学科')


    class Meta:
        managed = False
        db_table = 'tb_teacher'


class User(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='编号')
    username = models.CharField(max_length=20, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='密码')
    tel = models.CharField(max_length=20, unique=True, verbose_name='手机号')
    reg_date = models.DateTimeField(auto_now_add= True, verbose_name='注册时间')

    class Meta:
        db_table = 'tb_user'