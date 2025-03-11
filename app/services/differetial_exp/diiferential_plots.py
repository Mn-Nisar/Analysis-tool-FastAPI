from app.services.data_processing.data_preprocess import get_data_frame
from app.services.visualization.visualization import (plot_volcano_diff, plot_heatmap,
                                                       plot_elbow_plot, plot_kmeans_plot,
                                                       get_circbar_plot)
from app.services.external_api.gprofiler_api import get_gene_ontology

def get_columns(col, metadata):
    pv_methods = {
        "two_anova": "p_value_2_way_anova",
        "one_anova": "p_value_one_way_anova"
    }
    p_val_col = pv_methods.get(metadata["pv_method"], f"p_value_{col}")
    fc_col = f'{"ratio" if metadata["ratio_or_log2"] == "ratio" else "log2_fc"}_{col}'

    return [p_val_col, fc_col], p_val_col, fc_col

def get_tile(col,control_name):
    return f"{col} vs {control_name}" 

def get_volcano_plot(file_url, index_col, columns_data, metadata,analysis_id):

    volcano_plots = []
    df = get_data_frame(file_url, index_col=index_col)    
    for col in columns_data["test"]:
        columns, p_val_col, fc_col = get_columns(col,metadata)
        title = get_tile(col,metadata["control_name"])
        vol_df = df[columns].reset_index()

        volcano_plot_url,expressed_genes = plot_volcano_diff(vol_df,fc_col,p_val_col,metadata["log2_cut"],metadata["pv_cutoff"],index_col,title, analysis_id)
        volcano_plots.append([volcano_plot_url,expressed_genes])

    return volcano_plots


def filter_columns(df): 

    if any(i.startswith('log2_fc_') for i in df.columns):
        df = df[[i for i in df.columns if i.startswith('log2_fc_') ]]
    else:
        df = df[[i for i in df.columns if i.startswith('fold_change_') ]]

    return df

def get_heatmap_plot(file_url, index_col, metadata, data):
    df = get_data_frame(file_url, index_col=index_col)
    
    df = filter_columns(df)

    both = True if metadata["ratio_or_log2"] == "log2_fc" else False
    fc_left = metadata["ratio_down"]
    fc_right = metadata["ratio_up"]
    lg2cut = metadata["log2_cut"]
    z_convert = data.z_score
    
    if data.method ==  "heirarchial":
        plot  = plot_heatmap(df,both,fc_left,fc_right,lg2cut , z_convert, data.analysis_id)

    else:
        plot  = plot_elbow_plot(df,data.analysis_id )

    return plot


def get_kmean_plot(file_url, index_col, metadata, data):
    
    df = get_data_frame(file_url, index_col=index_col)

    df = filter_columns(df)

    both = True if metadata["ratio_or_log2"] == "log2_fc" else False
    
    fc_left = metadata["ratio_down"]
    fc_right = metadata["ratio_up"]
    lg2cut = metadata["log2_cut"]

    plot = plot_kmeans_plot(df, data.k_value ,fc_left,fc_right,lg2cut,both, data.analysis_id)

    return plot

def go_analysis(genes, p_value, species, analysis_id):
    go = get_gene_ontology(genes, p_value, species)
    circbar = get_circbar_plot(go, analysis_id)
    print("circbarcircbarcircbarcircbarcircbarcircbarcircbarcircbarcircbarcircbarcircbarcircbar",circbar)
    return circbar, go 