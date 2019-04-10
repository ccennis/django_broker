from rest_framework.views import APIView
from rest_framework.response import Response
from .builder import drop_recreate_index
from django.http import HttpResponse
from .tasks import full_reindex_task

def drop_recreate(request,env,type):
    drop_recreate_index(env, type)
    return HttpResponse("true")

class reindex_all(APIView):
    def post(self, request):

        request.session.flush()

        data = request.data
        env = data.get('env')
        type = data.get('type')
        dev_domain = data.get('dev_domain')

        request.session['var_type'] = type
        request.session['environment'] = env
        request.session['dev_domain_var'] = dev_domain

        queue = env + "-queue-name.fifo"
        full_reindex_task.apply_async((env, type, dev_domain), priority=0, queue=queue)

        return Response(data="acknowledged")