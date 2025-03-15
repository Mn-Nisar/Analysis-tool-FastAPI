import datetime

from app.services.data_processing.data_preprocess import get_data_frame
from app.services.visualization.utils import format_circ_df
from  app.services.visualization.visualization import get_circbar_plot


def plot_pipeline(file_url, plot_type,meta_data, viz_id):

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = f"{timestamp}_{viz_id}"

    df = get_data_frame(file_url)
    
    # plot["cicrular","volcano","pca","rain","ma-plot","heatmap-heirarch","heatmap-kmean","upset",
    #                 "density","violion","box","bubble","histogram","s-curve","venn"]
    
    if plot_type ==  "cicrular":
        df = format_circ_df(df,meta_data)
        plot = get_circbar_plot(df,unique_id)
    
    # elif plot_type == "volcano":
    #     plot = volcano_plot(df,meta_data)
    # elif plot_type == "pca":
    #     plot = pca_plot(df,meta_data)
    # elif plot_type == "rain":
    #     plot = rain_plot(df,meta_data)
    # elif plot_type == "ma-plot":
    #     plot = ma_plot(df,meta_data)
    # elif plot_type == "heatmap-heirarch":
    #     plot = heatmap_heirarch(df,meta_data)
    # elif plot_type == "heatmap-kmean":
    #     plot = heatmap_kmean(df,meta_data)
    # elif plot_type == "upset":
    #     plot = upset_plot(df,meta_data)
    # elif plot_type == "density":
    #     plot = density_plot(df,meta_data)
    # elif plot_type == "violion":
    #     plot = violion_plot(df,meta_data)
    # elif plot_type == "box":
    #     plot = box_plot(df,meta_data)
    # elif plot_type == "bubble":
    #     plot = bubble_plot(df,meta_data)
    # elif plot_type == "histogram":
    #     plot = histogram_plot(df,meta_data)
    # elif plot_type == "s-curve":
    #     plot = s_curve_plot(df,meta_data)
    # elif plot_type == "venn":
    #     plot = venn_plot(df,meta_data)
    else:
        plot = "Invalid plot type"
    
    return plot