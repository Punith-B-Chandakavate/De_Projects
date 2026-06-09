# 🪣 AWS S3 Setup & Fundamentals

⬅️ [Back to AWS Account Setup](../01_AWS_account_Setup.md)

---

# 📚 Table of Contents

* Introduction
* What is Amazon S3?
* Why Use S3?
* Key Concepts
* S3 Storage Classes
* Creating an S3 Bucket
* Uploading Files
* Folder Structure in S3
* Access Control
* S3 Versioning
* AWS CLI Commands
* Real-World Data Engineering Example
* Best Practices
* Interview Questions
* Key Takeaways

---

# 📖 Introduction

Amazon Simple Storage Service (Amazon S3) is a highly scalable object storage service provided by AWS.

It is one of the most widely used services in Data Engineering because it serves as the foundation for:

* Data Lakes
* Data Warehouses
* ETL Pipelines
* Backup & Archiving
* Analytics Platforms

---

# ☁️ What is Amazon S3?

Amazon S3 (Simple Storage Service) is an object storage service designed to store and retrieve any amount of data from anywhere.

Unlike traditional file systems, S3 stores data as **objects** inside  **buckets** .

![Amazon S3 Overview](images/AWS_S3_Overview.png)

---

# 🎯 Why Use S3?

Amazon S3 provides:

✅ High Durability (99.999999999%)

✅ High Availability

✅ Unlimited Scalability

✅ Cost-Effective Storage

✅ Integration with AWS Services

---

# 🏗️ Key Concepts

## Bucket

A bucket is a container used to store objects.

Example:

```text
my-data-lake
company-data
etl-project-bucket
```

---

## Object

An object consists of:

* Data (File Content)
* Metadata
* Unique Key

Example:

```text
employees.csv
sales.parquet
customers.json
```

---

## Key

The unique identifier of an object inside a bucket.

Example:

```text
raw/customers.csv
processed/sales.parquet
```

---

# 🏛️ S3 Architecture

![S3 Architecture](images/AWS_S3_Architecture.png)

---

# 📦 S3 Storage Classes

AWS provides different storage classes for different use cases.

| Storage Class                 | Use Case                    |
| ----------------------------- | --------------------------- |
| S3 Standard                   | Frequently Accessed Data    |
| S3 Intelligent-Tiering        | Automatic Cost Optimization |
| S3 Standard-IA                | Infrequent Access           |
| S3 One Zone-IA                | Single AZ Storage           |
| S3 Glacier Instant Retrieval  | Archival Data               |
| S3 Glacier Flexible Retrieval | Long-Term Backup            |
| S3 Glacier Deep Archive       | Lowest Cost Storage         |

---

# 🪣 Creating an S3 Bucket

## Step 1

Open AWS Console.

Navigate to:

```text
AWS Console → S3
```

---

## Step 2

Click:

```text
Create Bucket
```

---

## Step 3

Provide Bucket Name.

Example:

```text
de-learning-data-lake
```

### Naming Rules

* Must be globally unique
* Lowercase letters only
* No spaces
* Use hyphens (-)

---

## Step 4

Select AWS Region.

Example:

```text
ap-south-1 (Mumbai)
```

---

## Step 5

Keep default settings and click:

```text
Create Bucket
```

---

# 📤 Uploading Files

Open your bucket.

Click:

```text
Upload
```

Choose files such as:

```text
customers.csv
employees.json
sales.parquet
```

Click:

```text
Upload
```

---

# 📂 Folder Structure in S3

Although S3 doesn't have real folders, it uses prefixes to simulate folders.

Recommended Data Engineering structure:

```text
s3://de-learning-data-lake/

raw/
├── customers/
├── products/
└── orders/

processed/
├── parquet/
└── curated/

analytics/
├── reports/
└── dashboards/
```

---

# 🔒 Access Control

S3 access can be controlled using:

## IAM Policies

Grant permissions to users and roles.

Example:

```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}
```

---

## Bucket Policies

Apply permissions directly to buckets.

---

## Access Control Lists (ACLs)

Object-level permissions.

---

# 🔄 S3 Versioning

Versioning keeps multiple versions of an object.

Example:

### Version 1

```text
customers.csv
```

### Updated Version

```text
customers.csv
```

S3 stores both versions.

---

## Benefits

* Recover deleted files
* Protect against accidental overwrites
* Maintain historical versions

---

# 💻 AWS CLI Commands

## List Buckets

```bash
aws s3 ls
```

---

## Create Bucket

```bash
aws s3 mb s3://de-learning-data-lake
```

---

## Upload File

```bash
aws s3 cp employees.csv s3://de-learning-data-lake/
```

---

## Download File

```bash
aws s3 cp s3://de-learning-data-lake/employees.csv .
```

---

## List Files in Bucket

```bash
aws s3 ls s3://de-learning-data-lake/
```

---

## Remove File

```bash
aws s3 rm s3://de-learning-data-lake/employees.csv
```

---

# 🚀 Real-World Data Engineering Example

![S3 Data Lake Architecture](images/AWS_S3_Data_Lake.png)

---

# 🛠️ Common AWS Services Integrated with S3

| Service        | Purpose               |
| -------------- | --------------------- |
| AWS Glue       | ETL                   |
| Athena         | Query S3 Data         |
| Redshift       | Data Warehouse        |
| EMR            | Big Data Processing   |
| Lambda         | Serverless Processing |
| Lake Formation | Data Lake Governance  |

---

# 🚀 Best Practices

✅ Enable Versioning

✅ Enable Encryption

✅ Use Lifecycle Policies

✅ Follow Least Privilege Access

✅ Organize Data Using Prefixes

✅ Use Parquet for Analytics

✅ Monitor Storage Costs

---

# 🎤 Interview Questions

### What is Amazon S3?

Amazon S3 is an object storage service used to store and retrieve data at any scale.

### What is a Bucket?

A container used to store objects in S3.

### What is an Object?

A file stored inside an S3 bucket.

### What is a Key in S3?

The unique identifier for an object.

### Why is S3 widely used in Data Engineering?

Because it provides scalable, durable, and cost-effective storage for Data Lakes and analytics platforms.

### What is S3 Versioning?

A feature that stores multiple versions of an object.

### What storage format is commonly used in S3 for analytics?

Parquet.

---

# 🏁 Key Takeaways

* Amazon S3 is AWS's object storage service.
* Buckets store objects such as CSV, JSON, and Parquet files.
* S3 is the foundation of most Data Lakes.
* Versioning helps protect and recover data.
* AWS CLI enables S3 management from the command line.
* S3 integrates with Glue, Athena, Redshift, and EMR.
* Parquet is the preferred format for analytics workloads.
* Proper folder organization improves Data Lake management.

---

➡️ [SCD Modeling](04_SCD_modeling.md)
