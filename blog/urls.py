from django.conf.urls import url
from blog.views import *



urlpatterns = [
    url(r'^$',index,name="index"),
    url(r'^archive/$', archive, name="archive"),
    url(r'^article/$', article, name="article"),
    url(r'^comment/post/$', comment_post, name='comment_post'),
    url(r'^classify/$', classify, name='classify'),
    url(r'^reg', do_reg, name='reg'),
    url(r'^login', do_login, name='login'),
    url(r'^logout$', do_logout, name='logout'),
    url(r'^search$', search, name='search'),
    url(r'^about$', about, name='about'),
    url(r'^tags$', tags, name='tags'),
    url(r'^friendly$', friendly, name='friendly'),
]