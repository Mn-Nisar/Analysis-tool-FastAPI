import os
from fastapi import HTTPException
import pandas as pd
from sqlalchemy.future import select
from app.db.models import Analysis
from app.services.external_api import gprofiler_api
from app.config import Settings

settings = Settings()

PRODUCTION = settings.is_production

def get_columns(url,*args, **kwargs):
    columns = pd.read_csv(url, nrows=0).columns.tolist()
    return columns

def column_dict_to_list(column_dict):
    return [item for category in column_dict.values() for sublist in category.values() for item in sublist]

def data_cleaning(df, columns_dict, index_col):
    
    filtered_test = list(columns_dict["test"].values())
    filtered_control = list(columns_dict["control"].values())
    columns = filtered_test+filtered_control
    mask = df.apply(lambda row: all(row[sample].isnull().sum() < 2 for sample in columns), axis=1)
    filtered_df = df[mask]
    dropped_df = df[~mask]

    return filtered_df, dropped_df

async def get_file_url(analysis_id, user, db, *args,**kwargs):
    stmt = select(Analysis).where(
        Analysis.id == analysis_id,
        Analysis.user_id == user.id
    )
    result = await db.execute(stmt)
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
    
    if kwargs.get("get_normalized"):
        return analysis.normalized_data, analysis.index_col, analysis.column_data
    
    else:
        return analysis.file_url

async def get_volcano_meta_data(analysis_id, user, db, *args,**kwargs):
    stmt = select(Analysis).where(
        Analysis.id == analysis_id,
        Analysis.user_id == user.id
    )
    result = await db.execute(stmt)
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
    
    metadata = {
        "pv_cutoff": analysis.pv_cutoff,
        "ratio_or_log2":analysis.ratio_or_log2,
        "ratio_up": analysis.ratio_up,
        "ratio_down": analysis.ratio_down,
        "log2_cut": analysis.log2_cut,
        "control_name": analysis.control_name,
        "pv_method": analysis.pv_method
        }
    
    return analysis.file_url, analysis.index_col, analysis.column_data , metadata


async def get_heatmap_data(data,user, db, *args,**kwargs):

    stmt = select(Analysis).where(
        Analysis.id == data.analysis_id,    
        Analysis.user_id == user.id
    )
    result = await db.execute(stmt)
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")

    metadata = {
        # "pv_cutoff": analysis.pv_cutoff,
        "ratio_or_log2":analysis.ratio_or_log2,
        "ratio_up": analysis.ratio_up,
        "ratio_down": analysis.ratio_down,
        "log2_cut": analysis.log2_cut,
        "control_name": analysis.control_name,
        }
    
    return analysis.file_url, analysis.index_col, analysis.column_data , metadata



async def get_normalized_data_bc(analysis_id, user, db, *args,**kwargs):
    stmt = select(Analysis).where(
        Analysis.id == analysis_id,
        Analysis.user_id == user.id
    )
    result = await db.execute(stmt)
    analysis = result.scalars().first()
    if not analysis:    
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
    return analysis.normalized_data, analysis.index_col, analysis.batch_data, analysis.column_data

async def get_go_data(analysis_id, user, db, *args,**kwargs):
    stmt = select(Analysis).where(
        Analysis.id == analysis_id,
        Analysis.user_id == user.id
    )
    result = await db.execute(stmt)
    analysis = result.scalars().first()
    if not analysis:    
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
    genes = pd.read_csv(analysis.normalized_data, usecols=[analysis.index_col])
    return genes[analysis.index_col].tolist()

def get_data_frame(url,*args,**kwargs):
    if PRODUCTION:
        if kwargs.get('index_col'):

            df = pd.read_csv(url, index_col=kwargs['index_col'])
        else:
            df = pd.read_csv(url)
        return df
    else:
        filename = url.split("/")[-1].strip()
        local_path = os.path.join("app", "static_files", filename)        
        if kwargs.get('index_col'):
            df = pd.read_csv(local_path, index_col=kwargs['index_col'])
        else:
            df = pd.read_csv(url)
        return df

def modify_duplicates(val):
    occurrences = {}

    if val in occurrences:
        occurrences[val] += 1
        return val + " " * occurrences[val]  # Add spaces
    else:
        occurrences[val] = 0
        return val
    
def find_index(df,accession_column,gene_column, convert_protein_to_gene):
    final_key = accession_column
    if (gene_column == None or convert_protein_to_gene) and accession_column:
        con_df , gs_convert_success = gprofiler_api.convert_acc_to_gene(df[accession_column].tolist())

        if gs_convert_success:
            df[accession_column] = df[accession_column].apply(lambda x: x.split(';')[0] if ';' in x else x)
            df = df.merge(con_df,left_on = accession_column , right_on='Accesion_gf' , how = 'left' , suffixes = (None , '_y'))
            df.drop('Accesion_gf', axis=1, inplace=True)
            final_key = "_GENE_SYMBOL_"
        else:
            final_key = accession_column
            
    if gene_column != None and accession_column == None:
        final_key = gene_column

    df = df.loc[df[final_key] != 'sp'] 

    df[final_key] = df[final_key].apply(modify_duplicates)

    return df, final_key

def get_normalized_columns(columns):
    
    return ["normalized_"+item for category in columns.values() for sublist in category.values() for item in sublist]

def get_norm_columns(columns_data):
    for category, samples in columns_data.items():
        for sample, values in samples.items():
            samples[sample] = [f"normalized_{val}" for val in values]
    return columns_data


def get_control_list(columns_data):
    return list(columns_data["control"].keys())

def get_lbl_free_file_url(data):
    df = pd.read_csv(data.analysis_file)
    fasta_url = data.fasta_url
    return df, fasta_url

def get_batch_data(data, column_names):

    transformed_data = {"test": {}, "control": {}}

    sample_values = list(data["test"].values())
    grouped_samples = list(map(list, zip(*sample_values))) if sample_values else []

    control_values = list(data["control"].values())
    grouped_control = list(map(list, zip(*control_values))) if control_values else []

    transformed_data["test"] = dict(zip(column_names["test"], grouped_samples))
    transformed_data["control"] = dict(zip(column_names["control"], grouped_control))

    return transformed_data

