import json
import requests
import io
import pandas as pd
from app.services.external_api.aws import create_s3_object

LIMMA_API_URL='http://limma_api:8000'

def batch_correct_limma(df, batches_list, job_id):
    
    object_id = str(job_id)+"for_batch.csv"
    batches = json.dumps(batches_list)
    create_s3_object(df,object_id)
    params = {'batches':batches, 's3Object':object_id}
    batch_correct_api = requests.post(f"{LIMMA_API_URL}/remove_batch_effect", params=params)    
    json_data = json.load(io.BytesIO(batch_correct_api.content))
    btc_df = pd.DataFrame(json_data,columns=list(df.columns))
    
    return btc_df
    