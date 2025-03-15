import matplotlib.pyplot as plt
from  matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import zscore
import pandas as pd
import seaborn as sns
import numpy as np
from io import BytesIO
from app.services.aws_s3.save_to_s3 import save_to_s3 
from app.config import Settings
import os
import matplotlib
from itertools import  groupby

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

def get_box_plot(df, title, columns, analysis_id,normalized=False):
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




def result_bar_graph(df, analysis_id):
    df = df[[i for i in df.columns if i.startswith('expression_')]]

    updict = {}
    downdict = {}

    for column in df.columns:
        counts = df[column].value_counts()
        updict[column] = counts.get('up-regulated', 0)
        downdict[column] = counts.get('down-regulated', 0)

    upmax = max(updict.values(), default=0)
    downmax = max(downdict.values(), default=0)


    fig, ax = plt.subplots()
    plt.xticks(rotation=90, fontsize = 6)

    ax.bar(updict.keys(),updict.values(), color = 'red')
    ax.bar(downdict.keys(),[x*-1 for x in downdict.values()], color = 'green')

    ax.set_ylim(-downmax-5, upmax+5)

    upareg = list(updict.values())
    downreg = [x*-1 for x in downdict.values()]


    for i in range(len(upareg)):
        plt.text(i,upareg[i], upareg[i], ha = 'center')


    for j in range(len(downreg)):
        plt.text(j,downreg[j]-2, abs(downreg[j]), ha = 'center', va = 'bottom')

    ticks =  ax.get_yticks()
    ax.set_yticklabels([int(abs(tick)) for tick in ticks])
    plt.axhline(y= 0 , linestyle='-', color='#7d7d7d', linewidth=1)

    custom_lines = [Line2D([0], [0], color='red', lw=4),
                Line2D([0], [0], color='green', lw=4)]
    plt.ylabel("Number of proteins")
    ax.legend(custom_lines, ['Upregulated', 'Downregulated'])

    plt.tight_layout()

    get_plot_url = get_s3_url("result_bar_plot",analysis_id)
    return get_plot_url


     
