from django.http import HttpResponse
import logging
logger = logging.getLogger(__name__)

def hello_world(request):
    return HttpResponse('Hello World')

