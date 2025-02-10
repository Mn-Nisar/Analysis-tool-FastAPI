from pydantic import BaseModel 
from typing import Optional, Dict, Any, Literal

class MetadataRequest(BaseModel):
    noOfTest: int
    noOfControl: int
    noOfBatches: Optional[int] = None
    expType: Literal ["techrep","biorep"]
    fileUrl: str

class Normalize(BaseModel):
    analysis_id: int
    norm_method: Literal["median","sum","quantile","irs","z_score","tmm"]
    exp_type: Literal["biological", "technical"]
    imputation_value: float = 0
    imputation_method: Literal["value","one_fifth","miss_forest"]
    remove_contamination: bool = False
    accession_column: Optional[str] = None
    gene_column: Optional[str] = None
    convert_protein_to_gene: bool = False
    column_data: Dict[str, Any] = { "test":{"127N Sample":["Abundance R1 127N Sample","Abundance R3 127N Sample","Abundance R2 127N Sample"],"127C Sample":["Abundance R1 127C Sample","Abundance R3 127C Sample","Abundance R2 127C Sample"],
                        "128N Sample":["Abundance R1 128N Sample","Abundance R3 128N Sample","Abundance R2 128N Sample"],"128C Sample":["Abundance R1 128C Sample","Abundance R3 128C Sample","Abundance R2 128C Sample"],
                        "129N Sample":["Abundance R1 129N Sample","Abundance R3 129N Sample","Abundance R2 129N Sample"],"129C Sample":["Abundance R1 129C Sample","Abundance R3 129C Sample","Abundance R2 129C Sample"],
                        "130N Sample":["Abundance R1 130N Sample","Abundance R3 130N Sample","Abundance R2 130N Sample"],"130C Sample":["Abundance R1 130C Sample","Abundance R3 130C Sample","Abundance R2 130C Sample"]}
                        ,
                "control":{"126 control":["Abundance R1 126 control","Abundance R2 126 control","Abundance R3 126 control"]}
                }
    tmm_propotion: int = 10