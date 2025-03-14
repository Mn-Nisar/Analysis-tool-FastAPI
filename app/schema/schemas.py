from pydantic import BaseModel 
from typing import Optional, Dict, Any, Literal

class MetadataRequest(BaseModel):
    noOfTest: int
    noOfControl: int
    noOfBatches: Optional[int] = None
    expType: Literal ["techrep","biorep"]
    fileUrl: str = "https://proteoark-example.s3.us-west-1.amazonaws.com/TECHNICAL.csv" 

class MetadataDirect(BaseModel):
    noOfTest: int
    noOfControl: int
    fileUrl: str = "https://proteoark-example.s3.us-west-1.amazonaws.com/NORMALIZED_TECHNICAL.csv" 

class Normalize(BaseModel):
    analysis_id: int
    norm_method: Literal["median","sum","quantile","irs","z_score","tmm"]
    exp_type: Literal["techrep","biorep"]
    imputation_value: float = 0
    imputation_method: Literal["value","one_fifth","miss_forest"]
    remove_contamination: bool = False
    accession_column: Optional[str] = None
    gene_column: Optional[str] = None
    convert_protein_to_gene: bool = False
    column_data: Dict[str, Any] = { }
    tmm_propotion: int = 10

class BatchCorrection(BaseModel):
    analysis_id: int
    bc_method: Literal["combat","limma"]
    batch_data: Dict[str, Any] = {}

class Differential(BaseModel):
    analysis_id: int

    pv_method: Literal ["weltch","ttest","one_anova",
                             "two_anova","limma"]
    pv_cutoff:float = 0.05
    adj_pv_method:Literal["bonferroni","benjam_hoch","benjam_hekuti"]
    ratio_log2:Literal["log2_fc","ratio"]
    ratio_cut_up: float = 1.5
    ratio_cut_down: float = 0.67
    log2_fc_cutoff: float = 0.5
    choose_control: str
    column_data: Dict[str, Any] = {}

    direct_differntial: bool = False
    gene_column: Optional[str] = None


class HeatMap(BaseModel):
    analysis_id: int
    method: Literal["heirarchial","k_mean"]
    z_score: bool = False

class Kmean(BaseModel):
    analysis_id: int
    k_value: int

class GeneOntology(BaseModel):
    analysis_id: int
    p_value: float = 0.05
    species: str = "hsapiens"


class PlotData(BaseModel):
    plot_id: int
    viz_type: Literal["cicrular","volcano","pca","rain","ma-plot","heatmap-heirarch","heatmap-kmean","upset",
                    "density","violion","box","bubble","histogram","s-curve","venn"]
    fileUrl: str = None
    example: bool = False

class VizualizeSchema(BaseModel):
    viz_id: int
    meta_data: Dict[str, Any] = { }
