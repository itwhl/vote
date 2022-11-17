# DRF的模型序列化器
from rest_framework.serializers import ModelSerializer

from polls.models import Subject, Teacher


# 自定义序列化器
class SubjectSerializer(ModelSerializer):

    class Meta:
        model = Subject
        fields = '__all__'


class SubjectSimpleSerializer(ModelSerializer):

    class Meta:
        model = Subject
        fields = ('no', 'name')


class TeacherSerializer(ModelSerializer):

    class Meta:
        model = Teacher
        exclude = ('subject', )