def plot_volcano_diff(df,lfc, pv, lg2cut, pvalue_cut_off, genes, title, analysis_id):
    
    difex_ptn = dict()

    pv_thr = -(np.log10(pvalue_cut_off))
    lfc_thr = ( lg2cut,-lg2cut)

    color=("red", "grey", "green","black")

    df.loc[(df[lfc] >= lfc_thr[0]) & (df[pv] > pv_thr), 'color_add_axy'] = color[0]  # upregulated
    df.loc[(df[lfc] <= lfc_thr[1]) & (df[pv] > pv_thr), 'color_add_axy'] = color[2]  # downregulated
    df.loc[(df[lfc] > lfc_thr[1]) & (df[pv] > pv_thr) & (df[lfc] < lfc_thr[0]), 'color_add_axy'] = color[3]
    df['color_add_axy'].fillna(color[1], inplace=True)  # intermediate

    filt = df['color_add_axy'] == color[0]
    to_lable_up =  df.loc[filt]
    
    to_lable_up.sort_values([lfc, pv], ascending=[False, False], inplace=True)
    to_lable_up = to_lable_up.head(5)


    filt1 = df['color_add_axy'] == color[2]
    to_lable_down =  df.loc[filt1]
    

    to_lable_down.sort_values([lfc, pv], ascending=[True, False], inplace=True)
    to_lable_down = to_lable_down.head(5)


    difex_ptn['Upregulated'] = df.loc[df['color_add_axy'] == color[0], genes].tolist()
    difex_ptn['Downregulated'] = df.loc[df['color_add_axy'] == color[2], genes].tolist()

    df['color_add_axy'].replace('nan', np.nan, inplace=True)                       #edit
    df['color_add_axy'].fillna('grey', inplace=True)                               #edit

    plt.scatter(x = df[lfc], y = df[pv], s = 26 , c = df['color_add_axy'], alpha=0.8)

    pv_max = df[pv].max()+1
    pv_min = df[pv].min()
    lfc_max = df[lfc].max()
    
    if lfc_max > 4:
        lfc_max = lfc_max + 1
    else:
        lfc_max = 4
    
    try:
        plt.xlim(-lfc_max,lfc_max)
        plt.ylim(pv_min,pv_max)
    
    except:
        plt.xlim(-4,4)
                          
    plt.axvline(x=lfc_thr[0], linestyle='--', color='#7d7d7d', linewidth=1,)
    plt.axvline(x=lfc_thr[1], linestyle='--', color='#7d7d7d', linewidth=1)
    plt.axhline(y=pv_thr, linestyle='--', color='#7d7d7d', linewidth=1)
    plt.ylabel('-log10 (p-value)', fontsize = 8)
    
    plt.xlabel('log2 fold-change', fontsize = 8)

    plt.title(title, fontsize = 10)


    for index, row in to_lable_up.iterrows():
        x = row[lfc]
        y = row[pv]
        gene_label = row[genes]

        plt.annotate(gene_label , xy = (x,y), xycoords='data', size= 8,
                                # xytext = (random.randint(0, 20),random.randint(0, 20)),
                                xytext = (30,22),

                                textcoords='offset pixels', ha='center', va='bottom',
                                # bbox=dict(boxstyle='round,pad=0.1', fc='white', alpha=0.3),
                                arrowprops=dict(arrowstyle='->',
                                                color='grey'))


    for index, row in to_lable_down.iterrows():
        x = row[lfc]
        y = row[pv]
        gene_label = row[genes]

        plt.annotate(gene_label , xy = (x,y), xycoords='data', size= 8,
                                # xytext = (random.randint(0, 20),random.randint(0, 20)),
                                xytext = (-30, 22),

                                textcoords='offset pixels', ha='center', va='bottom',
                                # bbox=dict(boxstyle='round,pad=0.1', fc='white', alpha=0.3),
                                   arrowprops=dict(arrowstyle='->',
                                                color='grey'))
    

    get_plot_url = get_s3_url(title,analysis_id)
    
    return get_plot_url, difex_ptn


def scale_number(unscaled, to_min, to_max, from_min, from_max):
    return (to_max-to_min)*(unscaled-from_min)/(from_max-from_min)+to_min

def scale_list(l, to_min, to_max):
    return [scale_number(i, to_min, to_max, min(l), max(l)) for i in l]


def plot_heatmap(df,both,fc_left,fc_right,lg2cut , z_score, analysis_id):

    if z_score:
        df.fillna(0, inplace  = True)
        df= zscore(df)
        fc_left = -2
        fc_right = 2
        lg2cut = 2

    cols = list()
    for x in df.columns:
        x = x.replace('LOG2 foldchange of','')
        x = x.replace('FOLDCHANGE_','')
        x = x.strip()
        cols.append(x)

    max_val = df.melt().value.max()
    min_val = df.melt().value.min()

    if both:
        df.fillna(0, inplace = True)
        cbar_kws={"ticks":[min_val,-lg2cut,lg2cut,max_val] }
        v = scale_list([ min_val, (min_val+(-lg2cut))/2,-lg2cut,0, lg2cut ,(lg2cut+max_val)/2, max_val] , 0,1)
        

    else:
        df.fillna(1, inplace = True)
        cbar_kws={"ticks":[min_val, fc_left,fc_right, max_val] }
        v = scale_list([ min_val, (min_val+(fc_left))/2,fc_left,1, fc_right ,(fc_right+max_val)/2, max_val] , 0,1)
    
    v = sorted(v)

    c = ["darkgreen","green","palegreen","black","lightcoral","red","darkred"]
    l = list(zip(v,c))

    cmap = LinearSegmentedColormap.from_list('rg',l, N=256)

    df.columns = cols
    plt.switch_backend('AGG')
    sns.set(font_scale=0.5)
    try:
        ax = sns.clustermap(df,yticklabels=True,cmap=cmap,cbar_kws=cbar_kws, ) 
    except:
        ax = sns.clustermap(df,yticklabels=True,) 

               
    plt.tight_layout()


    get_plot_url = get_s3_url("Hierarchical cluster heatmap",analysis_id)
    
    return get_plot_url


