from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.api.endpoints import auth
from app.config import Settings
from app.db.models import Analysis,LableFree
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.services.data_processing.data_preprocess import (get_columns , 
                                                           get_file_url, get_norm_columns,
                                                           get_lbl_free_file_url, get_normalized_data_bc,
                                                           get_volcano_meta_data, get_heatmap_data)
from app.services.normalization.normalize_pipeline import  norm_pipeline
from app.schema.schemas import MetadataRequest, Normalize , Differential, LableFree, BatchCorrection, HeatMap
from app.services.aws_s3.save_to_s3 import save_df, save_lable_free_df
from app.services.differetial_exp.diff_pipeline import diff_pipeline
from app.services.lable_free.lable_free_analysis import protien_identify
from app.services.normalization.batch_correction import batch_correction_pipeline
from app.services.differetial_exp.diiferential_plots import get_volcano_plot, get_heatmap_plot
settings = Settings()

 
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
            "exp_type":data.expType,"no_of_batches":data.noOfBatches}

# except Exception as e:
#     raise HTTPException(status_code=500, detail=str(e))


@router.post("/normalization")
async def data_normalization(data: Normalize,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),
):
    # try:

    file_url = await get_file_url(data.analysis_id, user, db)
    

    normalized_data,pca_before_nrom,pca_after_norm,box_before_norm,box_after_norm , index_col, control_list, df_copy , dropped_df = norm_pipeline(data,file_url)

    # create a model to save all the files for an analysis id and save it for zipping
    
    result = await db.execute(select(Analysis).filter(Analysis.id == data.analysis_id))
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")
    
    analysis.normalized_data = normalized_data
    analysis.index_col = index_col
    analysis.column_data = data.column_data
    analysis.batch_data = data.batch_data
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
    try:    
        file_url, index_col, columns_data = await get_file_url(data.analysis_id, user, db, get_normalized=True)
        
        columns = get_norm_columns(columns_data)

        df,diff_df,bargraph  = diff_pipeline(file_url,data, columns, index_col)
        final_df = save_df(df, name=f"{data.analysis_id}_final_data", file_format = "csv")
        diff_df_url = save_df(diff_df, name=f"{data.analysis_id}_differential_data", file_format = "csv")

        q = await db.execute(select(Analysis).filter(Analysis.id == data.analysis_id))
        analysis = q.scalars().first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis record not found")
        
        analysis.pv_method = data.pv_method
        analysis.pv_cutoff = data.pv_cutoff
        analysis.ratio_or_log2 = data.ratio_log2
        analysis.ratio_up = data.ratio_cut_up
        analysis.ratio_down = data.ratio_cut_down
        analysis.log2_cut =  data.log2_fc_cutoff
        analysis.control_name = data.choose_control
        analysis.final_data = final_df
        analysis.diffential_data = diff_df_url

        await db.commit()

        return {"analysis_id":data.analysis_id,"final_df":final_df,"diff_df":diff_df_url,"bargraph":bargraph}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lable-free-analysis")
async def lable_free(data: LableFree, user: dict = Depends(auth.get_current_user),
                     db: AsyncSession = Depends(get_async_session),):
    try:
        df, fasta_url = await get_lbl_free_file_url(data)
        
        result_head = df.head(10).to_dict()

        result_df =  protien_identify(df,fasta_url,data.quant_method, data.miss_cleavage,
                             data.min_peptide,data.max_peptide, data.digest_enzyme, data.fasta_source)

        result_url = save_lable_free_df(result_df)


        new_lable_free = LableFree(
        user_id=user.id,  
        result=result_url,
        )
    
        db.add(new_lable_free)
        await db.flush() 
        await db.commit() 
        await db.refresh(new_lable_free) 

        return {"result_url":result_url,"result_head":result_head}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-correction")
async def batch_correction(data: BatchCorrection ,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),):

    file_url, index_col,batch_data, columns_data = await get_normalized_data_bc(data.analysis_id, user, db)

    df_cor,box_after_batch = batch_correction_pipeline(file_url, index_col, batch_data, columns_data, data.analysis_id, data.bc_method)

    q = await db.execute(select(Analysis).filter(Analysis.id == data.analysis_id))
    analysis = q.scalars().first()
    analysis.normalized_data = df_cor
    await db.commit()
    return {"analysis_id":data.analysis_id,"box_after_batch":box_after_batch}


@router.post("/differential-volcano-plot")
async def volcano_plot_api(analysis_id: int,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),):
    
    file_url, index_col, columns_data , metadata = await get_volcano_meta_data(analysis_id, user, db)
    
    volcano_plots = get_volcano_plot(file_url, index_col, columns_data, metadata,analysis_id )

    return {"volcano_plots":volcano_plots}



@router.post("/differential-heatmap")
async def heatmap_api(data:HeatMap ,user: dict = Depends(auth.get_current_user),
                                                     db: AsyncSession = Depends(get_async_session),):

    file_url, index_col, columns_data , metadata = await get_heatmap_data(data, user, db)

    heatmap_plot  = get_heatmap_plot(file_url, index_col, columns_data, metadata, data)