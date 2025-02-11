import pandas as pd 
import numpy as np 
from scipy.stats import zscore
from scipy import stats
from fastapi import HTTPException

def normalize_data(df,method,tmm_propotion ,*args, **kwargs):
    
    if (method == 'median'):
        median_dict = df.median().to_dict()
        min_median = min(median_dict.values())
        m_factor = {col: median / min_median for col, median in median_dict.items()}
        
        for col in df.columns:
            df[f'normalized_{col}'] = df[col] * m_factor[col]

        return df
    
    elif (method == 'sum'):
        mean_dict = df.mean().to_dict()
        min_mean = min(mean_dict.values())
        m_factor = {col: mean / min_mean for col, mean in mean_dict.items()}
        
        for col in df.columns:
            df[f'normalized_{col}'] = df[col] * m_factor[col]

        return df
    
    elif (method == 'quantile'):
        df_main = df.copy()
        df_sorted = pd.DataFrame(np.sort(df.values,
                                     axis=0),
                             index=df.index,
                             columns=df.columns)
        df_mean = df_sorted.mean(axis=1)
        df_mean.index = np.arange(1, len(df_mean) + 1)
        df_qn =df.rank(method="min").stack().astype(int).map(df_mean).unstack()
        df_qn.rename(lambda x: "normalized_"+x, axis='columns', inplace = True)

        df_main = df_main.join(df_qn)
        
        return df_main
    
    elif (method == "irs"):
        Q1 = df.quantile(0.25)
        Q3 = df.quantile(0.75)

        IQR = Q3 - Q1

        df_irs = (df - Q1) / IQR

        df_irs = df_irs.add_prefix("normalized_")

        df_final = pd.concat([df, df_irs], axis=1) 

        return df_final
    
    elif (method == "z_score"):
        df_main = df.copy()
        df_zscore= zscore(df)
        df_zscore.rename(lambda x: "normalized_"+x, axis='columns', inplace = True)
        df = df.join(df_zscore)

        return df

    elif method == "tmm":
        prcount = tmm_propotion / 100
        tmm_dict = {col: stats.trim_mean(df[col], prcount) for col in df.columns}
        min_tmm = min(tmm_dict.values())
        m_factor = {col: tmm / min_tmm for col, tmm in tmm_dict.items()}
        for col in df.columns:
            df[f'normalized_{col}'] = df[col] * m_factor[col]
        
        return df
    
    else:
        raise HTTPException(status_code=400, detail="Choose a valid normalization method.")