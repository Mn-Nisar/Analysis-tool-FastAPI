from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel 
from typing import Optional, Dict, Any, Literal
from app.services.analysis.analysis import normalize_data
from app.api.endpoints import auth
from app.config import Settings
from app.db.models import Analysis
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.data_processing.data_preprocess import get_columns

settings = Settings()

PRODUCTION = settings.is_production
# router = APIRouter(dependencies=[Depends(auth.get_current_user)])
router = APIRouter()

class MetadataRequest(BaseModel):
    noOfTest: int
    noOfControl: int
    noOfBatches: Optional[int] = None
    expType: Literal ["techrep","biorep"]
    fileUrl: str


class Normalize(BaseModel):
    norm_method: Literal["median","sum","quantile","irs","z_score","tmm"]
    exp_type: Literal["biological", "technical"]
    imputation_value: float = 0
    imputation_method: Literal["value","one_fifth","miss_forest"]
    remove_contamination: bool = False
    accession_column: Optional[str] = None
    gene_column: Optional[str] = None
    convert_protein_to_gene: bool = False
    column_data: Dict[str, Any]

@router.post("/pre-analysis")
async def save_metadata(data: MetadataRequest, user: dict = Depends(auth.get_current_user), 
                        db: Session = Depends(get_db),
):
    try:
        file_type = str(data.fileUrl.split('.')[-1]).strip()

        new_analysis = Analysis(
            user_id=user.id,
            no_of_test=data.noOfTest,
            no_of_control=data.noOfControl,
            no_of_batches=data.noOfBatches,
            exp_type=data.expType,
            file_url=data.fileUrl,
            file_type=file_type
        )
        
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)

        print("file_typefile_typefile_typefile_type",file_type)

        columns = get_columns(data.fileUrl,file_type)
        print(columns)
        return {"data": new_analysis.id, "columns":columns}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/normalize")
 # async def normalize_technical(data: NormalizeTechnical, user: dict = Depends(auth.get_current_user)):
async def normalize_technical(data: Normalize):
    try:
        normalize_data(data)
        return {"message": "Metadata saved successfully!", "data": data.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



columns = { "test":[["Abundance R1 127N Sample","Abundance R3 127N Sample","Abundance R2 127N Sample"],["Abundance R1 127C Sample","Abundance R3 127C Sample","Abundance R2 127C Sample"],
                    ["Abundance R1 128N Sample","Abundance R3 128N Sample","Abundance R2 128N Sample"],["Abundance R1 128C Sample","Abundance R3 128C Sample","Abundance R2 128C Sample"],
                    ["Abundance R1 129N Sample","Abundance R3 129N Sample","Abundance R2 129N Sample"],["Abundance R1 129C Sample","Abundance R3 129C Sample","Abundance R2 129C Sample"],
                    ["Abundance R1 130N Sample","Abundance R3 130N Sample","Abundance R2 130N Sample"],["Abundance R1 130C Sample","Abundance R3 130C Sample","Abundance R2 130C Sample"]],
            "control":[["Abundance R1 126 control","Abundance R2 126 control","Abundance R3 126 control"]]}




