import numpy as np

def calc_foldchange(df,columns,control_name,data):

    for group, replications in columns['test'].items():
        df[f'fold_change_{group}'] = df[replications].mean(axis = 1) / df[columns['control'][control_name]].mean(axis = 1)
        df[f'log2_fc_{group}'] = np.log2(df[f'fold_change_{group}'])
        
        if data.ratio_log2 == "log2_fc":
            df.loc[(df[f'log2_fc_{group}'] >= data.log2_fc_cutoff ) & (df[f'p_value_{group}'] <= data.pv_cutoff),f"expression_{group}" ] = "up-regulated"
            df.loc[(df[f'log2_fc_{group}'] <= -data.log2_fc_cutoff ) & (df[f'p_value_{group}'] <= data.pv_cutoff), f"expression_{group}" ] = "down-regulated"
        else:
            df.loc[(df[f'fold_change_{group}'] >= data.ratio_cut_up ) & (df[f'p_value_{group}'] <= data.pv_cutoff), f"expression_{group}"] = "up-regulated"
            df.loc[(df[f'fold_change_{group}'] <= data.ratio_cut_down ) & (df[f'p_value_{group}'] <= data.pv_cutoff), f"expression_{group}"] = "down-regulated"

    return df