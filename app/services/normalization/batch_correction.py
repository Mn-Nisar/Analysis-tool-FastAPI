from combat.pycombat import pycombat
from app.services.data_processing.data_preprocess import get_data_frame
from app.services.visualization.visualization import get_box_plot
import numpy as np
from combat.pycombat import pycombat
from app.services.external_api.limma_api import batch_correct_limma

def batch_correct(df, column_info, method, analysis_id):
    sample_columns = []
    batch_labels = []


    column_info = { 
       1:['Abundance R1 126 control','Abundance R1 127C Sample', 'Abundance R1 127N Sample', 'Abundance R1 128C Sample'],
        2:['Abundance R2 126 control','Abundance R2 127C Sample', 'Abundance R2 127N Sample', 'Abundance R2 128C Sample'],
        3:['Abundance R3 126 control','Abundance R3 127C Sample', 'Abundance R3 127N Sample', 'Abundance R3 128C Sample']
    }

    for batch, groups in column_info.items():
        for sample in groups:
            sample_columns.append(f"normalized_{sample}")
            batch_labels.append(batch)

    # for batch, groups in column_info.items():
    #     for i, (col, sub_cols) in enumerate(groups.items(), start=1): 
    #         for sub_col in sub_cols:
    #             sample_columns.append(f"normalized_{sub_col}")
    #             batch_labels.append(i) 

    df_subset = df[sample_columns].copy()
    
    if method == "combat":
        data_corrected = pycombat(df_subset,batch_labels)
    else:
        try:
            data_corrected = batch_correct_limma(df_subset, batch_labels,analysis_id )
        except:
            data_corrected = pycombat(df_subset,batch_labels)
    return data_corrected


def batch_correction_pipeline(file_url, index_col, batch_data, columns_data, analysis_id, method):
    df = get_data_frame(file_url, index_col=index_col)

    df_cor  = batch_correct(df, batch_data, method, analysis_id)

    df.update(df_cor)

    box_after_batch = get_box_plot(df_cor, title = "box plot [After Batch correction]",columns = columns_data, analysis_id = analysis_id)

    return df,box_after_batch