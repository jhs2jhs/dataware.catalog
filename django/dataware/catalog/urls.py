from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^hello', 'catalog.views.hello'),
    url(r'^slibs', 'catalog.views.hello_slibs'),

    # registeration with resource
    # INIT
    url(r'^init_resource', 'catalog.views.init_resource'),
    # AUTH
    url(r'^resource_grant', 'catalog.views.resource_grant'),

)
