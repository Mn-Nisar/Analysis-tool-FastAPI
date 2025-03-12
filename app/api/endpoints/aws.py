from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import boto3
import pandas as pd
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from app.config import Settings
from app.services.aws_s3.save_to_s3 import save_to_s3 
import io

settings = Settings()

PRODUCTION = settings.is_production

router = APIRouter()


@router.post("/upload-file")
async def upload_file_to_s3(file: UploadFile = File(...)):
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename_parts = file.filename.rsplit(".", 1)
        base_filename = filename_parts[0].replace(" ", "_") if len(filename_parts) == 2 else file.filename.replace(" ", "_")

        new_filename = f"{base_filename}_{timestamp}.csv" 
        
        file_bytes = await file.read()
        file_extension = filename_parts[1].lower() if len(filename_parts) == 2 else ""

        if file_extension == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            file_data = csv_buffer.getvalue()
        elif file_extension == "txt":
            df = pd.read_csv(io.BytesIO(file_bytes), sep="\t")
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            file_data = csv_buffer.getvalue()
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            file_data = csv_buffer.getvalue()
        else:
            # Save the file as is
            file_data = file_bytes

        if PRODUCTION:
            file_url = save_to_s3(io.BytesIO(file_data), new_filename)
        else:
            local_path = Path("app/analysis-files")
            local_path.mkdir(parents=True, exist_ok=True)
            file_location = local_path / new_filename
            
            with open(file_location, "wb") as buffer:
                buffer.write(file_data)
            
            file_url = str(file_location)

        return {"file_url": file_url}

    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail="AWS credentials error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")