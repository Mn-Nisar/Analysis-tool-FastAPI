from scipy.stats import ttest_ind


def calc_p_value(df,columns,data):
    """
    Calculate p-value for differential expression analysis
    """
    if data.pv_method == "weltch":
        for samples in columns["test"]:
            df[samples] = df[samples].apply(lambda x: x.replace(",",".")).astype(float)
    