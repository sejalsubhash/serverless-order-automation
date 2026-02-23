import json
import boto3
import pymysql

secret_name = "order-db-secret"

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

def lambda_handler(event, context):
    try:
        print("EVENT:", event)

        name = event.get("customer_name")
        amount = float(event.get("amount", 0))

        if not name:
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "FAILED", "message": "Customer name empty"})
            }

        if amount <= 0:
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "FAILED", "message": "Invalid amount"})
            }

        conn = get_db()
        cursor = conn.cursor()

        sql = """
        INSERT INTO orders (customer_name, amount, status)
        VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (name, amount, "PROCESSED"))
        conn.commit()

        cursor.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({"status": "SUCCESS", "message": "Order stored in database"})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "FAILED", "message": f"Database error: {str(e)}"})
        }
