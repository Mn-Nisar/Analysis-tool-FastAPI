from app.services.data_processing.data_preprocess import get_data_frame
from app.services.visualization.visualization import plot_volcano_diff, plot_heatmap, plot_elbow_plot

columns = { "test":{"127N Sample":["Abundance R1 127N Sample","Abundance R3 127N Sample","Abundance R2 127N Sample"],"127C Sample":["Abundance R1 127C Sample","Abundance R3 127C Sample","Abundance R2 127C Sample"],
                        "128N Sample":["Abundance R1 128N Sample","Abundance R3 128N Sample","Abundance R2 128N Sample"],"128C Sample":["Abundance R1 128C Sample","Abundance R3 128C Sample","Abundance R2 128C Sample"],
                        "129N Sample":["Abundance R1 129N Sample","Abundance R3 129N Sample","Abundance R2 129N Sample"],"129C Sample":["Abundance R1 129C Sample","Abundance R3 129C Sample","Abundance R2 129C Sample"],
                        "130N Sample":["Abundance R1 130N Sample","Abundance R3 130N Sample","Abundance R2 130N Sample"],"130C Sample":["Abundance R1 130C Sample","Abundance R3 130C Sample","Abundance R2 130C Sample"]}
                        ,
                "control":{"126 control":["Abundance R1 126 control","Abundance R2 126 control","Abundance R3 126 control"]}
                }

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
        volcano_plot_url,expressed_genes = plot_volcano_diff(df[columns],fc_col,p_val_col,metadata["log2_cut"],metadata["pv_cutoff"],title, analysis_id)
        volcano_plots.append([volcano_plot_url,expressed_genes])

    return volcano_plots

def get_heatmap_plot(file_url, index_col, columns_data, metadata, data):
    df = get_data_frame(file_url, index_col=index_col)
    both = True if metadata["ratio_or_log2"] == "log2_fc" else False
    fc_left = metadata["ratio_down"]
    fc_right = metadata["ratio_up"]
    lg2cut = metadata["log2_cut"]
    z_convert = data.z_score
    
    if data.method ==  "heirarchial":
        plot  = plot_heatmap(df,both,fc_left,fc_right,lg2cut , z_convert, data.analysis_id)

    else:
        plot  = plot_elbow_plot(df,index_col,data.analysis_id )

    return plot