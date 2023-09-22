import os
import csv
from datetime import timedelta, datetime
from django.utils import timezone
from monitor_activity.models import Store, BusinessHours, StoreStatus
import secrets
import string


def generate_random_string(store_id, length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string + str(store_id)


def generate_report(store_id):
    # Fetch store data, business hours, and status data based on store_id
    store = Store.objects.get(pk=store_id)
    business_hours = BusinessHours.objects.filter(store=store)
    status_data = StoreStatus.objects.filter(store=store).order_by('timestamp_utc')

    # Get the latest timestamp in the status data
    latest_timestamp = status_data.latest('timestamp_utc').timestamp_utc

    # Initialize variables to store report data
    uptime_last_hour = 0
    uptime_last_day = 0
    uptime_last_week = 0
    downtime_last_hour = 0
    downtime_last_day = 0
    downtime_last_week = 0

    # Define a function to calculate downtime within business hours
    def calculate_downtime(start_time, end_time, status_data):
        downtime = 0
        for status_entry in status_data:
            if start_time <= status_entry.timestamp_utc <= end_time:
                if status_entry.status != 'active':
                    downtime += 1
        return downtime

    # Calculate report data
    for business_hour in business_hours:
        start_time = timezone.make_aware(datetime.combine(latest_timestamp.date(), business_hour.start_time_local))
        end_time = timezone.make_aware(datetime.combine(latest_timestamp.date(), business_hour.end_time_local))

        # Calculate downtime within the last hour
        one_hour_ago = latest_timestamp - timedelta(hours=1)
        downtime_last_hour += calculate_downtime(one_hour_ago, latest_timestamp, status_data)

        # Calculate downtime within the last day
        one_day_ago = latest_timestamp - timedelta(days=1)
        downtime_last_day += calculate_downtime(one_day_ago, latest_timestamp, status_data)

        # Calculate downtime within the last week
        one_week_ago = latest_timestamp - timedelta(days=7)
        downtime_last_week += calculate_downtime(one_week_ago, latest_timestamp, status_data)

        # Calculate uptime as the complement of downtime
        total_minutes_in_hour = 60
        total_hours_in_day = 24
        total_hours_in_week = 168

        # Calculate downtime within the current business hour
        current_hour_downtime = calculate_downtime(start_time, end_time, status_data)

        # Calculate the number of minutes within the business hour
        total_minutes_in_business_hour = (end_time - start_time).seconds // 60

        # Calculate the uptime within the current business hour using linear interpolation
        uptime_last_hour += total_minutes_in_business_hour - current_hour_downtime

        # Calculate the uptime within the current business day using linear interpolation
        uptime_last_day += (business_hour.end_time_local.hour - business_hour.start_time_local.hour) * (
                    total_hours_in_day - downtime_last_day)

        # Calculate the uptime within the current business week using linear interpolation
        uptime_last_week += (business_hour.end_time_local.hour - business_hour.start_time_local.hour) * (
                    total_hours_in_week - downtime_last_week)

    # Prepare the report data as a dictionary
    report_data = {
        'store_id': store_id,
        'uptime_last_hour': uptime_last_hour,
        'uptime_last_day': uptime_last_day,
        'uptime_last_week': uptime_last_week,
        'downtime_last_hour': downtime_last_hour,
        'downtime_last_day': downtime_last_day,
        'downtime_last_week': downtime_last_week,
    }

    # Write data to CSV file
    report_name = generate_random_string(store_id=store_id)
    report_path = "{}/{}.csv".format("reports_generated", report_name)
    with open(report_path, 'w', newline='') as csv_file:
        fieldnames = ['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week',
                      'downtime_last_hour', 'downtime_last_day', 'downtime_last_week']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(report_data)
    return report_name


def is_report_complete(report_id):
    report_directory = 'reports_generated'
    report_filename = '{}.csv'.format(report_id)
    # Create the full path to the report file
    report_file_path = os.path.join(report_directory, report_filename)
    return os.path.exists(report_file_path)
