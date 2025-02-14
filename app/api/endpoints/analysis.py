import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.api.endpoints import auth
from app.config import Settings
from app.db.models import Analysis
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.services.data_processing.data_preprocess import (get_columns , data_cleaning,
                                                           get_file_url, get_data_frame,
                                                           find_index, get_normalized_columns, 
                                                           column_dict_to_list)
from app.services.normalization.normalization import normalize_data
from app.services.normalization.normalize_pipeline import  norm_pipeline
from app.services.imputation.imputation import data_imputation
from app.services.visualization.visualization import get_pca_plot , get_box_plot
from app.schema.schemas import MetadataRequest, Normalize , Differential
from app.services.aws_s3.save_to_s3 import save_df
from app.services.differetial_exp.diff_pipeline import diff_pipeline

settings = Settings()

PRODUCTION = settings.is_production

router = APIRouter(dependencies=[Depends(auth.get_current_user)])
        
@router.post("/pre-analysis")
async def save_metadata(
    data: MetadataRequest, 
    user: dict = Depends(auth.get_current_user), 
    db: AsyncSession = Depends(get_async_session),
):
    try:

        new_analysis = Analysis(
            user_id=user.id,  
            no_of_test=data.noOfTest,
            no_of_control=data.noOfControl,
            no_of_batches=data.noOfBatches,
            exp_type=data.expType,
            file_url=data.fileUrl,
        )
        
        db.add(new_analysis)
        await db.flush() 
        await db.commit() 
        await db.refresh(new_analysis)  

        columns = get_columns(data.fileUrl)  

        return {"analysis_id": new_analysis.id, "columns": columns, "no_of_test":data.noOfTest,"no_of_control":data.noOfControl,
                "exp_type":data.expType}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/normalization")
async def data_normalization(data: Normalize,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),
):
    # try:

    file_url = await get_file_url(data, user, db)
    

    normalized_data,pca_before_nrom,pca_after_norm,box_before_norm,box_after_norm , index_col, df_copy , dropped_df = norm_pipeline(data,file_url)

    # create a model to save all the files for an analysis id and save it for zipping
    
    result = await db.execute(select(Analysis).filter(Analysis.id == data.analysis_id))
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")
    
    analysis.normalized_data = normalized_data
    analysis.index_col = index_col
    db.commit()
    # await db.commit()

    return {"analysis_id":data.analysis_id,
            "normalized_data":normalized_data,
            "pca_before":pca_before_nrom,
            "pca_after":pca_after_norm,
            "box_before":box_before_norm,
            "box_after":box_after_norm,
                        }


@router.post("/differential-expression-analysis")
async def differentail_analysis(data: Differential,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),):
    file_url, index_col = await get_file_url(data, user, db, get_normalized=True)

    # columns = get_grouped_norm_columns()

    columns = { "test":{"127N Sample":["normalized_Abundance R1 127N Sample","normalized_Abundance R3 127N Sample","normalized_Abundance R2 127N Sample"],"127C Sample":["normalized_Abundance R1 127C Sample","normalized_Abundance R3 127C Sample","normalized_Abundance R2 127C Sample"],
                        "128N Sample":["normalized_Abundance R1 128N Sample","normalized_Abundance R3 128N Sample","normalized_Abundance R2 128N Sample"],"128C Sample":["normalized_Abundance R1 128C Sample","normalized_Abundance R3 128C Sample","normalized_Abundance R2 128C Sample"],
                        "129N Sample":["normalized_Abundance R1 129N Sample","normalized_Abundance R3 129N Sample","normalized_Abundance R2 129N Sample"],"129C Sample":["normalized_Abundance R1 129C Sample","normalized_Abundance R3 129C Sample","normalized_Abundance R2 129C Sample"],
                        "130N Sample":["normalized_Abundance R1 130N Sample","normalized_Abundance R3 130N Sample","normalized_Abundance R2 130N Sample"],"130C Sample":["normalized_Abundance R1 130C Sample","normalized_Abundance R3 130C Sample","normalized_Abundance R2 130C Sample"]}
                        ,
                "control":{"126 control":["normalized_Abundance R1 126 control","normalized_Abundance R2 126 control","normalized_Abundance R3 126 control"]}
                }

    p_value  = diff_pipeline(file_url,data, columns, index_col)

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


    