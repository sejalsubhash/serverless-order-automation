# 🚀 Automated Order Processing System (AWS VPC + Serverless Architecture)

---

## 📌 Project Overview

The **Automated Order Processing System** is a cloud-based application built using AWS services that:

* Accepts orders from a web application
* Validates order amount using AWS Lambda
* Stores valid orders in Amazon RDS (MySQL)
* Generates daily reports
* Uploads reports to Amazon S3
* Automates reporting using EventBridge

This project demonstrates secure VPC design, serverless integration, database connectivity, IAM configuration, and event-driven automation.

---

# 🏗️ Architecture Workflow Diagram

```
                    ┌──────────────────────────────┐
                    │           Internet           │
                    └──────────────┬───────────────┘
                                   │
                            Public Subnets
                                   │
                         ┌──────────────────┐
                         │   EC2 Instance   │
                         │ (Flask App)      │
                         └────────┬─────────┘
                                  │
                     ┌────────────┴────────────┐
                     │         VPC              │
                     │                          │
             Private Subnets                Secrets Manager
                     │                          │
              ┌──────────────┐                  │
              │   RDS MySQL  │◄──────────────────┘
              └──────┬───────┘
                     │
              ┌──────┴─────────┐
              │ Lambda Validator│
              └──────┬─────────┘
                     │
              ┌──────┴─────────┐
              │ Lambda Report   │
              │ (Daily Delta)   │
              └──────┬─────────┘
                     │
              ┌──────┴─────────┐
              │      S3 Bucket  │
              └─────────────────┘
                     ▲
                     │
               EventBridge (24h Trigger)
```

---

# 🛠️ Implementation Steps

---

# ✅ Step 1: Create VPC

* Create custom VPC
* Create 2 Public Subnets → For EC2
* Create 2 Private Subnets → For RDS
* Attach Internet Gateway
* Configure route tables properly

---

# ✅ Step 2: Create RDS Subnet Group

* Go to RDS → Subnet Groups
* Create subnet group
* Select private subnets only
* Name: `order-processing-app-SG`

---

# ✅ Step 3: Create Security Groups

### 🔹 RDS Security Group

* Allow MySQL (Port 3306)
* Source: EC2 & Lambda Security Group

### 🔹 EC2 Security Group

* SSH (22)
* HTTP (80)
* Custom TCP (5000 for Flask)
* MySQL (3306)

### 🔹 Lambda Security Group

* MySQL (3306)

---

# ✅ Step 4: Create RDS Database

* Engine: MySQL
* Template: Free Tier
* DB Name: ordersdb
* Public Access: NO
* Select VPC created above
* Select Subnet Group
* Attach RDS Security Group

---

# ✅ Step 5: Launch EC2 Instance

### 🔹 Create IAM Role

Name: `EC2-Secrets-Manager-Access-Role`

Attach:

* SecretsManagerReadWrite
* AWSLambda_FullAccess
* AmazonS3FullAccess

Attach role to EC2.

### 🔹 Launch EC2

* Ubuntu 22.04
* Instance Type: t3.micro
* Attach Security Group created earlier

---

# ✅ Step 6: Connect EC2 to RDS

From EC2 terminal:

* Install MySQL client
* Connect using RDS endpoint
* Verify database
* Create new database if required
* Create `orders` table manually

---

# ✅ Step 7: Install Application Dependencies on EC2

On EC2:

* Install Python
* Create virtual environment
* Activate environment
* Install:

  * flask
  * boto3
  * pymysql

---

# ✅ Step 8: Add Flask Application Code

Inside EC2:

1. Create file:

   ```
   nano app.py
   ```

2. Add Flask application code that:

   * Accepts order input
   * Invokes Lambda function (`order-validator`)
   * Displays success or invalid message

3. Run application:

   ```
   python3 app.py
   ```

Access in browser:

```
http://<EC2-Public-IP>:5000
```

---

# ✅ Step 9: Configure AWS Secrets Manager

* Go to Secrets Manager
* Create secret
* Type: Credentials for RDS
* Add:

  * username
  * password
  * host
  * db

Secret name:

```
order-db-secret
```

---

# ✅ Step 10: Create Lambda – Order Validator

### 🔹 Create IAM Role

Name: `order-app-lambda-role`

Attach:

* SecretsManagerReadWrite
* AWSLambdaBasicExecutionRole
* AWSLambdaVPCAccessExecutionRole

### 🔹 Create Lambda Function

* Name: order-validator
* Runtime: Python 3.x
* Attach role

### 🔹 Add Code

* Add validation logic
* If amount ≤ 0 → Return invalid
* If amount > 0 → Fetch secret and insert into RDS

### 🔹 Add pymysql Layer

* Install pymysql locally
* Zip dependencies
* Create Lambda Layer
* Attach layer to function

### 🔹 Configure VPC

* Select same VPC
* Select Private Subnets
* Attach Lambda security group

Deploy and test function.

---

# ✅ Step 11: Create S3 Bucket

* Create bucket
* General purpose
* Keep default settings (avoid public access in production)

---

# ✅ Step 12: Create Lambda – Daily Report Generator

### 🔹 Create IAM Role

Name: `lambda-daily-delta-task-role`

Attach:

* AmazonS3FullAccess
* SecretsManagerReadWrite
* AWSLambdaVPCAccessExecutionRole

### 🔹 Create Lambda Function

* Name: daily-delta-processor
* Runtime: Python 3.x
* Attach role

### 🔹 Add Code

* Connect to RDS
* Fetch orders
* Generate CSV
* Upload file to S3

### 🔹 Attach pymysql Layer

* Use same layer created earlier

### 🔹 Configure VPC

* Same VPC
* Private Subnets
* Lambda security group

Test function.

---

# ✅ Step 13: Create EventBridge Rule

* Go to EventBridge
* Create Schedule Rule
* Schedule pattern: Every 24 hours
* Target: Lambda
* Select `daily-delta-processor`

After 24 hours:

* New report generated
* File uploaded to S3

---

# 🔍 Verification

✔ Submit order from browser
✔ Check RDS table for stored data
✔ Test invalid order (≤ 0)
✔ Verify CSV file generated in S3
✔ Confirm scheduled execution

---

# 🛠️ Troubleshooting Handled

* Missing pymysql module → Fixed using Lambda Layer
* Lambda timeout → Increased timeout
* RDS connection issue → Fixed security group inbound rule
* IAM VPC permission error → Attached AWSLambdaVPCAccessExecutionRole
* Secret key error → Corrected secret JSON format

---

# 🎯 Key Learning Outcomes

* VPC architecture design
* Secure database deployment
* Lambda VPC networking
* IAM role management
* Secrets management
* Serverless automation
* EventBridge scheduling
* S3 integration

---

# 👩‍💻 Author

**Sejal Pawar**
AWS | DevOps | Cloud Projects

