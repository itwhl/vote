# 将模型注册到Django自带的管理平台

from django.contrib import admin

from polls.models import Subject, Teacher


class SubjectModeAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'intro')
    ordering = ('no',)


class TeacherModeAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'sno', 'intro')
    ordering = ('no', )


admin.site.register(Subject, SubjectModeAdmin)
admin.site.register(Teacher, TeacherModeAdmin)

