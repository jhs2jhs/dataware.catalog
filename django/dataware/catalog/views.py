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

'''
def method_registrant_confirm(request):
    print request.REQUEST
    user = request.user
    registrant_redirect_token = request_get(request.REQUEST, url_keys.registrant_redirect_token)
    regist_type = request_get(request.REQUEST, url_keys.regist_type)
    try:
        print request_get(request.REQUEST, url_keys.registrant_request_action)
        print url_keys.registrant_request_action_confirm
        if request_get(request.REQUEST, url_keys.registrant_request_action) == url_keys.registrant_request_action_confirm:
            print "hello"
            registrant_access_token = request_get(request.REQUEST, url_keys.registrant_access_token)
            #print registrant_request_token
            registration = Registration.objects.get(registrant_access_token=registrant_access_token)
            print registration
            if registration.user != user :
                return error_response(2, ("user"))
            registrant_access_token = request_get(request.REQUEST, url_keys.registrant_access_token)
            if registration.registrant_access_token != registrant_access_token:
                return error_response(2, (url_keys.registrant_access_token))
            params = {
                url_keys.regist_status: REGIST_STATUS.register_activate,#TODO some error here
                url_keys.regist_type: regist_type,
                url_keys.regist_callback: regist_callback_me,
                url_keys.registrant_access_token: registration.registrant_access_token,
                url_keys.registrant_access_validate: registration.registrant_access_validate,
                url_keys.register_access_token: registration.register_access_token,
                }
            url_params = dwlib.urlencode(params)
            url = '%s?%s'%(registration.register_callback, url_params)
            return HttpResponseRedirect(url)
        registration = Registration.objects.get(registrant_redirect_token=registrant_redirect_token)
        regist_status_key = find_key_by_value_regist_status(REGIST_STATUS.registrant_owner_grant)
    except ObjectDoesNotExist:
        return error_response(3, (url_keys.registrant_redirect_token, registrant_redirect_token))
    regist_status_key = find_key_by_value_regist_status(REGIST_STATUS.registrant_confirm)
    registration.regist_status = regist_status_key
    registrant_access_token = dwlib.token_create_user(registration.register_callback, TOKEN_TYPE.access, user.id)
    registrant_access_validate = registration.register_request_scope #TODO need to expand here
    registration.registrant_access_token = registrant_access_token
    registration.registrant_access_validate = registrant_access_validate
    registration.save()
    params = {
        url_keys.regist_status: REGIST_STATUS.registrant_confirm, # for mutual registraiton it is different, user need to decide here, TODO, if it now ok to call this status?
        url_keys.regist_type: regist_type,
        url_keys.regist_callback: regist_callback_me,
        url_keys.registrant_access_token: registrant_access_token,
        url_keys.registrant_access_validate: registrant_access_validate,
        url_keys.register_access_token: registration.register_access_token,
        } 
    url_params = dwlib.urlencode(params)
    url = '%s?%s'%(registration.register_callback, url_params)
    c = {
        'regist_grant_url': url,
        'registrant_request_action':{
            'label': url_keys.registrant_request_action,
            'confirm': url_keys.registrant_request_action_confirm,
            },
        'registrant_access_token': {
            'label': url_keys.registrant_access_token,
            'value': registrant_access_token,
            },
        'registrant_access_validate': {
            'label': url_keys.registrant_access_validate,
            'value': registrant_access_validate,
            },
        'regist_status':{
            'label': url_keys.regist_status,
            'value': REGIST_STATUS.registrant_confirm,
            },
        'regist_type':{ # need to add into template files
            'label': url_keys.regist_type,
            'value':regist_type,
            },
        'regist_confirm_token': {
            'label': url_keys.registrant_access_token,
            'value': registration.registrant_access_token,
            },
        }
    context = RequestContext(request, c)
    return render_to_response("regist_confirm.html", context)
    #return HttpResponse("hello grant")
'''



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
    
    
    
