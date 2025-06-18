import hashlib
from google.cloud import bigquery
from datetime import datetime

def validate_file(data, context):
    file_name = data['name']
    bucket = data['bucket']
    content_type = data.get('contentType', '')
    file_size = int(data.get('size', 0))

    # Allow only PDFs and images
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
    if content_type not in allowed_types or file_size > 5 * 1024 * 1024:
        print("File rejected: wrong type or too large.")
        return

    file_hash = hashlib.md5(file_name.encode()).hexdigest()

    try:
        student_name, subject = file_name.rsplit('_', 1)
        subject = subject.split('.')[0]
    except:
        student_name = "unknown"
        subject = "unknown"

    client = bigquery.Client()
    table_id = "stalwart-method-462107-m8.assignments_dataset.submissions"

    row = [{
        "student_name": student_name,
        "subject": subject,
        "timestamp": datetime.utcnow().isoformat(),
        "file_name": file_name,
        "file_size": file_size,
        "file_type": content_type,
        "file_hash": file_hash
    }]

    errors = client.insert_rows_json(table_id, row)
    if errors == []:
        print("Inserted into BigQuery successfully.")
    else:
        print("Error inserting into BigQuery:", errors)

