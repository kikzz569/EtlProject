from pydantic import BaseModel, Field
from typing import Optional, Union

# --- CONTRATO DE DADOS ---

class AdPerformanceRecord(BaseModel):
    Organizador: int = Field(..., description="ID numérico do organizador.")
    Ano_Mes: str = Field(..., description="Período do registro (Ex: '2024 | Março').")
    Dia_da_Semana: str = Field(..., description="Nome do dia da semana (Ex: 'Sexta-Feira').")
    Tipo_Dia: str = Field(..., description="Classificação do dia (Ex: 'Dia útil').")
    Objetivo: str = Field(..., description="Objetivo da campanha (Ex: 'Leads').")
    Date: str = Field(..., description="Data do registro (Ex: '2024-03-01').")
    AdSet_name: str = Field(..., description="Nome do AdSet.")
    Amount_spent: float = Field(..., ge=0.0, description="Valor gasto (deve ser um número positivo ou zero).")
    Link_clicks: Optional[Union[int, float]] = Field(None, description="Número de cliques no link.")
    Impressions: Optional[Union[int, float]] = Field(None, description="Número de impressões.")
    Conversions: Optional[Union[int, float]] = Field(None, description="Número de conversões.")
    Segmentação: Optional[str] = Field(None, description="Tipo de segmentação de público.")
    Tipo_de_Anúncio: str = Field(..., description="Tipo do criativo (Ex: 'Estático', 'Video').")
    Fase: str = Field(..., description="Fase da campanha/lançamento.")

    class Config:
        extra = "ignore"