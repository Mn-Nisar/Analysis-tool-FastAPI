from fastapi import HTTPException
import pandas as pd
from sqlalchemy.future import select
from app.db.models import Analysis

def get_columns(url, file_type, *args, **kwargs):
    if file_type == 'csv':
        columns = pd.read_csv(url, nrows=0).columns.tolist()
    elif file_type == 'xlsx':
        columns = pd.read_excel(url, nrows=0).columns.tolist()
    elif file_type == 'txt':
        columns = pd.read_csv(url, delimiter="\t", nrows=0).columns.tolist()
    else:
        raise ValueError("Unsupported file type. Use .txt, .xlsx, or .csv")
    
    return columns

# Example usage:
# columns = get_columns("data.csv", ".csv")
# print(columns)

def data_cleaning(df):
    
    df.dropna(how='all',inplace = True)

    return df


async def get_file_url(data, user, db):
    stmt = select(Analysis).where(
        Analysis.id == data.analysis_id,
        Analysis.user_id == user["id"]
    )
    result = await db.execute(stmt)
    analysis = result.scalars().first()

    # If no analysis found, raise an error
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
    return analysis.file_url
