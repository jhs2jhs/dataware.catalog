# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
import slibs_hello
import dwlib
from dwlib import url_keys, request_get, url_keys
from libauth.models import Registration as CRR # TODO needs to delete later
from libauth.models import Registration
from libauth.models import regist_steps, regist_dealer, REGIST_STATUS, REGIST_TYPE, REQUEST_MEDIA
from libauth.models import find_key_by_value_regist_type, find_key_by_value_regist_status, find_key_by_value_regist_request_media

def hello(request):
    return HttpResponse("Hello, catalog")

def hello_slibs(request):
    slibs_hello.hello()
    return HttpResponse('hello, dataware shared libs')

regist_callback_me = 'http://localhost:8000/catalog/regist'

class regist_dealer_catalog(regist_dealer):
    def regist_init(self):
        registrant_init_action = request_get(self.request.REQUEST, url_keys.registrant_init_action)
        register_callback = request_get(self.request.REQUEST, url_keys.regist_callback)
        regist_type = request_get(self.request.REQUEST, url_keys.regist_type)
        registrant_request_scope = request_get(self.request.REQUEST, url_keys.registrant_request_scope)
        registrant_request_reminder = request_get(self.request.REQUEST, url_keys.registrant_request_reminder)
        registrant_request_media = request_get(self.request.REQUEST, url_keys.registrant_request_media)
        registrant_request_user_public = request_get(self.request.REQUEST, url_keys.registrant_request_user_public)
        if registrant_init_action == None or (registrant_init_action != url_keys.registrant_init_action_generate and registrant_init_action != url_keys.registrant_init_action_request): # TODO or if error happened here
            register_callback = 'http://localhost:8001/resource/regist'
            registrant_request_scope = "{'action':'read, write', 'content':'blog, status'}" # to be confirmed
            registrant_request_reminder = ''
            registrant_request_user_public = ''
            c = {
                'registrant_init_action': {
                    'label': url_keys.registrant_init_action,
                    'value': url_keys.registrant_init_action_generate,
                    },
                'register_callback':{
                    'label': url_keys.regist_callback,
                    'value': register_callback,
                    },
                'registrant_request_scope':{
                    'label': url_keys.registrant_request_scope,
                    'value': registrant_request_scope,
                    },
                'regist_type':{
                    'label': url_keys.regist_type,
                    'catalog_resource': REGIST_TYPE.catalog_resource,
                    'client_catalog': REGIST_TYPE.client_catalog,
                    },
                'regist_status':{
                    'label': url_keys.regist_status,
                    'value': REGIST_STATUS.init,
                    },
                'registrant_request_reminder': {
                    'label': url_keys.registrant_request_reminder,
                    'value': registrant_request_reminder,
                    },
                'registrant_request_user_public': {
                    'label': url_keys.registrant_request_user_public,
                    'value': registrant_request_user_public,
                    },
                'registrant_request_media' : url_keys.registrant_request_media,
                'request_media': { r:{'label':r, 'value':r, 'desc':r} for k, r in REQUEST_MEDIA.iteritems()},
                }
            context = RequestContext(self.request, c)
            return render_to_response('regist_init.html', context)
        if registrant_init_action == url_keys.registrant_init_action_generate:
        # if the input is correct, need to check regist_type
            user = self.request.user
            registrant_request_token = dwlib.token_create_user(register_callback, user.id) 
            params = {
                url_keys.regist_status: REGIST_STATUS.registrant_request,
                url_keys.regist_type: REGIST_TYPE.catalog_resource,
                url_keys.regist_callback: regist_callback_me,
                url_keys.registrant_request_token: registrant_request_token,
                url_keys.registrant_request_scope: registrant_request_scope,
                url_keys.registrant_request_reminder: registrant_request_reminder,
                url_keys.registrant_request_user_public: registrant_request_user_public,
                url_keys.registrant_request_media: registrant_request_media,
                }
            url_params = dwlib.urlencode(params)
            url = '%s?%s'%(register_callback, url_params)
            regist_type_key = find_key_by_value_regist_type(regist_type)
            regist_status_key = find_key_by_value_regist_status(REGIST_STATUS.init)
            print url
            print self.request.REQUEST
            print registrant_request_media
            registrant_request_media_key = find_key_by_value_regist_request_media(registrant_request_media)
            print registrant_request_media_key
            obj, created = Registration.objects.get_or_create(
                regist_type=regist_type_key, 
                regist_status=regist_status_key, 
                registrant_request_token=registrant_request_token, 
                registrant_request_scope=registrant_request_scope, 
                registrant_callback=regist_callback_me, 
                register_callback=register_callback, 
                registrant_request_reminder=registrant_request_reminder, 
                registrant_request_user_public=registrant_request_user_public,
                registrant_request_media=registrant_request_media_key,
                user=user)
            c = {
                'request_url': {
                    'label': 'regist_request_url',
                    'value': url,
                    },
                'registrant_init_action': {
                    'label': url_keys.registrant_init_action,
                    'value': url_keys.registrant_init_action_request,
                    },
                'regist_status':{
                    'label': url_keys.regist_status,
                    'value': REGIST_STATUS.init,
                    },
                }
            context = RequestContext(self.request, c)
            return render_to_response('regist_init_generate.html', context)
        if registrant_init_action == url_keys.registrant_init_action_request:
            request_url = request_get(self.request.REQUEST, "regist_request_url")
            print request_url
            return HttpResponseRedirect(request_url)
    def registrant_request(self): 
        return HttpResponseRedirect('http://www.baidu.com')
    def register_owner_redirect(self): pass
    def register_owner_grant(self): pass
    def register_grant(self): pass
    def registrant_owner_redirect(self): pass
    def registrant_owner_grant(self): pass
    def registrant_confirm(self): pass
    def register_activate(self): pass
    def regist_finish(self): pass
    
@login_required
def regist(request):
    # if no correct status is matched
    return regist_steps(regist_dealer_catalog(request), request)
    


@login_required
def resource_grant(request):
    params = request.REQUEST
    catalog_request_token = request_get(params, url_keys.catalog_request_token)
    resource_access_token = request_get(params, url_keys.resource_access_token)
    resource_request_token = request_get(params, url_keys.resource_request_token)
    resource_validate_code = request_get(params, url_keys.resource_validate_code)
    resource_callback = request_get(params, url_keys.resource_callback)
    resource_access_scope = request_get(params, url_keys.resource_access_scope)

    crr = CRR.objects.get(catalog_request_token=catalog_request_token)
    user_id = crr.user.id
    catalog_access_token = dwlib.token_create_user(resource_callback, user_id)
    catalog_validate_token = 'expire in 10 hours'
    crr.catalog_access_token = catalog_access_token
    crr.catalog_validate_code = catalog_validate_token
    crr.resource_access_token = resource_access_token
    crr.resource_request_token = resource_request_token
    crr.resource_validate_code = resource_validate_code
    crr.resource_callback = resource_callback
    crr.resource_access_scope = resource_access_scope
    crr.registration_status = 4 # 4=auth
    crr.save()
    
    params = {
        url_keys.catalog_access_token:catalog_access_token,
        url_keys.catalog_validate_token:catalog_validate_token,
        url_keys.resource_access_token:resource_access_token,
        }
    url_params = dwlib.urlencode(params)
    url = '%s?%s'%(resource_callback, url_params)
    return HttpResponseRedirect(url)
    


    
    
