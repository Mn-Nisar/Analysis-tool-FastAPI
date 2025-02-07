import pandas as pd

def get_columns(url, file_type, *args, **kwargs):
    if file_type == 'csv':
        columns = pd.read_csv(url, nrows=0).columns.tolist()
    elif file_type == 'xlsx':
        columns = pd.read_excel(url, nrows=0).columns.tolist()
    elif file_type == 'txt':
        columns = pd.read_csv(url, delimiter="\t", nrows=0).columns.tolist()
    else:
        raise ValueError("Unsupported file type. Use .txt, .xlsx, or .csv")
    
    return columns

# Example usage:
# columns = get_columns("data.csv", ".csv")
# print(columns)

