import pandas as pd
import statistics
import re
from app.services.external_api.gprofiler_code import GProfiler

def get_gene_column(columns):

    for cols in columns:
        gene = re.search('.*[gG][eE][nN][eE].*',cols)
        if gene:
            return cols

        gene = re.search('.*[Aa][cC][cC][eE][sS][sS][iI][oO][nN].*',cols)
        if gene:
            return cols
    return None



def convert_acc_to_gene(accessions):
    gp = GProfiler(return_dataframe=True)
    
    gs = gp.convert(organism='hsapiens',
            query=accessions,
            target_namespace='ENTREZGENE_ACC')

    return gs["name"]


def Trypsin(sequence, missed_clevage, pep_min_len, pep_max_len):
    if 'K' in sequence or 'R' in sequence:
        get_dup_k = [i for i in range(len(sequence)) if sequence.startswith('K', i)]
        get_dup_r = [j for j in range(len(sequence)) if sequence.startswith('R', j)]
        merge_list = sorted(get_dup_k + get_dup_r)
        merge_list_fltrd = [i for i in merge_list if i+1 < len(sequence) and sequence[i + 1] !='P'] #look for KP or RP position
        merge_list_fltrd.append(len(sequence))
        initialize = 0
        for iter_lst in range(len(merge_list_fltrd) - int(missed_clevage)):
            peptide = (sequence[initialize: int(merge_list_fltrd[iter_lst + missed_clevage]) + 1])
            if len(peptide) >= int(pep_min_len) and len(peptide) <= int(pep_max_len):
                yield peptide
            initialize = merge_list_fltrd[iter_lst] + 1

def Lysc(sequence, missed_clevage, pep_min_len, pep_max_len):
    if 'K' in sequence:
        get_dup_k = [i for i in range(len(sequence)) if sequence.startswith('K', i)]
        merge_list_fltrd = get_dup_k
        merge_list_fltrd.append(len(sequence))
        initialize = 0
        for iter_lst in range(len(merge_list_fltrd) - int(missed_clevage)):
            peptide = (sequence[initialize: int(merge_list_fltrd[iter_lst + missed_clevage]) + 1])
            if len(peptide) >= int(pep_min_len) and len(peptide) <= int(pep_max_len):
                yield peptide
            initialize = merge_list_fltrd[iter_lst] + 1

def Chymotrypsin(sequence, missed_clevage, pep_min_len, pep_max_len):
    if 'F' in sequence or 'W' in sequence or 'Y' in sequence:
        get_dup_f = [i for i in range(len(sequence)) if sequence.startswith('F', i)]
        get_dup_w = [j for j in range(len(sequence)) if sequence.startswith('W', j)]
        get_dup_y = [j for j in range(len(sequence)) if sequence.startswith('Y', j)]
        merge_list = sorted(get_dup_f + get_dup_w + get_dup_y)
        merge_list_fltrd = [i for i in merge_list if i+1 < len(sequence) and sequence[i + 1] !='P'] #look for KP or RP position
        merge_list_fltrd.append(len(sequence))
        initialize = 0
        for iter_lst in range(len(merge_list_fltrd) - int(missed_clevage)):
            peptide = (sequence[initialize: int(merge_list_fltrd[iter_lst + missed_clevage]) + 1])
            if len(peptide) >= int(pep_min_len) and len(peptide) <= int(pep_max_len):
                yield peptide
            initialize = merge_list_fltrd[iter_lst] + 1




def theoritical(Gene_symbol, fasta , missed_clevage,pep_min_len,pep_max_len, enzyme):

    if enzyme == "trypsin":
        digest = Trypsin(str(fasta), missed_clevage, pep_min_len, pep_max_len)
        peptides = []
        for i in digest:
            peptides.append(i)
        return len(peptides)

def top3calc(x):
    if(len(x)) >= 3:
        intensity = sorted( [i for i in x], reverse=True )[:3]
        top3 = statistics.fmean(intensity)
        return top3
    else:
        top3 = statistics.fmean(x)
        return top3

def convert_fasta(fasta_file, fastadb):
    seq = []
    header = []
    block = []
    fasta_file = fasta_file.split('\n')
    for line in fasta_file:
        if line.startswith('>'):
            if block:
                seq.append(''.join(block))
                block = []
            header.append(line)
        else:
            block.append(line.strip())
    if block:
        seq.append(''.join(block))
    
    if fastadb == "ncbi":
        header = [i.split(' ', 1)[0].replace('>','').strip() for i in header]
    else:
        header = [i.split('|')[1].strip() for i in header]

    res = dict(zip(header, seq))

    df = pd.DataFrame(res.items(), columns=['protein_Accession', 'fasta'])

    return df 


def protien_identify(df,fastafile,prot_ident, missed_clevage,pep_min_len,pep_max_len, enzyme, fastsdb):

    fasta_df = convert_fasta(fastafile, fastsdb)
    if prot_ident == 'ibaq' or prot_ident == 'top3':
        gene_col =  get_gene_column(df.columns)
        df = df.groupby(gene_col).agg(pd.Series.tolist)
        df.reset_index(inplace = True)
        
        df_copy = df.merge(fasta_df, left_on = gene_col, right_on = "protein_Accession")

        if df_copy.empty:
            fasta_df["protein_Accession"] = convert_acc_to_gene(fasta_df['protein_Accession'].tolist())
            df = df.merge(fasta_df, left_on = gene_col, right_on = "protein_Accession")
        else:
            df = df.merge(fasta_df, left_on = gene_col, right_on = "protein_Accession")

        df['theoritical_peptide'] = df.apply(lambda x: theoritical(x[gene_col], x['fasta'], missed_clevage,pep_min_len,pep_max_len,enzyme), axis=1)
        df = df.loc[df['theoritical_peptide'] > 0]

        df = df[['Annotated Sequence',gene_col,'Intensity','theoritical_peptide']]

        if prot_ident == 'ibaq':
            df['Sum_of_intensity'] = df['Intensity'].apply(lambda x: sum(x))
            df['ibaq'] = (df['Sum_of_intensity']).div(df['theoritical_peptide'])
            prot_id = 'ibaq'
        else:
            prot_id = 'top3'
            df['top3'] = df['Intensity'].apply(top3calc)

        df = df[[gene_col,'theoritical_peptide','Sum_of_intensity',prot_id]]

    else:
        gene_col =  get_gene_column(df.columns)
        df = df.groupby(gene_col).agg(pd.Series.tolist)
        df.reset_index(inplace = True)

        df['#PSM'] = df['#PSM'].apply(lambda x: sum(x))


        df_copy = df.merge(fasta_df, left_on = gene_col, right_on = "protein_Accession")
        
        if df_copy.empty:
            fasta_df["protein_Accession"] = convert_acc_to_gene(fasta_df['protein_Accession'].tolist())
            df = df.merge(fasta_df, left_on = gene_col, right_on = "protein_Accession")
        else:
            df = df.merge(fasta_df, left_on = gene_col, right_on = "protein_Accession")
                    
        df['SAF'] = df.apply(lambda x: x['#PSM']/len(x['fasta']), axis = 1)

        sum_of_saf = df['SAF'].sum()

        df['NSAF'] = df['SAF'].apply(lambda x: x/ sum_of_saf)


        df.set_index(gene_col, inplace = True )

    return df