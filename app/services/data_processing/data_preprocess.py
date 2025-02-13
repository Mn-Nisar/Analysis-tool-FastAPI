from fastapi import HTTPException
import pandas as pd
from sqlalchemy.future import select
from app.db.models import Analysis
from app.services.external_api import gprofiler_api

def get_columns(url,*args, **kwargs):
    columns = pd.read_parquet(url, columns=None).columns.tolist()
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
    return [c for c in columns if "normalized_" in c ]

