import pandas as pd 

from app.services.external_api.gprofiler_code import GProfiler


def convert_acc_to_gene(accessions, organism='hsapiens'):

    accessions = [acc.split(';')[0] if ";" in acc else acc for acc in accessions]
    
    gs_convert_success = True
    con_df = pd.DataFrame()
    try:
        gp = GProfiler(return_dataframe=True)
        
        gs = gp.convert(organism=organism,
                query=accessions,
                target_namespace='ENTREZGENE_ACC')

        con_df = gs[['incoming','name']]
        con_df.rename(columns = {'incoming':'Accesion_gf' , 'name': '_GENE_SYMBOL_'}, inplace = True)
        
        none_df = con_df.loc[ con_df['_GENE_SYMBOL_'] == 'None']

        for index, row in none_df.iterrows():
            if row['_GENE_SYMBOL_'] == 'None':
                con_df.loc[index, '_GENE_SYMBOL_'] =  con_df.loc[index, 'Accesion_gf']

    except:
        gs_convert_success = False

    return con_df , gs_convert_success


def get_gene_ontology(genes, p_value, species):
    gp = GProfiler(return_dataframe=True)
    go = gp.profile(organism=species,
                    query=genes,
                    no_evidences=False,
                    user_threshold=p_value,
                    )
    
    go = go[['native','name','p_value','intersection_size','source']]
    go.sort_values(by=['source'], inplace=True)
    go.rename(columns = {"intersection_size": "value","source":"group"},inplace = True)

    return go