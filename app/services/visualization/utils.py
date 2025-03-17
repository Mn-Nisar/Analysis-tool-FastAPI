

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


def get_volcano_metadata(meta_data):

    genes = meta_data["selected_index"]
    lfc = meta_data["fold_change"]
    pv = meta_data["p_value"]
    lg2cut = meta_data["log2_cut"]

    return genes, lfc, pv, lg2cut