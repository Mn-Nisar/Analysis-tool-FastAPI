import pandas as pd
from app.services.imputation.imputation import data_imputation
from itertools import chain
from app.services.normalization.normalization import data_normalization
def normalize_data(args):

    file_url="app/analysis-files/TECHNICAL_20250205084824.csv"


    columns = { "test":[["Abundance R1 127N Sample","Abundance R3 127N Sample","Abundance R2 127N Sample"],["Abundance R1 127C Sample","Abundance R3 127C Sample","Abundance R2 127C Sample"],
                        ["Abundance R1 128N Sample","Abundance R3 128N Sample","Abundance R2 128N Sample"],["Abundance R1 128C Sample","Abundance R3 128C Sample","Abundance R2 128C Sample"],
                        ["Abundance R1 129N Sample","Abundance R3 129N Sample","Abundance R2 129N Sample"],["Abundance R1 129C Sample","Abundance R3 129C Sample","Abundance R2 129C Sample"],
                        ["Abundance R1 130N Sample","Abundance R3 130N Sample","Abundance R2 130N Sample"],["Abundance R1 130C Sample","Abundance R3 130C Sample","Abundance R2 130C Sample"]],
                "control":[["Abundance R1 126 control","Abundance R2 126 control","Abundance R3 126 control"]]}
    
    test_columns = columns["test"] 

    control_column = columns["control"]

    df_columns  = list(chain.from_iterable(test_columns)) + list(chain.from_iterable(control_column))


    # https://chatgpt.com/c/67a46312-5b10-800f-8c88-cabcca1a8e92
    # pd.read_parquet()

    df = pd.read_csv(file_url)

    # missing value imputation
    df = data_imputation(df,df_columns,args.imputation_value,args.imputation_method)
    
    # data normalization
    df = data_normalization(df,columns,args.norm_method)
    print(df)