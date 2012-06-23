# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import slibs_hello
import dwlib
from dwlib import url_keys, request_get, url_keys, error_response
from libauth.models import Registration
from libauth.models import REGIST_STATUS, REGIST_TYPE, REQUEST_MEDIA, TOKEN_TYPE
from libauth.models import find_key_by_value_regist_type, find_key_by_value_regist_status, find_key_by_value_regist_request_media
from libauth.views import regist_steps

def hello(request):
    #return HttpResponse("Hello, catalog")
    return render_to_response("hello_test.html", {'name': 'catalog'})

def hello_slibs(request):
    slibs_hello.hello()
    return HttpResponse('hello, dataware shared libs')

regist_callback_me = 'http://localhost:8000/catalog/regist'
  
def regist(request):
    return regist_steps(request, regist_callback_me)
    
    
    
