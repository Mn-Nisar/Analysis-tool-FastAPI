import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from app.api.endpoints import auth
from app.config import Settings
from app.db.models import Analysis
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.services.data_processing.data_preprocess import (get_columns , data_cleaning,
                                                           get_file_url, get_data_frame,
                                                           filter_dataframe)
from app.services.normalization.normalization import data_normalization
from app.services.imputation.imputation import data_imputation
from app.services.visualization.visualization import get_pca_plot , get_box_plot
from app.schema.schemas import MetadataRequest, Normalize

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

        return {"data": new_analysis.id, "columns": columns}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/normalization")
async def data_normalization(data: Normalize,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),
):
    # try:

    file_url = await get_file_url(data, user, db)
    df = get_data_frame(file_url)
    
    df_copy = df.copy()

    df = filter_dataframe(df,data.accession_column,data.gene_column, data.convert_protein_to_gene, data.column_data)

    # df = data_cleaning(df)

    # df = data_imputation(df,data.imputation_method,data.imputation_value)

    # norm_df = data_normalization(df, data.norm_method, data.tmm_propotion )

    # normalized_columns = [c for c in norm_df.columns if "normalized_" in c ]
    
    # df_for_pca = norm_df[normalized_columns]

    # pca_before_nrom = get_pca_plot(df, title = "PCA plot [Before normalization]",columns = columns )

    # pca_after_norm = get_pca_plot(norm_df[normalized_columns], title = "PCA plot [After normalization]", columns = columns)

    # box_before_norm = get_box_plot(df)
    
    # box_after_norm = get_box_plot(df)
    
    return {"file_url":file_url}

    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))





