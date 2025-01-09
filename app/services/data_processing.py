import pandas as pd

def clean_data(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data)
    # Apply cleaning logic
    df.dropna(inplace=True)
    return df
