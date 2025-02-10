import matplotlib.pyplot as plt
import os
from sklearn.decomposition import PCA
import pandas as pd
import seaborn as sns

def generate_plot(data, file_name="plot.png"):
    plt.plot(data)
    path = f"app/static/{file_name}"
    plt.savefig(path)
    plt.close()
    return path

def get_pca_plot(df, title, columns, *args, **kwargs):

    df_pca = df.transpose()
    pca = PCA(n_components=2)
    components = pca.fit_transform(df_pca)
    pca_df = pd.DataFrame(components, columns = ['x','y'], index=df_pca.index)

    sample_mapping = {value: key for key, values in columns["test"].items() for value in values}
    sample_mapping.update({value: key for key, values in columns["control"].items() for value in values})

    pca_df["samples"] = pca_df.index.map(sample_mapping)

    percentagee=pca.explained_variance_ratio_
    per = [i * 100 for i in percentagee]
    per = ["{:.2f}".format(i) for i in per]

    # pca_df['samples'] = pd.Series(sample_list)
    pca_df.to_csv("pca_dfpca_dfpca_df.csv")

    sns.scatterplot(data=pca_df,x=pca_df['x'],y=pca_df['y'],hue=pca_df['samples'],s=80)

    plt.legend(fontsize=6)

    plt.xlabel('PC1 ('+str(per[0])+'%)')

    plt.ylabel('PC2 ('+str(per[1])+'%)')

    plt.title(title)

    plt.axvline(x=0, linestyle='--', color='#7d7d7d', linewidth=1)
    plt.axhline(y=0, linestyle='--', color='#7d7d7d', linewidth=1)

    plt.tight_layout()
    plt.savefig("plot.svg", format='svg')
    plt.close()


def get_box_plot(df):
    pass