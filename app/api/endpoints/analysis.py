from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi import UploadFile, File
from typing import  Literal
import pandas as pd
from sqlalchemy.future import select
from app.api.endpoints import auth
from app.config import Settings
from app.db.models import Analysis,LableFreeAnalysis
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.services.data_processing.data_preprocess import (get_columns , 
                                                           get_file_url, get_file_url_direct_diff, get_norm_columns,
                                                           get_lbl_free_file_url, get_normalized_data_bc,
                                                           get_volcano_meta_data, get_heatmap_data, get_go_data, get_data_frame,
                                                           find_index, column_dict_to_list, get_pathway_list, get_kegg_data)
from app.services.normalization.normalize_pipeline import  norm_pipeline
from app.schema.schemas import MetadataRequest, Normalize , Differential, BatchCorrection, HeatMap, GeneOntology , Kmean , MetadataDirect
from app.services.aws_s3.save_to_s3 import save_df, save_lable_free_df
from app.services.differetial_exp.diff_pipeline import diff_pipeline
from app.services.lable_free.lable_free_analysis import protien_identify
from app.services.normalization.batch_correction import batch_correction_pipeline
from app.services.differetial_exp.diiferential_plots import get_volcano_plot, get_heatmap_plot, get_kmean_plot, get_kegg_pathway
from app.services.differetial_exp.diiferential_plots import go_analysis
import io 

settings = Settings()
 
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
                "exp_type":data.expType,"no_of_batches":data.noOfBatches}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pre-analysis-direct")
async def save_metadata_direct(
    data: MetadataDirect,
    user: dict = Depends(auth.get_current_user), 
    db: AsyncSession = Depends(get_async_session),
):
    # try:

    new_analysis = Analysis(
        user_id=user.id,  
        no_of_test=data.noOfTest,
        no_of_control=data.noOfControl,
        file_url=data.fileUrl,
        direct_differential = True,
    )

    db.add(new_analysis)
    await db.flush() 
    await db.commit() 
    await db.refresh(new_analysis)  

    columns = get_columns(data.fileUrl)  

    return {"analysis_id": new_analysis.id, "columns": columns, "no_of_test":data.noOfTest,"no_of_control":data.noOfControl}

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

@router.post("/normalization")
async def data_normalization(data: Normalize,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),
):
    # try:

    file_url = await get_file_url(data.analysis_id, user, db)

    df = get_data_frame(file_url)
    
    df, index_col  = find_index(df,data.accession_column,data.gene_column, data.convert_protein_to_gene)
    
    cols_to_analyze = column_dict_to_list(data.column_data)

    df_copy = df.drop(columns=cols_to_analyze).copy()

    df_to_alyz = df[cols_to_analyze]
    
    normalized_data,pca_before_nrom,pca_after_norm,box_before_norm,box_after_norm , index_col, control_list ,dropped_df = norm_pipeline(df_to_alyz, data, index_col)

    # create a model to save all the files for an analysis id and save it for zipping
    
    result = await db.execute(select(Analysis).filter(Analysis.id == data.analysis_id))
    analysis = result.scalars().first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found")

    if not df_copy.empty:
        normalized_data = normalized_data.merge(df_copy, left_index=True, right_index=True, how="inner")

    normalized_data_url = save_df(normalized_data, name=f"{data.analysis_id}_normalized_data", file_format = "csv")

    analysis.normalized_data = normalized_data_url
    analysis.index_col = index_col
    analysis.column_data = data.column_data

    await db.commit() 
    
    return {"analysis_id":data.analysis_id,
            "normalized_data":normalized_data_url,
            "pca_before":pca_before_nrom,
            "pca_after":pca_after_norm,
            "box_before":box_before_norm,
            "box_after":box_after_norm,
            "control_list":control_list,
            "exp_type":data.exp_type,
            "column_data": data.column_data,
            "dropped_df": dropped_df
                    }
   