def plot_elbow_plot(df, analysis_id):
    n_c = 15
    cols = list()
   
    if df.shape[0] <= 15:
         n_c = df.shape[0]
    wcss=[]
    for i in range(1,n_c):
        kmeans=KMeans(n_clusters=i,init="k-means++",random_state=42)
        kmeans.fit(df)
        wcss.append(kmeans.inertia_)
    clusters=np.arange(1, n_c) 

    plt.plot(clusters,wcss,marker ='x', markeredgecolor = 'blue')

    plt.tight_layout()

    get_plot_url = get_s3_url("Elbow plot",analysis_id)
    return get_plot_url

def get_auto_figsize(df_shape):
    if df_shape[0] < 50:
        return (df_shape[1], int(df_shape[0]/5)+2)
    else:          
        return (df_shape[1], int(df_shape[0]/10)+1)


def plot_kmeans_plot(df,n_clusters,fc_left,fc_right,lg2cut,both, analysis_id):
    auto_fig_size = get_auto_figsize(df.shape)
    
    max_val = df.melt().value.max()
    min_val = df.melt().value.min()

    if both:
        df.fillna(0, inplace = True)
        cbar_kws={"ticks":[min_val,-lg2cut,lg2cut,max_val] , "orientation": "horizontal"}
        v = scale_list([ min_val, (min_val+(-lg2cut))/2,-lg2cut,0, lg2cut ,(lg2cut+max_val)/2, max_val] , 0,1)

    else:
        df.fillna(1, inplace = True)
        cbar_kws={"ticks":[min_val, fc_left,fc_right, max_val], "orientation": "horizontal" }
        v = scale_list([ min_val, (min_val+(fc_left))/2,fc_left,1, fc_right ,(fc_right+max_val)/2, max_val] , 0,1)

    c = ["darkgreen","green","palegreen","black","lightcoral","red","darkred"]
    l = list(zip(v,c))

    cmap = LinearSegmentedColormap.from_list('rg',l, N=256)

    kmeans=KMeans(n_clusters=n_clusters,max_iter=1000,random_state=42)
    kmeans.fit(df)

    df['clusters']=kmeans.labels_

    df=df.sort_values('clusters')

    data=df.loc[:, df.columns != 'clusters']
    
    sns.set(font_scale=0.5)

    fig, axes = plt.subplots(figsize=(auto_fig_size))

    ax = sns.heatmap(data,yticklabels=True,cmap=cmap,cbar_kws=cbar_kws)

    clusters=list(df['clusters'])

    hline_list=[0]
    points=0
    for i in range(0,n_clusters):
        counts=clusters.count(i)
        points=points+counts
        hline_list.append(points)

    cmap= matplotlib.cm.viridis
    bounds = hline_list
    bounds=list(reversed(bounds))
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    ax1=fig.colorbar(
        matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm),
        ax=ax,  # Specify the axes to use for the colorbar
        ticks=bounds,
        spacing='proportional',
        orientation='vertical',
        #label='Discrete intervals, some other units',
        )

    get_plot_url = get_s3_url("K means plot",analysis_id)

    matplotlib.rc_file_defaults()

    kmap = get_s3_url("K means plot",analysis_id)
    return kmap

#all code below are for circular bargraph
#---------------------------------------------------------------------
def getgroupsize(golist):
    sep_go = [list(grp) for k, grp in groupby(golist)]
    counts = [len(x) for x in sep_go]
    return counts

