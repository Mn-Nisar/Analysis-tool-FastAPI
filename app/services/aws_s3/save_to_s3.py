from app.config import Settings
import boto3
import io 
import os

settings = Settings()
AWS_CREDENTIAL = settings.aws_credentials
S3_ACCESS_ID = AWS_CREDENTIAL["aws_access_key"]
S3_SECRET_KEY = AWS_CREDENTIAL["aws_secret_key"]
S3_BUCKET = AWS_CREDENTIAL["s3_bucket"]
PRODUCTION = settings.is_production
s3_client = boto3.client(
    "s3",
    aws_access_key_id = S3_ACCESS_ID,
    aws_secret_access_key= S3_SECRET_KEY,
)

def save_to_s3(file_buffer, file_name):
    s3_client.upload_fileobj(
    file_buffer,
    S3_BUCKET,
    file_name,
    ExtraArgs={"ContentType": "application/octet-stream"}
        )
    
    file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}"

    return file_url

def save_df(df,name,file_format):

    buffer = io.BytesIO()
    if file_format == "csv":
        print(df)
        df.to_csv(buffer)  # Save CSV to buffer

    buffer.seek(0)  # Reset buffer pointer to start
    file_name = f"{name}.{file_format}"

    if PRODUCTION:
        file_url = save_to_s3(buffer, file_name)
    else:
        local_path = os.path.join(settings.local_df_dir(), file_name)
        with open(local_path, "wb") as f:
            f.write(buffer.getvalue())
        file_url = f"http://localhost:8000/files/{file_name}"
    
    return file_url