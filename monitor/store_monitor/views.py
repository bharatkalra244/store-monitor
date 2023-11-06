from django.shortcuts import render
from django.http import JsonResponse
from .models import StoreTimezone
import random
import string
# Create your views here.

def triggerReport(request):
    data = StoreTimezone.objects.all()
    dict_data = []
    for datum in data:
        dict_data.append({
            "store_id": datum.store_id,
            "timezone_str": datum.timezone_str
        })
    print(f"dict data is: {dict_data}")
    report_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return JsonResponse({'report_id': report_id})

# def getReport(request):
#     if request.method == 'GET':
#         report_id = request.GET.get('report_id')
#         try:
#             report = Report.objects.get(report_id=report_id)

#             if report.status == 'Running':
#                 return JsonResponse({'status': 'Running'})
#             elif report.status == 'Complete':
#                 return JsonResponse({'status': 'Complete', 'csv_data': report.csv_data})
#             else:
#                 return JsonResponse({'status': 'Unknown'})

#         except Report.DoesNotExist:
#             return JsonResponse({'status': 'Not found'})

#     return JsonResponse({'status': 'Invalid request'}, status=400)