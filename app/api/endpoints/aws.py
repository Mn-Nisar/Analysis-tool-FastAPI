from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from app.config import Settings

settings = Settings()
AWS_CREDENTIAL = settings.aws_credentials
S3_ACCESS_ID = AWS_CREDENTIAL["aws_access_key"]
S3_SECRET_KEY = AWS_CREDENTIAL["aws_secret_key"]
S3_BUCKET = AWS_CREDENTIAL["s3_bucket"]

PRODUCTION = settings.is_production

router = APIRouter()

s3_client = boto3.client(
    "s3",
    aws_access_key_id = S3_ACCESS_ID,
    aws_secret_access_key= S3_SECRET_KEY,
)


@router.post("/upload-file")
async def upload_file_to_s3(file: UploadFile = File(...)):
    print(file)
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename_parts = file.filename.rsplit(".", 1)
        if len(filename_parts) == 2:
            new_filename = f"{filename_parts[0]}_{timestamp}.{filename_parts[1]}"
        else:
            new_filename = f"{file.filename}_{timestamp}"

        if PRODUCTION:
            s3_client.upload_fileobj(
                file.file,
                S3_BUCKET,
                new_filename,
                ExtraArgs={"ContentType": file.content_type}
            )
            file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{new_filename}"
        else:
            local_path = Path("app/analysis-files")
            file_location = local_path / new_filename
            
            with open(file_location, "wb") as buffer:
                buffer.write(await file.read())
            
            file_url = str(file_location)

        return {"message": "File uploaded successfully", "file_url": file_url}
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail="AWS credentials error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")