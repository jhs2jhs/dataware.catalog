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
from libauth.views import regist_steps, regist_dealer
from libauth.views import method_regist_init, method_registrant_request, method_registrant_owner_redirect, method_registrant_owner_grant, method_registrant_confirm

def hello(request):
    #return HttpResponse("Hello, catalog")
    return render_to_response("hello_test.html", {'name': 'catalog'})

def hello_slibs(request):
    slibs_hello.hello()
    return HttpResponse('hello, dataware shared libs')

regist_callback_me = 'http://localhost:8000/catalog/regist'

class regist_dealer_catalog(regist_dealer):
    def regist_init(self):
        return method_regist_init(self.request)
    def registrant_request(self): 
        return method_registrant_request(self.request, regist_callback_me)
    def register_owner_redirect(self): pass
    def register_owner_grant(self): pass
    def register_grant(self): pass
    def registrant_owner_redirect(self): 
        return method_registrant_owner_redirect(self.request, regist_callback_me)
    def registrant_owner_grant(self): 
        return method_registrant_owner_grant(self.request, regist_callback_me)
    def registrant_confirm(self): 
        return method_registrant_confirm(self.request, regist_callback_me)
    def register_activate(self): pass
    def regist_finish(self): pass
  
#@login_required  
def regist(request):
    # if no correct status is matched
    return regist_steps(regist_dealer_catalog(request), request)
    
    
    
