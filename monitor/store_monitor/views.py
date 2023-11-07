import csv
import uuid
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _
from io import StringIO
from .models import StoreTimezone, Report, Store, BusinessHour
import random
import string
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta, time, datetime
import pytz
import threading
import json
# Create your views here.

def generateReport(store_id):
    try:
        timezone_data = StoreTimezone.objects.get(store_id=store_id)
        timezone_str = timezone_data.timezone_str
    except StoreTimezone.DoesNotExist:
        timezone_str = 'America/Chicago'
    
    current_datetime = Store.objects.filter(
        timestamp_utc__isnull=False
    ).latest('timestamp_utc').timestamp_utc
    current_time = current_datetime.time()
    current_day = current_datetime.weekday()

    uptime_last_hour = 0
    uptime_last_day = 0
    uptime_last_week = 0
    downtime_last_hour = 0
    downtime_last_day = 0
    downtime_last_week = 0

    try:
        business_hours = BusinessHour.objects.filter(store_id=store_id)
        if not business_hours.exists():
            business_hours = []
            for day in range(7):
                business_hour = BusinessHour(
                    store_id=store_id,
                    day=day,
                    start_time_local=time(0, 0, 0),
                    end_time_local=time(23, 59, 59),
                )
                business_hours.append(business_hour)
    except BusinessHour.DoesNotExist:
        business_hours = []
        for day in range(7):
            business_hour = BusinessHour(
                store_id=store_id,
                day=day,
                start_time_local=time(0, 0, 0),
                end_time_local=time(23, 59, 59),
            )
            business_hours.append(business_hour)


    one_hour_ago = current_datetime - timedelta(hours=1)
    one_day_ago = current_datetime - timedelta(days=1)
    one_week_ago = current_datetime - timedelta(weeks=1)

    
    utc_start_time_day = one_day_ago
    utc_start_time_hour = one_hour_ago
    utc_end_time_hour = current_datetime
    utc_end_time_day = current_datetime
    total_business_time_in_last_week = 0
    total_business_time_in_last_hour = 0
    
    for data in business_hours:
        start_time = datetime.combine(one_week_ago, data.start_time_local)
        end_time = datetime.combine(one_week_ago, data.end_time_local)
        local_timezone = pytz.timezone(timezone_str)
        local_start_time = local_timezone.localize(start_time)
        local_end_time = local_timezone.localize(end_time)
        utc_start_time = local_start_time.astimezone(pytz.utc)
        utc_end_time = local_end_time.astimezone(pytz.utc)
        total_business_time_in_last_week += ((utc_end_time-utc_start_time).total_seconds() / 3600)
        if data.day == one_day_ago.weekday():
            start_time_day = datetime.combine(one_day_ago, data.start_time_local)
            end_time_day = datetime.combine(one_day_ago, data.end_time_local)
            local_timezone = pytz.timezone(timezone_str)
            local_start_time = local_timezone.localize(start_time_day)
            local_end_time = local_timezone.localize(end_time_day)
            utc_start_time_day = local_start_time.astimezone(pytz.utc)
            utc_end_time_day = local_end_time.astimezone(pytz.utc)
        if data.day == one_hour_ago.weekday():
            start_time_hour = datetime.combine(one_hour_ago, data.start_time_local)
            end_time_hour = datetime.combine(one_hour_ago, data.end_time_local)
            local_timezone = pytz.timezone(timezone_str)
            local_start_time = local_timezone.localize(start_time_hour)
            local_end_time = local_timezone.localize(end_time_hour)
            utc_start_time_hour = local_start_time.astimezone(pytz.utc)
            utc_end_time_hour = local_end_time.astimezone(pytz.utc)

    total_business_time_in_last_hour = 60
    total_business_time_in_last_day = (utc_end_time_day-utc_start_time_day).total_seconds() / 3600

    try:
        hour_pings = Store.objects.filter(
            store_id=store_id,
            timestamp_utc__gte=max(one_hour_ago,utc_start_time_hour),
            timestamp_utc__lte=min(current_datetime,utc_end_time_hour),
            status='active'
        )
        latest_store_ping_last_hour = hour_pings.latest().timestamp_utc
        earliest_store_ping_last_hour = hour_pings.earliest().timestamp_utc
    except Store.DoesNotExist:
        latest_store_ping_last_hour = current_datetime
        earliest_store_ping_last_hour = current_datetime


    try:
        day_pings = Store.objects.filter(
        store_id=store_id,
        timestamp_utc__gte=one_day_ago,
        timestamp_utc__lte=current_datetime,
        status='active'
        )
        latest_store_ping_last_day = day_pings.latest().timestamp_utc
        earliest_store_ping_last_day = day_pings.earliest().timestamp_utc
    except Store.DoesNotExist:
        latest_store_ping_last_day = current_datetime
        earliest_store_ping_last_day = current_datetime


    try:
        week_pings = Store.objects.filter(
        store_id=store_id,
        timestamp_utc__gte=one_week_ago,
        timestamp_utc__lte=current_datetime,
        status='active'
        )
        latest_store_ping_last_week = week_pings.latest().timestamp_utc
        earliest_store_ping_last_week = week_pings.earliest().timestamp_utc
    except Store.DoesNotExist:
        latest_store_ping_last_week = current_datetime
        earliest_store_ping_last_week = current_datetime
    
    

    #total_business_time_in_last_hour = (min(current_datetime, utc_end_time_hour) - max(utc_start_time_hour, one_hour_ago)).total_seconds() / 60
    
    uptime_last_hour = (latest_store_ping_last_hour - earliest_store_ping_last_hour).total_seconds() / 60
    uptime_last_hour = uptime_last_hour - (60-total_business_time_in_last_hour)
    if uptime_last_hour < 0:
        uptime_last_hour = 0 
    uptime_last_day = (latest_store_ping_last_day - earliest_store_ping_last_day).total_seconds() / 3600
    uptime_last_day = uptime_last_day - (24-total_business_time_in_last_day)
    if uptime_last_day < 0:
        uptime_last_day = 0 
    uptime_last_week = (latest_store_ping_last_week - earliest_store_ping_last_week).total_seconds() / 3600
    uptime_last_week = uptime_last_week - (168 - total_business_time_in_last_week)
    if uptime_last_week < 0:
        uptime_last_week = 0 
    downtime_last_hour = total_business_time_in_last_hour - uptime_last_hour
    downtime_last_day = total_business_time_in_last_day - uptime_last_day
    downtime_last_week = total_business_time_in_last_week - uptime_last_week


    # Create and return the report as a dictionary
    report = {
        'store_id': store_id,
        'uptime_last_hour': uptime_last_hour,
        'uptime_last_day': uptime_last_day,
        'uptime_last_week': uptime_last_week,
        'downtime_last_hour': downtime_last_hour,
        'downtime_last_day': downtime_last_day,
        'downtime_last_week': downtime_last_week
    }

    return report

