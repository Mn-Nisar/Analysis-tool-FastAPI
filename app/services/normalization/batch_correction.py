from combat.pycombat import pycombat
from app.services.data_processing.data_preprocess import get_data_frame
from app.services.visualization.visualization import get_box_plot
import numpy as np
from combat.pycombat import pycombat
from app.services.external_api.limma_api import batch_correct_limma

def batch_correct(df, column_info, method, analysis_id):
    sample_columns = []
    batch_labels = []

    for batch, groups in column_info.items():
        for col_type in ["test", "control"]:
            for col in groups[col_type]:
                sample_columns.append(f"normalized_{col}")
                batch_labels.append(batch)  
    
    df_subset = df[sample_columns].copy()


    unique_batches = {batch: i for i, batch in enumerate(set(batch_labels))}
    batch_numeric = np.array([unique_batches[batch] for batch in batch_labels])
    if method == "combat":
        data_corrected = pycombat(df_subset,batch_numeric)
    else:
        try:
            data_corrected = batch_correct_limma(df_subset, batch_numeric,analysis_id )
        except:
            data_corrected = pycombat(df_subset,batch_numeric)
    return data_corrected


def batch_correction_pipeline(file_url, index_col, batch_data, columns_data, analysis_id, method):
    df = get_data_frame(file_url, index_col=index_col)
    df.set_index(index_col, inplace=True)
    df_cor = batch_correct(df, batch_data, method, analysis_id)

    box_after_batch = get_box_plot(df_cor, title = "box plot [After Batch correction]",columns = columns_data, analysis_id = analysis_id)

    return df_cor,box_after_batch