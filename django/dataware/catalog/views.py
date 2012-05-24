# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
import slibs_hello
import dwlib
from dwlib import url_keys

def hello(request):
    return HttpResponse("Hello, catalog")

def hello_slibs(request):
    slibs_hello.hello()
    return HttpResponse('hello, dataware shared libs')

# user need to login first
#### registeration with resource ####
def init_resource(request):
    resource_url = 'http://localhost:8001/resource'
    resource_callback = 'catalog_register'
    catalog_callback = 'resource_grant'
    catalog_temp_id = dwlib.token_create(resource_url, resource_callback) # may need to add user login to identify, otherwise, different user can have same token at same time. 
    access_scope_action = 'read, write' # to be confirmed
    access_scope_content = 'photo, status' # to be confirmed
    params = {
        url_keys.catalog_callback:catalog_callback,
        url_keys.catalog_temp_id:catalog_temp_id,
        url_keys.access_scope_action:access_scope_action,
        url_keys.access_scope_content:access_scope_content
        }
    url_params = dwlib.urlencode(params)
    url = '%s/%s?%s'%(resource_url, resource_callback, url_params)
    # before redirection, needs to save variable in database first. 
    return HttpResponseRedirect(url)
