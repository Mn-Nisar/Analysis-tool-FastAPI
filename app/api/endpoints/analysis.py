from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.api.endpoints import auth
from app.config import Settings
from app.db.models import Analysis
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.services.data_processing.data_preprocess import (get_columns , 
                                                           get_file_url, get_norm_columns)
from app.services.normalization.normalize_pipeline import  norm_pipeline
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
    # try:

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

# except Exception as e:
#     raise HTTPException(status_code=500, detail=str(e))


@router.post("/normalization")
async def data_normalization(data: Normalize,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),
):
    # try:

    file_url = await get_file_url(data, user, db)
    

    normalized_data,pca_before_nrom,pca_after_norm,box_before_norm,box_after_norm , index_col, control_list, df_copy , dropped_df = norm_pipeline(data,file_url)

    # create a model to save all the files for an analysis id and save it for zipping
    
    result = await db.execute(select(Analysis).filter(Analysis.id == data.analysis_id))
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")
    
    analysis.normalized_data = normalized_data
    analysis.index_col = index_col
    analysis.column_data = data.column_data
    await db.commit()
    
    return {"analysis_id":data.analysis_id,
            "normalized_data":normalized_data,
            "pca_before":pca_before_nrom,
            "pca_after":pca_after_norm,
            "box_before":box_before_norm,
            "box_after":box_after_norm,
            "control_list":control_list,
                        }


@router.post("/differential-expression-analysis")
async def differentail_analysis(data: Differential,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),):
    
    file_url, index_col, columns_data = await get_file_url(data, user, db, get_normalized=True)
    
    columns = get_norm_columns(columns_data)

    df,diff_df,bargraph  = diff_pipeline(file_url,data, columns, index_col)
    final_df = save_df(df, name=f"{data.analysis_id}_final_data", file_format = "csv")
    diff_df_url = save_df(diff_df, name=f"{data.analysis_id}_differential_data", file_format = "csv")

    return {"analysis_id":data.analysis_id,"final_df":final_df,"diff_df":diff_df_url,"bargraph":bargraph}

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))




@router.post("/differential-volcano-plot")
async def volcano_plot_api(analysis_id: int,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),):
    pass