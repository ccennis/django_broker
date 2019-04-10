from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import HttpResponse
from .tasks import rebuild_task

#call to kick off the reindex of a doc type
def queue_rebuild(request,env,type,dev_domain,id):
    queue = env + "-queue-name.fifo"
    rebuild_task.apply_async((env,type,dev_domain,id),priority=0, queue=queue)
    return HttpResponse("queued")

#accepts array of ids and rebuilds them
class rebuild_ids(APIView):
    def post(self, request):
        data = request.data
        env = data.get('env')
        type = data.get('type')
        ids = data.get('ids')
        dev_domain = data.get('dev_domain')

        request.session['var_type'] = type
        request.session['environment'] = env
        request.session['dev_domain_var'] = dev_domain

        queue = env + "-queue-name.fifo"
        for id in ids:
            rebuild_task.apply_async((env, type, dev_domain, id), priority=9,queue=queue)
        return Response(data="queued")