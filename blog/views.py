# -*- coding:utf-8 -*-
import json
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password   #密码加密
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render, redirect
import logging
from django.conf import settings
from blog.forms import *
from blog.models import *
from pyquery import PyQuery as pq

logger=logging.getLogger("blog.views")
# Create your views here.


def global_setting(request):
    SITE_NAME= settings.SITE_NAME
    SITE_DESC= settings.SITE_DESC
    # 分类信息获取（导航数据）
    category_list = Category.objects.all()
    #广告数据
    ad = Ad.objects.all()
    #文章归档数据
    archive_list = Article.objects.distinct_date()
    # 标签云数据
    tags=Tag.objects.all()
    #友情连接
    links=Links.objects.all()
    #站长推荐
    recommends = Article.objects.filter(is_recommend=True)
    recommend=image_path(recommends)
    # 评论排行
    comment_count_list=Comment.objects.values('article').annotate(commentcount=Count('article')).order_by('-commentcount')
    article_comment_lists= [Article.objects.get(pk=comment['article']) for comment in comment_count_list]
    article_comment_list = image_path(recommends)
    return locals()


def image_path(articless):
    img_path = list()
    temp=articless.values('content')
    for i in range(len(temp)):
        html = pq(temp[i]['content'])
        img_path.append(pq(html)('img').attr('src'))
    img_paths = list()
    for a, b in zip(articless.values(), img_path):
        a.update(im=b)
        img_paths.append(a)
    for ar,im in zip(articless,img_paths):
            im['username']=ar.user.username
    return img_paths

def index(request):
    try:
        #最新文章数据
        article_list=Article.objects.all()
        article_lists = image_path(article_list)
        article_list =getPage(request, article_lists)
        # 文章排行榜数据
        articless = Article.objects.all().order_by('-click_count')
        temp = Article.objects.filter().order_by('-click_count').values('content')  # values获取Article数据表中的content字段内容
        img_paths=image_path(articless)
    except Exception as e:
        logger.error(e)
    return render(request,"index.html",locals())



def archive(request):
    try:
    #先获取客户端提交的信息
        year=request.GET.get("year",None)
        month = request.GET.get("month", None)
        article_list = Article.objects.filter(date_publish__icontains=year+'-'+month)
        article_list = getPage(request, article_list)
    except Exception as e:
        print(e)
        logger.error(e)
    return render(request,'archive.html',locals())


def getPage(request,article_list):
    paginator = Paginator(article_list, 1)

    try:
        page = int(request.GET.get('page', 1))
        article_list = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list



def getPagess(request,article_list):
    paginator = Paginator(article_list, 1)

    try:
        page = int(request.GET.get('page', 6))
        article_list = paginator.page(6)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list





#文章详情
def article(request):
    try:
        #获取文章id
        id =request.GET.get('id',None)
        try:
            articles=Article.objects.get(pk=id)
        except Article.DoesNotExist:
            return render(request,'failure.html',{'reason':'没有找到对应的文章'})

        #评论表单
        comment_form=CommentForm({'author':request.user.username,
                                  'email':request.user.email,
                                  'url':request.user.url,
                                  'article':id} if request.user.is_authenticated() else{"article":id})
        # 获取评论信息
        comments=Comment.objects.filter(article=articles).order_by('id')
        comment_list=[]
        for comment in comments:
            for item in comment_list:
                if not hasattr(item,'children_comment'):
                    setattr(item,'children_comment',[])
                if comment.pid==item:
                    item.children_comment.append(comment)
                    break
            if comment.pid is None:
                comment_list.append(comment)
        #下一页上一页
        blogs = Article.objects.all()

        pageid = request.GET.get('id')
        art=Article.objects.all()
        pagelist=list()
        for a in art:
            pagelist.append(a.id)
        for p in range(len(pagelist)):
            if int(pageid) == pagelist[p]:
                print(p)
                print(len(pagelist))
                if p-1 >= 0 and p+1<len(pagelist):
                    pageup=pagelist[p-1]
                    pagedown=pagelist[p+1]
                    arts = Article.objects.get(id=pageup)
                    artss = Article.objects.get(id=pagedown)
                elif p-1 < 0:
                    pageup = None
                    pagedown = pagelist[p + 1]
                    artss = Article.objects.get(id=pagedown)
                elif p+1== len(pagelist) :
                    pageup = pagelist[p-1]
                    print(pageup)
                    arts = Article.objects.get(id=pageup)
                    pagedown = None



    except Exception as e:
        print(e)
        logger.error(e)
    return render(request,'content.html',locals())

#提交评论
def comment_post(request):
    try:
        comment_form=CommentForm(request.POST)
        if comment_form.is_valid():
            #获取表单信息
            comment=Comment.objects.create(username=comment_form.cleaned_data["author"],
                                           email=comment_form.cleaned_data["email"],
                                           url=comment_form.cleaned_data["url"],
                                           content=comment_form.cleaned_data["comment"],
                                           article_id=comment_form.cleaned_data["article"],
                                           user=request.user if request.user.is_authenticated() else None )
            comment.save()
        else:
            return render(request,'content.html',{'reason':comment_form.errors})
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

def classify(request):
    try:
        # 获取文章id
        id = request.GET.get('id', None)
        try:

            article_list = Article.objects.filter(category=id)
            article_list = getPage(request, article_list)

        except Article.DoesNotExist:
            return render(request, 'failure.html', {'reason': '没有找到对应的文章'})

    except Exception as e:
        print(e)
        logger.error(e)
    return render(request, 'index.html', locals())


def do_reg(request):
    try:
        if request.method=='POST':
            reg_form =RegForm(request.POST)
            if reg_form.is_valid():
                user=User.objects.create(username=reg_form.cleaned_data["username"],
                                         email=reg_form.cleaned_data["email"],
                                         url=reg_form.cleaned_data["url"],
                                         password=make_password(reg_form.cleaned_data["password"]),
                                         )
                user.save()
                user.backend='django.contrib.auth.backends.ModelBackend'#指定默认的登录验证方式
                login(request,user)
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form=RegForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'reg.html', locals())


def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                username=login_form.cleaned_data["username"]
                password=login_form.cleaned_data["password"]
                user=authenticate(username=username,password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason':  "登录验证失败"})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())


def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print(e)
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])


def search(request):
    try:
        if request.method == "POST":
            key = request.POST.get('searchkey')
        # 最新文章数据
        article_list = Article.objects.filter(title__contains=key)

        article_lists = image_path(article_list)
        article_list = getPage(request, article_lists)
    except Exception as e:
        logger.error(e)
    return render(request, 'search.html', locals())

def about(request):
    return render(request, 'about.html', locals())

def tags(request):
    return render(request, 'tags.html', locals())

def friendly(request):
    return render(request, 'friendly.html', locals())

