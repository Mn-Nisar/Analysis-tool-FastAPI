from app.services.data_processing.data_preprocess import get_data_frame
from app.services.differetial_exp.p_value import calc_p_value
from app.services.differetial_exp.foldchange import calc_foldchange
from app.services.visualization.visualization import result_bar_graph


def get_diff_df(df,data):
    expression_cols = [i for i in df.columns if i.startswith('expression_')]
    
    if data.ratio_log2 == "log2_fc":
        diff_df = df[[i for i in df.columns if i.startswith('expression_') or i.startswith('log2_fc_') ]]
    else:
        diff_df = df[[i for i in df.columns if i.startswith('expression_') or i.startswith('fold_change_') ]]
    diff_df = diff_df.dropna(subset=expression_cols, how='all')

    return diff_df

def diff_pipeline(file_url,data, columns, idex_col):

    df = get_data_frame(file_url,index_col=idex_col, direct = True)

    df = calc_p_value(df,columns,data.choose_control,data.pv_method)

    df = calc_foldchange(df,columns,data.choose_control,data)

    diff_df = get_diff_df(df,data)

    bargraph = result_bar_graph(diff_df, data.analysis_id)

    return df,diff_df,bargraph 
    





    