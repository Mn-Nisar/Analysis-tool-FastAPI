import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel 
from typing import Optional, Dict, Any, Literal
from app.api.endpoints import auth
from app.config import Settings
from app.db.models import Analysis
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.services.data_processing.data_preprocess import get_columns , data_cleaning, get_file_url
from app.services.normalization.normalization import data_normalization
from app.services.imputation.imputation import data_imputation
from app.services.visualization.visualization import get_pca_plot , get_box_plot


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
    analysis_id: int
    norm_method: Literal["median","sum","quantile","irs","z_score","tmm"]
    exp_type: Literal["biological", "technical"]
    imputation_value: float = 0
    imputation_method: Literal["value","one_fifth","miss_forest"]
    remove_contamination: bool = False
    accession_column: Optional[str] = None
    gene_column: Optional[str] = None
    convert_protein_to_gene: bool = False
    column_data: Dict[str, Any] = { "test":{"127N Sample":["Abundance R1 127N Sample","Abundance R3 127N Sample","Abundance R2 127N Sample"],"127C Sample":["Abundance R1 127C Sample","Abundance R3 127C Sample","Abundance R2 127C Sample"],
                        "128N Sample":["Abundance R1 128N Sample","Abundance R3 128N Sample","Abundance R2 128N Sample"],"128C Sample":["Abundance R1 128C Sample","Abundance R3 128C Sample","Abundance R2 128C Sample"],
                        "129N Sample":["Abundance R1 129N Sample","Abundance R3 129N Sample","Abundance R2 129N Sample"],"129C Sample":["Abundance R1 129C Sample","Abundance R3 129C Sample","Abundance R2 129C Sample"],
                        "130N Sample":["Abundance R1 130N Sample","Abundance R3 130N Sample","Abundance R2 130N Sample"],"130C Sample":["Abundance R1 130C Sample","Abundance R3 130C Sample","Abundance R2 130C Sample"]}
                        ,
                "control":{"126 control":["Abundance R1 126 control","Abundance R2 126 control","Abundance R3 126 control"]}
                }
    tmm_propotion: int = 10

        
@router.post("/pre-analysis")
async def save_metadata(
    data: MetadataRequest, 
    user: dict = Depends(auth.get_current_user), 
    db: AsyncSession = Depends(get_async_session),
):
    try:
        file_type = str(data.fileUrl.split('.')[-1]).strip()

        new_analysis = Analysis(
            user_id=user["id"],  
            no_of_test=data.noOfTest,
            no_of_control=data.noOfControl,
            no_of_batches=data.noOfBatches,
            exp_type=data.expType,
            file_url=data.fileUrl,
            file_type=file_type
        )
        
        db.add(new_analysis)
        await db.flush() 
        await db.commit() 
        await db.refresh(new_analysis)  

        columns = get_columns(data.fileUrl, file_type)  

        return {"data": new_analysis.id, "columns": columns}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/normalization")
async def data_normalization(data: Normalize, 
                             
                             
                             user: dict = Depends(auth.get_current_user)):
# async def normalize_technical(data: Normalize):
    

    # try:

    file_url = get_file_url(data,user)

    df = pd.read_csv("app/analysis-files/TECHNICAL.csv", index_col ="Accession")

    df = data_cleaning(df)

    df = data_imputation(df,data.imputation_method,data.imputation_value)

    norm_df = data_normalization(df, data.norm_method, data.tmm_propotion )

    normalized_columns = [c for c in norm_df.columns if "normalized_" in c ]
    
    df_for_pca = norm_df[normalized_columns]

    pca_before_nrom = get_pca_plot(df, title = "PCA plot [Before normalization]",columns = columns )

    pca_after_norm = get_pca_plot(norm_df[normalized_columns], title = "PCA plot [After normalization]", columns = columns)

    box_before_norm = get_box_plot(df)
    
    box_after_norm = get_box_plot(df)
    

    return {"message": "Metadata saved successfully!"}
    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))




# columns = { "test":[["Abundance R1 127N Sample","Abundance R3 127N Sample","Abundance R2 127N Sample"],["Abundance R1 127C Sample","Abundance R3 127C Sample","Abundance R2 127C Sample"],
#                     ["Abundance R1 128N Sample","Abundance R3 128N Sample","Abundance R2 128N Sample"],["Abundance R1 128C Sample","Abundance R3 128C Sample","Abundance R2 128C Sample"],
#                     ["Abundance R1 129N Sample","Abundance R3 129N Sample","Abundance R2 129N Sample"],["Abundance R1 129C Sample","Abundance R3 129C Sample","Abundance R2 129C Sample"],
#                     ["Abundance R1 130N Sample","Abundance R3 130N Sample","Abundance R2 130N Sample"],["Abundance R1 130C Sample","Abundance R3 130C Sample","Abundance R2 130C Sample"]],
#             "control":[["Abundance R1 126 control","Abundance R2 126 control","Abundance R3 126 control"]]}




