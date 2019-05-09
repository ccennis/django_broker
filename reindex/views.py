from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from .tasks import full_reindex_task
from django.views.decorators.csrf import csrf_exempt
from .builder import ReindexClass

class reindex_all(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        env = data.get('env')
        type = data.get('type')
        dev_domain = data.get('dev_domain')

        queue = env + "-queue-name.fifo"
        full_reindex_task.apply_async((env, type, dev_domain), priority=0, queue=queue)

        return Response(data="acknowledged")

class copy_all(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        env = data.get('env')
        type = data.get('type')
        dev_domain = data.get('dev_domain')

        queue = env + "-queue-name.fifo"
        reindexer = ReindexClass(env, type, dev_domain)
        reindexer.copy_index()

        return Response(data="acknowledged")