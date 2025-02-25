import boto3
import pandas as pd
import io
from app.config import Settings

settings = Settings()

AWS_CREDENTIAL = settings.aws_credentials
S3_ACCESS_ID = AWS_CREDENTIAL["aws_access_key"]
S3_SECRET_KEY = AWS_CREDENTIAL["aws_secret_key"]

mybucket = 'omciodss3bucketdev'
s3 = boto3.resource('s3',
         aws_access_key_id=S3_ACCESS_ID,
         aws_secret_access_key= S3_SECRET_KEY)

def create_s3_object(df,object_id):

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index = False)
    
    try:
        s3.Object(mybucket, object_id).put(Body=csv_buffer.getvalue())
    except:
        return Exception

def delete_s3_object(object_id):
    try:
        s3.Object(mybucket, object_id).delete()
    except:
        return