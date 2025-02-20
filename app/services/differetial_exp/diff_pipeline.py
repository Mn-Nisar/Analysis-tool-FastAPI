from app.services.data_processing.data_preprocess import get_data_frame
from app.services.differetial_exp.p_value import calc_p_value
from app.services.differetial_exp.foldchange import calc_foldchange
from app.services.visualization.visualization import result_bar_graph


def diff_pipeline(file_url,data, columns, idex_col):
    
    df = get_data_frame(file_url,index_col=idex_col)

    df = calc_p_value(df,columns,data.choose_control,data.pv_method)

    df, diff_df = calc_foldchange(df,columns,data.choose_control,data)

    bargraph = result_bar_graph(diff_df, data.analysis_id)

    return df,diff_df,bargraph
    





    