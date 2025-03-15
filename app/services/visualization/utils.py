

def format_circ_df(df,meta_data):
    # circular barplot code takes  column nmaes =[name, value, group]
    # META DATA SHOULD HAVE KEYS term_name, group, source
    # meta_data = {
    #     "term_name": "foo",
    #     "group": "xyz",
    #     "source": "blA",
    # }

    df.rename(columns={meta_data["term_name"]:"name",meta_data["group"]:"group",meta_data["source"]:"value"}, inplace=True)

    return df