@router.post("/differential-expression-analysis")
async def differentail_analysis(data: Differential,user: dict = Depends(auth.get_current_user),
                                 db: AsyncSession = Depends(get_async_session),):
    # try:    

    if data.direct_differntial:
        index_col = data.gene_column
        columns = data.column_data
        file_url = await get_file_url_direct_diff(data.analysis_id, user, db)
    else:
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
    
    if data.direct_differntial:
        analysis.index_col = data.gene_column

    await db.commit()

    return {"analysis_id":data.analysis_id,"final_df":final_df,"diff_df":diff_df_url,"bargraph":bargraph}

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@router.post("/lable-free-analysis")
async def lable_free(
    quant_method: Literal["ibaq", "nsaf", "top3"] = Form(...),
    digest_enzyme: Literal["trypsin", "lysc", "chymotrypsin"] = Form(...),
    fasta_source: Literal["ncbi", "uniprot"] = Form(...),
    miss_cleavage: int = Form(1),
    min_peptide: int = Form(6),
    max_peptide: int = Form(22),
    fasta_file: UploadFile = File(...),
    analysis_file: UploadFile = File(...),
    user: dict = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session),):

    # try:

    df = await get_lbl_free_file_url(analysis_file)
    file_content_fasta = await fasta_file.read()
    fasta_text = file_content_fasta.decode("utf-8", errors="replace")

    result_df =  protien_identify(df,fasta_text,quant_method, miss_cleavage,
                            min_peptide,max_peptide, digest_enzyme,fasta_source)

    result_head = result_df.head(10).to_dict()

    result_url = save_lable_free_df(result_df)

    new_lable_free = LableFreeAnalysis(
    user_id=user.id,  
    result=result_url,
    )

    db.add(new_lable_free)
    await db.flush() 
    await db.commit() 
    await db.refresh(new_lable_free) 

    return {"result_url":result_url,"result_head":result_head}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-correction")
async def batch_correction(data: BatchCorrection ,user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session),):

    file_url, index_col, columns_data = await get_normalized_data_bc(data.analysis_id, user, db)

    main_df,box_after_batch = batch_correction_pipeline(file_url, index_col,data.batch_data, columns_data, data.analysis_id, data.bc_method)
    
    normalized_data_url = save_df(main_df, name=f"{data.analysis_id}_normalized_batch_corr_data", file_format = "csv")

    q = await db.execute(select(Analysis).filter(Analysis.id == data.analysis_id))
    analysis = q.scalars().first()
    analysis.normalized_data = normalized_data_url
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

    file_url, index_col , metadata = await get_heatmap_data(data, user, db)

    heatmap_plot  = get_heatmap_plot(file_url, index_col , metadata, data)

    return {"heatmap_plot":heatmap_plot}

@router.post("/differential-kmeans")   
async def kmeans_api(data:Kmean ,user: dict = Depends(auth.get_current_user),
                                                     db: AsyncSession = Depends(get_async_session),):
    
    file_url, index_col , metadata = await get_heatmap_data(data, user, db)

    kmean_plot  = get_kmean_plot(file_url, index_col, metadata, data)
    
    return {"kmean_plot":kmean_plot}

@router.post("/gene-ontology")   
async def gene_ontology(data:GeneOntology, user: dict = Depends(auth.get_current_user),
                                                     db: AsyncSession = Depends(get_async_session),):
    # all species can be found here 
    # https://biit.cs.ut.ee/gprofiler/api/util/organisms_list/

    file_url, gene_col = await get_go_data(data.analysis_id, user, db)

    df = get_data_frame(file_url,index_col = gene_col )

    df = df.reset_index()
    genes = df[gene_col].tolist()

    plot, go_data = go_analysis(genes, data.p_value, data.species,data.analysis_id )

    kegg_path_list = get_pathway_list(go_data)
    
    go_data_url = save_df(go_data, name=f"{data.analysis_id}_GO_data", file_format = "csv")

    q = await db.execute(select(Analysis).filter(Analysis.id == data.analysis_id))
    analysis = q.scalars().first()
    analysis.gene_ontology = go_data_url
    await db.commit()

    return {"plot":plot,"go_data_url":go_data_url,'kegg_path_list':kegg_path_list}

@router.post("/kegg-pathway")
async def kegg_pathway(analysis_id: int,pathway:str, user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session)):

    file_url,go_data, gene_col = await get_kegg_data(analysis_id, user, db)

    pathway_image, gene_color = get_kegg_pathway(file_url, gene_col,go_data, pathway)
    
    return {"pathway_image":pathway_image,"gene_color":gene_color}

@router.post("/kegg-pathway")
async def string_db(analysis_id: int,confidence:str, user: dict = Depends(auth.get_current_user),
                             db: AsyncSession = Depends(get_async_session)):
    file_url, gene_col = await get_go_data(analysis_id, user, db)
    df = get_data_frame(file_url,index_col = gene_col )
    df = df.reset_index()
    genes = df[gene_col].tolist()

    return {'genes':genes}