def backgroundReportGenerator(report_id):
    unique_store_ids = Store.objects.values('store_id').distinct()
    final_report = []
    for store_id in unique_store_ids:
        report = generateReport(store_id["store_id"])
        final_report.append(report)
    obj = Report.objects.get(report_id=report_id)
    obj.status = "Complete"
    json_data = json.dumps(final_report)
    obj.csv_data = json_data
    obj.save()
    print("Done")

def triggerReport(request):
    report_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    Report.objects.create(report_id=report_id)
    task_thread = threading.Thread(target=backgroundReportGenerator, args=(report_id,))
    task_thread.start()
    return JsonResponse({'report_id': report_id})

def getReport(request):
    if request.method == 'GET':
        report_id = request.GET.get('report_id')
        try:
            report = Report.objects.get(report_id=report_id)

            if report.status == 'Running':
                return JsonResponse({'status': 'Running'})
            elif report.status == 'Complete':
                fieldnames = [
                    _("store_id"),
                    _("uptime_last_hour"),
                    _("uptime_last_day"),
                    _("uptime_last_week"),
                    _("downtime_last_hour"),
                    _("downtime_last_day"),
                    _("downtime_last_week"),
                ]
                filename = f"{uuid.uuid4()}.csv"
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = f"attachment; filename={filename}"
                csv_buffer = StringIO()
                writer = csv.DictWriter(
                    response,
                    fieldnames=[_(fieldname) for fieldname in fieldnames],
                )
                writer.writeheader()

                data = eval(report.csv_data)

                for datum in data:
                    writer.writerow(
                        {
                            _("store_id"): datum['store_id'],
                            _("uptime_last_hour"): datum['uptime_last_hour'],
                            _("uptime_last_day"): datum['uptime_last_day'],
                            _("uptime_last_week"): datum['uptime_last_week'],
                            _("downtime_last_hour"): datum['downtime_last_hour'],
                            _("downtime_last_day"): datum['downtime_last_day'],
                            _("downtime_last_week"): datum['downtime_last_week'],
                        }
                    )
                csv_buffer.seek(0)
                return response
                # return JsonResponse({'status': 'Complete', 'csv_data': report.csv_data})
            else:
                return JsonResponse({'status': 'Unknown'})

        except Report.DoesNotExist:
            return JsonResponse({'status': 'Not found'})

    return JsonResponse({'status': 'Invalid request'}, status=400)