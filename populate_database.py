import os
import csv
import django
from datetime import datetime
from pytz import UTC
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant_monitoring.settings")

django.setup()


from monitor_activity.models import StoreStatus, Store, BusinessHours


def populate_store_data_from_csv(csv_file_path):
    data_to_insert = []
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row if it exists
        i = 0
        for row in csv_reader:
            store_id, timezone_str = row
            store_name = "Store_{}".format(i)
            data_to_insert.append(Store(id=store_id, name=store_name, timezone=timezone_str))
            i += 1

    # Bulk insert the data into the database
    Store.objects.bulk_create(data_to_insert)


def populate_store_status_from_csv(csv_file_path):
    data_to_insert = []
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row if it exists
        for row in csv_reader:
            store_id, status, timestamp_utc_str = row
            try:
                date_format = "%Y-%m-%d %H:%M:%S.%f UTC"
                timestamp_utc = datetime.strptime(timestamp_utc_str, date_format).replace(tzinfo=UTC)
            except ValueError:
                date_format = "%Y-%m-%d %H:%M:%S UTC"
                timestamp_utc = datetime.strptime(timestamp_utc_str, date_format).replace(tzinfo=UTC)
            store = Store.get_store_or_none(id=store_id)
            if not store:
                store = Store.objects.create(id=store_id, name="Store_new")
            data_to_insert.append(StoreStatus(store=store, timestamp_utc=timestamp_utc, status=status))

    # Bulk insert the data into the database
    StoreStatus.objects.bulk_create(data_to_insert)


def populate_business_hours_from_csv(csv_file_path):
    data_to_insert = []
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row if it exists
        for row in csv_reader:
            store_id, day, start_time_local, end_time_local = row
            start_time_object = datetime.strptime(start_time_local, "%H:%M:%S").time()
            end_time_object = datetime.strptime(end_time_local, "%H:%M:%S").time()
            store = Store.get_store_or_none(id=store_id)
            if not store:
                store = Store.objects.create(id=store_id, name="Store_new")
            data_to_insert.append(BusinessHours(
                store=store,
                day_of_week=day,
                start_time_local=start_time_object,
                end_time_local=end_time_object,
                )
            )

    # Bulk insert the data into the database
    BusinessHours.objects.bulk_create(data_to_insert)


if __name__ == "__main__":

    csv_file_path = "store_data.csv"
    populate_store_data_from_csv(csv_file_path)

    csv_file_path = "store_status.csv"
    populate_store_status_from_csv(csv_file_path)

    csv_file_path = "business_hours.csv"
    populate_business_hours_from_csv(csv_file_path)
