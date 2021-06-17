from django.http import JsonResponse
from apimanager.models import APIInfo


def api_info(request):
    try:
        if request.method == "GET":
            query_apiinfo = APIInfo.objects.all()
            ret_json = []
            for apiinfo in query_apiinfo:
                ret_json.append({"pk": apiinfo.api_id, "api_nickname": apiinfo.api_nickname})
            return JsonResponse({"code": 0, "apiinfo": ret_json, "msg": "query API info success."},
                                safe=False)

        if request.method == "POST":
            req = request.POST.dict()
            print(req)
            print(request.body)
            return JsonResponse({"code": 0, "msg": "提交成功"})

    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})
