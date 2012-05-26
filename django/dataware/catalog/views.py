# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import slibs_hello
import dwlib
from dwlib import url_keys, request_get, url_keys
from libauth.models import CatalogResourceRegistration as CRR

def hello(request):
    return HttpResponse("Hello, catalog")

def hello_slibs(request):
    slibs_hello.hello()
    return HttpResponse('hello, dataware shared libs')

# user need to login first
#### registeration with resource ####
@login_required
def init_resource(request):
    resource_callback = 'http://localhost:8001/resource/catalog_register'
    catalog_callback = 'http://localhost:8000/catalog/resource_grant'
    catalog_request_token = dwlib.token_create(resource_callback) # may need to add user login to identify, otherwise, different user can have same token at same time. 
    catalog_access_scope = "{'action':'read, write', 'content':'blog, status'}" # to be confirmed
    params = {
        url_keys.catalog_callback:catalog_callback,
        url_keys.catalog_request_token:catalog_request_token,
        url_keys.catalog_access_scope:catalog_access_scope,
        }
    url_params = dwlib.urlencode(params)
    url = '%s?%s'%(resource_callback, url_params)
    #crr = CRR(catalog_callback=catalog_callback, catalog_request=str(catalog_temp_id), catalog_access_scope=catalog_access_scope)
    #print crr
    user = request.user
    obj, created = CRR.objects.get_or_create(catalog_callback=catalog_callback, catalog_request_token=catalog_request_token, catalog_access_scope=catalog_access_scope, user=user, registration_status=1) # 1=request
    return HttpResponseRedirect(url)

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
    


    
    
