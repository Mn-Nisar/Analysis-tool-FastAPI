from missforest.missforest import MissForest

def impute_with_lowest5(df):
    try:   
        min_values = df.min(skipna=True)  
        replacement_values = min_values / 5 
        return df.fillna(replacement_values) 
    except:
        return Exception

def missforest_impute(df):
    # df = df.dropna(how='all')
    imputer = MissForest()
    df = imputer.fit_transform(df)
    return df


imputation_method = ["value","one_fifth","miss_forest"]

def data_imputation(df,imputation_method,imputation_value,*args, **kwargs):
    
    if imputation_method == 'one_fifth':
        df = impute_with_lowest5(df)

    elif imputation_method== 'miss_forest':
        df = missforest_impute(df)
    else:
        df.fillna(imputation_value, inplace = True)

    return df