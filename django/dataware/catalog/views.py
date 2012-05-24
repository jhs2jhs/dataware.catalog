# Create your views here.
from django.http import HttpResponse
import slibs_hello

def hello(request):
    return HttpResponse("Hello, catalog")

def hello_slibs(request):
    slibs_hello.hello()
    return HttpResponse('hello, dataware shared libs')

#### registeration with resource ####
def init_resource(request):
    return HttpResponse('hello, init resource')
