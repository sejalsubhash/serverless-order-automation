import json
import boto3
import pymysql
import csv
import io
from datetime import date, timedelta

secret_name = "order-db-secret"
bucket_name = "order-daily-reports-215317654435"

def get_db():
    client = boto3.client("secretsmanager")
    secret = json.loads(client.get_secret_value(SecretId=secret_name)['SecretString'])

    return pymysql.connect(
        host=secret['host'],
        user=secret['username'],
        password=secret['password'],
        database=secret['dbname'],
        connect_timeout=5
    )

def get_daily_stats(cursor, day):
    query = """
        SELECT COUNT(*), IFNULL(SUM(amount),0)
        FROM orders
        WHERE DATE(created_time) = %s
    """
    cursor.execute(query, (day,))
    return cursor.fetchone()

def lambda_handler(event, context):

    conn = get_db()
    cursor = conn.cursor()

    today = date.today()
    yesterday = today - timedelta(days=1)

    today_orders, today_amount = get_daily_stats(cursor, today)
    y_orders, y_amount = get_daily_stats(cursor, yesterday)

    order_increment = today_orders - y_orders
    amount_increment = today_amount - y_amount

    # Create CSV
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)

    writer.writerow([
        "date",
        "orders_today",
        "amount_today",
        "orders_yesterday",
        "amount_yesterday",
        "order_increment",
        "amount_increment"
    ])

    writer.writerow([
        str(today),
        today_orders,
        today_amount,
        y_orders,
        y_amount,
        order_increment,
        amount_increment
    ])

    s3 = boto3.client("s3")

    filename = f"daily_summary_{today}.csv"

    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=csv_buffer.getvalue()
    )

    cursor.close()
    conn.close()

    return {
        "status": "SUCCESS",
        "file": filename,
        "today_orders": today_orders,
        "today_amount": float(today_amount),
        "order_increment": order_increment,
        "amount_increment": float(amount_increment)
    }
