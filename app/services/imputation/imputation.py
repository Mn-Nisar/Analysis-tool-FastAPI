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


def data_imputation(df,df_columns,imputation_value,imputation_method,*args, **kwargs):
    
    if imputation_method == 'impute-lowest5':
        df = impute_with_lowest5(df)

    elif imputation_method== 'miss-forest':
        df = missforest_impute(df)
    else:
        df.fillna(imputation_value, inplace = True)

    return df