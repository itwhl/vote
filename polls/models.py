# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Subject(models.Model):
    no = models.AutoField(primary_key=True, verbose_name='编号')
    name = models.CharField(max_length=50, verbose_name='名称')
    intro = models.CharField(max_length=1000, verbose_name='介绍')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门')

    class Meta:
        managed = False
        db_table = 'tb_subject'


SEX_OPTIONS = (
    (True, '男'),
    (False, '女')
)


class Teacher(models.Model):
    no = models.AutoField(primary_key=True, verbose_name='编号')
    name = models.CharField(max_length=20, verbose_name='姓名')
    sex = models.BooleanField(default=True, choices=SEX_OPTIONS, verbose_name='性别')
    intro = models.CharField(max_length=1000, verbose_name='介绍')
    good_count = models.IntegerField(default=0, db_column='gcount', verbose_name='好评数')
    bad_count = models.IntegerField(default=0, db_column='bcount', verbose_name='差评数')
    subject = models.ForeignKey(to=Subject, on_delete=models.DO_NOTHING, db_column='sno', verbose_name='所属学科')

    class Meta:
        managed = False
        db_table = 'tb_teacher'


class User(models.Model):
    no = models.AutoField(primary_key=True, db_column='id', verbose_name='编号')
    username = models.CharField(unique=True, max_length=20)
    password = models.CharField(max_length=32)
    tel = models.CharField(max_length=20, unique=True)
    photo = models.CharField(max_length=1024, default='', verbose_name='用户头像')
    reg_date = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    is_locked = models.BooleanField(default=False, verbose_name='是否禁用')
    counter = models.IntegerField(default=5, verbose_name='剩余票数')

    class Meta:
        db_table = 'tb_user'
