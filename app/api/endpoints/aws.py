from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
from pydantic import BaseModel
import pandas as pd


router = APIRouter()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")


s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)



@router.post("/upload-file")
async def upload_file_to_s3(file: UploadFile = File(...)):
    # try:
    s3_client.upload_fileobj(
        file.file,
        S3_BUCKET,
        file.filename,
        ExtraArgs={"ContentType": file.content_type}
    )
    
    # Generate the file URL
    file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file.filename}"

    return {"message": "File uploaded successfully", "file_url": file_url}
    # except (NoCredentialsError, PartialCredentialsError) as e:
    #     raise HTTPException(status_code=500, detail="AWS credentials error")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


class MetadataRequest(BaseModel):
    noOfSample: int
    noOfControl: int
    expType: str
    fileUrl: str


@router.post("/save-metadata")
async def save_metadata(data: MetadataRequest):
    # try:
    print("blassssssss")
    print(f"Received data: {data.dict()}")
    df = pd.read_csv(data.fileUrl)
    print(df)
        # Simulate saving data (e.g., to a database or S3)
        # Add your actual save logic here
    return {"message": "Metadata saved successfully!", "data": data.dict()}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))