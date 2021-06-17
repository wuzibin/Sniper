from django.http import JsonResponse
from dbmanager.models import DBConnInfo


def db_info(request):
    try:
        if request.method == "GET":
            query_dbinfo = DBConnInfo.objects.all()
            ret_json = []
            for dbinfo in query_dbinfo:
                ret_json.append({"pk": dbinfo.db_id, "db_nickname": dbinfo.db_nickname})
            return JsonResponse({"code": 0, "dbinfo": ret_json, "msg": "query database info success."},
                                safe=False)

        if request.method == "POST":
            req = request.POST.dict()
            print(req)
            print(request.body)
            return JsonResponse({"code": 0, "msg": "提交成功"})

    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})