def getfunctions(golist):
    sep_go = [list(grp) for k, grp in groupby(golist)]
    functions = [x[0] for x in sep_go]
    return functions
# The following is a helper function that given the angle at which the bar is positioned and the
# offset used in the barchart, determines the rotation and alignment of the labels.

def get_label_rotation(angle, offset):
    # Rotation must be specified in degrees :(
    rotation = np.rad2deg(angle + offset)
    if angle <= np.pi:
        alignment = "right"
        rotation = rotation + 180
    else:
        alignment = "left"
    return rotation, alignment


def add_labels(angles, values, labels, offset, ax):
    # This is the space between the end of the bar and the label
    padding = 4

    # Iterate over angles, values, and labels, to add all of them.
    for angle, value, label, in zip(angles, values, labels):
        angle = angle

        # Obtain text rotation and alignment
        rotation, alignment = get_label_rotation(angle, offset)

        # And finally add the text
        ax.text(
            x=angle,
            y=value + padding,
            s=label,
            ha=alignment,
            va="center",
            rotation=rotation,
            rotation_mode="anchor",
            size = 8
        )

def get_circbar_plot(df, analysis_id):
    # column nmaes =[name, value, group]
    plt.switch_backend('AGG')
    df["strvalue"] = df["value"].astype(str)
    df["strvalue"] = df["strvalue"].apply(lambda x: '('+x+')')
    df["name"]  = df[['strvalue', 'name']].agg('-'.join, axis=1)


    OFFSET = np.pi / 2

    VALUES = np.log2(df["value"].values)
    LABELS = df["name"].values
    GROUP = df["group"].values

    PAD = 3
    ANGLES_N = len(VALUES) + PAD * len(np.unique(GROUP))
    ANGLES = np.linspace(0, 2 * np.pi, num=ANGLES_N, endpoint=False)
    WIDTH = (2 * np.pi) / len(ANGLES)

    offset = 0
    IDXS = []

    GROUPS_SIZE = getgroupsize(df['group'].tolist())

    for size in GROUPS_SIZE:
        IDXS += list(range(offset + PAD, offset + size + PAD))
        offset += size + PAD



    fig, ax = plt.subplots(figsize=(20, 10), subplot_kw={"projection": "polar"})
    # fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

    ax.set_ylim(-100, max(VALUES))
    ax.set_theta_offset(OFFSET)
    ax.set_frame_on(False)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

    GROUPS_SIZE = getgroupsize(df['group'].tolist())

    COLORS = [f"C{i}" for i, size in enumerate(GROUPS_SIZE) for _ in range(size)]

    ax.bar(
        ANGLES[IDXS], VALUES, width=WIDTH, color=COLORS,
        edgecolor="white", linewidth=2
    )

    add_labels(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax)

    # Extra customization below here --------------------

    # This iterates over the sizes of the groups adding reference
    # lines and annotations.
# Set the coordinates limits


    offset = 0
    funcs = getfunctions(df['group'].tolist())

    for group, size in zip(funcs, GROUPS_SIZE):
        # Add line below bars
        x1 = np.linspace(ANGLES[offset + PAD], ANGLES[offset + size + PAD - 1], num=50)
        ax.plot(x1, [-5] * 50, color="#333333")

        # Add text to indicate group
        ax.text(
            np.mean(x1), -20, group, color="#333333", fontsize=8,
            fontweight="bold", ha="center", va="center"
        )

        # Add reference lines at 20, 40, 60, and 80
        x2 = np.linspace(ANGLES[offset], ANGLES[offset + PAD - 1], num=50)
        ax.plot(x2, [20] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [40] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [60] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [80] * 50, color="#bebebe", lw=0.8)

        offset += size + PAD

    plt.tight_layout()

    get_plot_url = get_s3_url("Circular bar plot",analysis_id)
    return get_plot_url

#------------------------------------------------ cirbar done -----------------------------------------------------
