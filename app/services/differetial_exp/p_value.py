import pandas as pd
from scipy import stats
import numpy as np
import statsmodels.formula.api as smf
import statsmodels.api as sm


def two_way_anova(data):
    """
    Perform a two-way ANOVA on the given dataset.
    The dataset should contain three columns: 'Group' (Sample1, Sample2, Control), 'Replication', and 'Value'.
    """
    model = smf.ols('Value ~ C(Group) + C(Replication) + C(Group):C(Replication)', data=data).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    return anova_table

def perform_two_way_anova(row, columns):
    """
    Perform two-way ANOVA for a given row based on the columns dictionary.
    """
    data = []
    for group, replications in columns['test'].items():
        for i, col in enumerate(replications):
            data.append([group, i + 1, row[col]])
    
    for group, replications in columns['control'].items():
        for i, col in enumerate(replications):
            data.append([group, i + 1, row[col]])
    
    df = pd.DataFrame(data, columns=['Group', 'Replication', 'Value'])

    anova_results = two_way_anova(df)
    return anova_results.loc['C(Group)', 'PR(>F)']


def one_way_anova(data):
    """
    Perform a one-way ANOVA on the given dataset.
    The dataset should contain two columns: 'Group' (Sample1, Sample2, Control) and 'Value'.
    """
    model = smf.ols('Value ~ C(Group)', data=data).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    return anova_table

def perform_one_way_anova(row, columns):
    """
    Perform one-way ANOVA for a given row based on the columns dictionary.
    """
    data = []
    for group, replications in columns['test'].items():
        for col in replications:
            data.append([group, row[col]])
    
    for group, replications in columns['control'].items():
        for col in replications:
            data.append([group, row[col]])
    
    df = pd.DataFrame(data, columns=['Group', 'Value'])
    anova_results = one_way_anova(df)
    return anova_results.loc['C(Group)', 'PR(>F)']  # Returning p-value for Group



def calc_p_value(df,columns,control_name,p_val_type):
    if p_val_type == "weltch":
        for s in columns["test"]:
            df[s+"_avg"] = df[columns["test"][s]].mean(axis=1)
            
            _,df["p_value_"+s]= stats.ttest_ind(df[columns["control"][control_name]],df[columns["test"][s]],axis=1, equal_var = False)
            df["-log10_pvalue"+s] = abs(np.log10(df["p_value_"+s]))
    
    elif p_val_type == "ttest":
        for s in columns["test"]:
            df[s+"_avg"] = df[columns["test"][s]].mean(axis=1)

            _,df["p_value_"+s]= stats.ttest_ind(df[columns["control"][control_name]],df[columns["test"][s]],axis=1, equal_var = True)
            df["-log10_pvalue"+s] = abs(np.log10(df["p_value_"+s]))
    
    elif p_val_type == 'two_anova':
        
        df['p_value_2_way_anova'] = df.apply(lambda x: perform_two_way_anova(x, columns), axis=1)
        df["-log10_pvalue"] = abs(np.log10(df["p_value_2_way_anova"]))

    elif p_val_type== "one_anova":
        df['p_value_one_way_anova'] = df.apply(lambda x: perform_one_way_anova(x, columns), axis=1)
        df["-log10_pvalue"] = abs(np.log10(df["p_value_one_way_anova"]))


    elif p_val_type== "limma":
        pass
        # rename_cols,matrix =  get_columns_and_matrix(columns)
        # limma_df = limma_diff_API(df,matrix,rename_cols,analysis_id)
        # df = pd.concat([df, limma_df], axis=1)
        # concat the data and return df

    return df 

