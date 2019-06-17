from rest_framework.views import APIView
from .tasks import rebuild_task
import logging
logger = logging.getLogger(__name__)
from django.http import JsonResponse

#call to kick off the reindex of a doc type
class queue_rebuild(APIView):
    def get(self, request):
        try:
            queue = request.GET['env'] + "-queue-name.fifo"
            rebuild_task.apply_async(
                (request.GET['env'],request.GET['type'],request.GET['dev_domain'],request.GET['id']),priority=0, queue=queue)
            return JsonResponse({"status" : "true"})
        except Exception as e:
            logger.error(e)
            return JsonResponse({"status" : "false", "message" : e})

#accepts array of ids and rebuilds them
class rebuild_ids(APIView):
    def post(self, request):
        try:
            data = request.data
            env = data.get('env')
            type = data.get('type')
            ids = data.get('ids')
            dev_domain = data.get('dev_domain')

            queue = env + "-queue-name.fifo"
            for id in ids:
                rebuild_task.apply_async((env, type, dev_domain, id), priority=9,queue=queue)
            return JsonResponse({"status" : "true"})
        except Exception as e:
            logger.error(e)
            return JsonResponse({"status" : "false", "message" : e})