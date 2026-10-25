# Assignment Submission Portal

## Run locally
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python app.py        # open http://localhost:5000

Register one teacher and one student account to try the full flow.

## Deploy to the cloud
- Set env vars: SECRET_KEY (required), DB_PATH, UPLOAD_DIR
- Start command: `gunicorn app:app`
- AWS: Elastic Beanstalk or EC2 + Nginx; swap SQLite for RDS (PostgreSQL) via psycopg2
- Store files in S3: replace `save_file()` with `boto3.client("s3").upload_fileobj(...)`
  and the download route with `generate_presigned_url(...)`
- Serve over HTTPS, and give the S3 bucket no public access

## API summary
POST /api/register, /api/login
GET/POST /api/assignments
POST /api/assignments/<id>/submit (multipart, student)
GET /api/assignments/<id>/submissions (teacher)
POST /api/submissions/<id>/grade (teacher)
GET /api/submissions/<id>/file
