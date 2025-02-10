from fastapi import HTTPException
import pandas as pd
from sqlalchemy.future import select
from app.db.models import Analysis
from app.services.external_api import gprofiler_api

def get_columns(url,*args, **kwargs):
    columns = pd.read_parquet(url, nrows=0).columns.tolist()
    return columns

def data_cleaning(df):
    
    df.dropna(how='all',inplace = True)

    return df

async def get_file_url(data, user, db):
    stmt = select(Analysis).where(
        Analysis.id == data.analysis_id,
        Analysis.user_id == user.id
    )
    result = await db.execute(stmt)
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
    return analysis.file_url

def get_data_frame(url):
    df = pd.read_parquet(url)
    return df

def filter_dataframe(df,accession_column,gene_column, convert_protein_to_gene, column_data):
            
        if (gene_column or convert_protein_to_gene) and accession_column:
            con_df , gs_convert_success = gprofiler_api.convert_acc_to_gene(df[accession_column].tolist())

            if gs_convert_success:
                df[accession_col] = df[accession_col].apply(lambda x: x.split(';')[0] if ';' in x else x)
                df = df.merge(con_df,left_on = accession_col , right_on='Accesion_gf' , how = 'left' , suffixes = (None , '_y'))
                df.drop('Accesion_gf', axis=1, inplace=True)
                final_key = "_GENE_SYMBOL_"
            else:
                final_key = accession_col
                
        if gene_column != None and accession_column == None:
            accession_col = gene_col

