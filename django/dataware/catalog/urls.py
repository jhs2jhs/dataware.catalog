from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^hello', 'catalog.views.hello'),
    url(r'^slibs', 'catalog.views.hello_slibs'),

    url(r'^regist$', 'catalog.views.regist'),

)
