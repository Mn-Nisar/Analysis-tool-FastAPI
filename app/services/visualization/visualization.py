import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import pandas as pd
import seaborn as sns
import numpy as np
from io import BytesIO
import base64


def generate_plot(data, file_name="plot.png"):
    plt.plot(data)
    path = f"app/static/{file_name}"
    plt.savefig(path)
    plt.close()
    return path


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format = 'svg')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    plt.close()
    return graph

my_colours  = ['cyan','gold','hotpink','peru','red','navy','purple','grey','tan','steelblue',
    'peachpuff','palegreen','orchid','darkred','black','orange','teal','firebrick','indigo','orchid','darkred','black',
    'orange','purple','grey','tan','brown','forestgreen',
    'cyan','gold','hotpink','peru','red','navy','purple','grey','tan','steelblue',
    'cyan','gold','hotpink','peru','red','navy','purple','grey','tan','steelblue',
    'peachpuff','palegreen','orchid','darkred','black','orange','teal','firebrick','indigo','orchid','darkred','black',
    'orange','purple','grey','tan','brown','forestgreen',
    'cyan','gold','hotpink','peru','red','navy','purple','grey','tan','steelblue','hotpink','peru','red','navy']


def get_pca_plot(df, title, columns, normalized=False, *args, **kwargs):

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

    pca_plot = get_graph()
    
    return pca_plot

def get_box_plot(df,isbio, title, columns, normalized=False):
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

    boxplot = get_graph()
    return boxplot

