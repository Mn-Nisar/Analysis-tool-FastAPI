from app.services.imputation.imputation import data_imputation
from app.services.normalization.normalization import normalize_data
from app.services.aws_s3.save_to_s3 import save_df
from app.services.data_processing.data_preprocess import ( data_cleaning,
                                                           get_data_frame,
                                                           find_index, get_normalized_columns, 
                                                           column_dict_to_list)

from app.services.visualization.visualization import get_pca_plot , get_box_plot

def norm_pipeline(data,file_url):
    
    df = get_data_frame(file_url)
    
    df, index_col  = find_index(df,data.accession_column,data.gene_column, data.convert_protein_to_gene)
    
    df.set_index(index_col,inplace = True)

    before_norm_columns = column_dict_to_list(data.column_data)

    df, dropped_df = data_cleaning(df,data.column_data, index_col)

    df_copy = df.copy()

    df = data_imputation(df,data.imputation_method,data.imputation_value)

    df = normalize_data(df, data.norm_method, data.tmm_propotion )

    
    norm_columns = get_normalized_columns(df.columns)
    
    normalized_data = save_df(df[norm_columns], name=f"{data.analysis_id}_normalized_data", file_format = "csv")
    
    pca_before_nrom = get_pca_plot(df[before_norm_columns], title = "PCA plot [Before normalization]",columns = data.column_data, analysis_id=data.analysis_id )

    pca_after_norm = get_pca_plot(df[norm_columns], title = "PCA plot [After normalization]", columns = data.column_data,analysis_id=data.analysis_id, normalized = True)

    box_before_norm = get_box_plot(df[before_norm_columns], data.exp_type, title = "box plot [Before normalization]",analysis_id=data.analysis_id,columns = data.column_data)

    box_after_norm = get_box_plot(df[norm_columns],data.exp_type, title = "box plot [After normalization]",analysis_id=data.analysis_id,columns = data.column_data)

    return normalized_data,pca_before_nrom,pca_after_norm,box_before_norm,box_after_norm ,index_col, df_copy , dropped_df
 