from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import boto3
import pandas as pd
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from app.config import Settings
import io

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
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename_parts = file.filename.rsplit(".", 1)
        base_filename = filename_parts[0] if len(filename_parts) == 2 else file.filename
        new_filename = f"{base_filename}_{timestamp}.parquet" 

        file_bytes = await file.read()
        file_extension = filename_parts[1].lower() if len(filename_parts) == 2 else ""

        if file_extension == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif file_extension == "txt":
            df = pd.read_csv(io.BytesIO(file_bytes), sep="\t")
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            return {"error": "Unsupported file format. Only CSV and Excel are allowed."}

        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, engine="pyarrow", index=False)
        parquet_buffer.seek(0) 
        
        if PRODUCTION:
            s3_client.upload_fileobj(
                parquet_buffer,
                S3_BUCKET,
                new_filename,
                ExtraArgs={"ContentType": "application/octet-stream"}
            )
            file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{new_filename}"
        else:
            local_path = Path("app/analysis-files")
            local_path.mkdir(parents=True, exist_ok=True)
            file_location = local_path / new_filename
            
            with open(file_location, "wb") as buffer:
                buffer.write(parquet_buffer.getvalue())
            
            file_url = str(file_location)

        return {"message": "File successfully uploaded as Parquet", "file_url": file_url}

    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail="AWS credentials error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")