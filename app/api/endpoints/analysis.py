import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
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
    
    df, index_col  = find_index(df,data.accession_column,data.gene_column, data.convert_protein_to_gene)
    
    df.set_index(index_col,inplace = True)

    before_norm_columns = column_dict_to_list(data.column_data)

    df, dropped_df = data_cleaning(df,data.column_data, index_col)

    df_copy = df.copy()

    df = data_imputation(df,data.imputation_method,data.imputation_value)

    df = normalize_data(df, data.norm_method, data.tmm_propotion )

    norm_columns = get_normalized_columns(df.columns)
    
    pca_before_nrom = get_pca_plot(df[before_norm_columns], title = "PCA plot [Before normalization]",columns = data.column_data )

    pca_after_norm = get_pca_plot(df[norm_columns], title = "PCA plot [After normalization]", columns = data.column_data, normalized = True)

    box_before_norm = get_box_plot(df[before_norm_columns], data.exp_type, title = "box plot [Before normalization]",columns = data.column_data)

    box_after_norm = get_box_plot(df[norm_columns],data.exp_type, title = "box plot [After normalization]",columns = data.column_data)
    
    # save_normalized_data()

    return {"analysis_id":data.analysis_id,
            "file_url":file_url,
            "pca_before":pca_before_nrom,
            "pca_after":pca_after_norm,
            "box_before":box_before_norm,
            "box_after":box_after_norm,
                        }
    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))





