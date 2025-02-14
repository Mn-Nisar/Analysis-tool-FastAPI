from app.services.data_processing.data_preprocess import get_data_frame
from app.services.differetial_exp.p_value import calc_p_value


def diff_pipeline(file_url,data, columns, idex_col):
    
    df = get_data_frame(file_url,index_col=idex_col)

    df = calc_p_value(df,columns,data)

    