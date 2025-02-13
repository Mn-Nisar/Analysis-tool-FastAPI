import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import pandas as pd
import seaborn as sns
import numpy as np
from io import BytesIO
from app.services.aws_s3.save_to_s3 import save_to_s3 
from app.config import Settings
import os

settings = Settings()
PRODUCTION = settings.is_production

def get_s3_url(plot_titel, analysis_id):
    
    buffer = BytesIO()
    
    plt.savefig(buffer, format = 'svg')
    
    buffer.seek(0)
    
    file_name = f"plots/{str(analysis_id)}_{plot_titel}.svg" 
    
    if PRODUCTION:
        file_url = save_to_s3(buffer, file_name)
    else:
        local_path = os.path.join(settings.local_plots_dir(), file_name)
        with open(local_path, "wb") as f:
            f.write(buffer.getvalue())
        file_url = f"http://localhost:8000/plots/{file_name}"

    buffer.close()
    plt.close()

    return file_url


my_colours  = ['cyan','gold','hotpink','peru','red','navy','purple','grey','tan','steelblue',
    'peachpuff','palegreen','orchid','darkred','black','orange','teal','firebrick','indigo','orchid','darkred','black',
    'orange','purple','grey','tan','brown','forestgreen',
    'cyan','gold','hotpink','peru','red','navy','purple','grey','tan','steelblue',
    'cyan','gold','hotpink','peru','red','navy','purple','grey','tan','steelblue',
    'peachpuff','palegreen','orchid','darkred','black','orange','teal','firebrick','indigo','orchid','darkred','black',
    'orange','purple','grey','tan','brown','forestgreen',
    'cyan','gold','hotpink','peru','red','navy','purple','grey','tan','steelblue','hotpink','peru','red','navy']


def get_pca_plot(df, title, columns, analysis_id, normalized=False, *args, **kwargs):

    df_pca = df.transpose()
    pca = PCA(n_components=2)
    components = pca.fit_transform(df_pca)
    pca_df = pd.DataFrame(components, columns = ['x','y'], index=df_pca.index)
    
    if normalized:
        normalized_columns = {
        category: {
            sample: [f"normalized_{value}" for value in values]
            for sample, values in samples.items()
        }
        for category, samples in columns.items()
             }
        sample_mapping = {value: key for key, values in normalized_columns["test"].items() for value in values}
        sample_mapping.update({value: key for key, values in normalized_columns["control"].items() for value in values})
    else:
        sample_mapping = {value: key for key, values in columns["test"].items() for value in values}
        sample_mapping.update({value: key for key, values in columns["control"].items() for value in values})

    pca_df["samples"] = pca_df.index.map(sample_mapping)

    percentagee=pca.explained_variance_ratio_
    per = [i * 100 for i in percentagee]
    per = ["{:.2f}".format(i) for i in per]

    sns.scatterplot(data=pca_df,x=pca_df['x'],y=pca_df['y'],hue=pca_df['samples'],s=80)

    plt.legend(fontsize=6)

    plt.xlabel('PC1 ('+str(per[0])+'%)')

    plt.ylabel('PC2 ('+str(per[1])+'%)')

    plt.title(title)

    plt.axvline(x=0, linestyle='--', color='#7d7d7d', linewidth=1)
    plt.axhline(y=0, linestyle='--', color='#7d7d7d', linewidth=1)

    plt.tight_layout()

    get_plot_url = get_s3_url(title,analysis_id)

    return get_plot_url

def get_box_plot(df,isbio, title, columns, analysis_id,normalized=False):
    df = np.log2(df)
    flierprops = dict(marker='o', markerfacecolor='white', markersize=3,
                  linestyle='none', markeredgecolor='black')

    ax = sns.boxplot(data = df, notch=True, flierprops = flierprops, linewidth = 0.5, width = 0.5)

    colourdict = dict()


    sample_groups = list(columns["test"].values())
    control_groups = list(columns["control"].values())
    
    groups = sample_groups + control_groups

    if normalized:
        groups = [[f"normalized_{item}" for item in sublist] for sublist in groups]

    color_mapping = {sample: my_colours[i % len(my_colours)] for i, group in enumerate(groups) for sample in group}


    for patch, colours in zip(ax.patches,color_mapping):
        patch.set_facecolor(color_mapping[colours])

    plt.xticks(fontsize=6, rotation=90)
    plt.ylabel('log2 of Abundances')
    plt.title(title)
    plt.tight_layout()

    get_plot_url = get_s3_url(title,analysis_id)
    return get_plot_url

