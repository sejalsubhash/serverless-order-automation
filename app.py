from flask import Flask, request, render_template_string
import boto3
import json
import pymysql

app = Flask(__name__)
lambda_client = boto3.client('lambda', region_name='ap-south-1')

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Order Processing System</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card shadow-lg p-4">
<h2 class="mb-4 text-center">Automated Order Processing</h2>
<form method="post">
<div class="mb-3">
<label class="form-label">Customer Name</label>
<input class="form-control" name="name" required>
</div>
<div class="mb-3">
<label class="form-label">Amount</label>
<input class="form-control" name="amount" type="number" step="0.01" required>
</div>
<button class="btn btn-primary w-100">Submit Order</button>
</form>
{% if message %}
<div class="alert mt-3 {{'alert-success' if status=='SUCCESS' else 'alert-danger'}}">
{{message}}
</div>
{% endif %}
</div>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    status = ""
    if request.method == "POST":
        payload = {
            "customer_name": request.form["name"],
            "amount": request.form["amount"]
        }
        try:
            response = lambda_client.invoke(
                FunctionName="order-processing-function",
                Payload=json.dumps(payload)
            )
            result = json.loads(response['Payload'].read())
            
            # Debug: Print what Lambda actually returned
            print("Lambda Response:", result)
            
            # Handle different response formats
            if "errorMessage" in result:
                # Lambda had an error
                message = f"Lambda Error: {result.get('errorMessage', 'Unknown error')}"
                status = "FAILED"
            else:
                message = result.get("message", "Unknown response")
                status = result.get("status", "UNKNOWN")
                
        except Exception as e:
            message = f"Error invoking Lambda: {str(e)}"
            status = "FAILED"
            print("Exception:", str(e))
            
    return render_template_string(HTML, message=message, status=status)

app.run(host="0.0.0.0", port=5000)
