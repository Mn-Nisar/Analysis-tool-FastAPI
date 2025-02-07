


def data_normalization(df,columns,method):
    if (method == 'Median'):
        
        mediun_list = {}

        for controls in control_columns:
            for replicates in controls:
                mediun_list[replicates] = df[replicates].median()
    
        for samples in sample_columns:
            for samp_replicates in samples:
                mediun_list[samp_replicates] = df[samp_replicates].median()
    
        minn = min(mediun_list.values())
        #deviding each value with multiplication factor
        multiplication_fact_list = {}
        for key,value in mediun_list.items():
            multiplication_fact_list[key] = (minn/value)
        
        cna = []

        for controls in control_columns:
            each_control = []
            for replicates in controls:
                df['NORM_'+replicates] = df[replicates] * multiplication_fact_list[replicates]
                each_control.append('NORM_'+replicates)
            cna.append(each_control)


        sna = []
        for samples in sample_columns:
            each_sample = []
            for samp_replicates in samples:
                df['NORM_'+samp_replicates] = df[samp_replicates] * multiplication_fact_list[samp_replicates]
                each_sample.append('NORM_'+samp_replicates)
            sna.append(each_sample)
            
    df_PCA_before = df[exp_samp + exp_cont]
    df_PCA_after = df[exp_sna + exp_cna]
    return df,df_PCA_before, df_PCA_after ,cna, sna , contaminants_df