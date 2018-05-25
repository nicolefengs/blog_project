#coding=utf-8
from django.contrib import admin
# Register your models here.
from blog.models import *


class ArticleAdmin(admin.ModelAdmin):
    #只在Ariticle里显示三列
    #fields = ('title','desc','content')
    #除开这些列其他的都显示
    #exclude = ('title','desc','content')
   #文章界面只显示文章
    list_display = ('title','desc','click_count',)
    list_display_links = ('title','desc',)

    list_editable = ('click_count',)

    fieldsets = (
        (None,{
            'fields':('title','desc','content',)
        }),
        ('高级设置',{
            'classes':('collapse',),
            'fields':('user','category','tag','is_recommend',)
        }),
    )

    class Media:
        js=(
            '/static/js/kindeditor/kindeditor-min.js',
            '/static/js/kindeditor/lang/zh_CN.js',
            '/static/js/kindeditor/config.js',

        )


admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Article,ArticleAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Links)
admin.site.register(Ad)