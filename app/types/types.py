from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class DataForm(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    nomProjet: str
    nomPromoteur: str
    secteurActivite: Optional[str] = None
    empriseGeospatiale: Optional[Dict[str, Any]] = None
    aireInfluenceValeur: Optional[str] = ""
    aireInfluenceSecteur: Optional[str] = None
    switch_palettes: bool = Field(default=False, alias="switch-palettes")
    switch_sols_organiques: bool = Field(default=False, alias="switch-sols-organiques")
    solsOrganiquesRadio: Optional[str] = None
    switch_plans_eau: bool = Field(default=False, alias="switch-plans-eau")
    switch_canalisation: bool = Field(default=False, alias="switch-canalisation")
    switch_milieux_aquatiques: bool = Field(default=False, alias="switch-milieux-aquatiques")
    switch_sols_interregional: bool = Field(default=False, alias="switch-sols-interregional")
    switch_especes_non_indigenes: bool = Field(default=False, alias="switch-especes-non-indigenes")
    switch_produits_ligneux: bool = Field(default=False, alias="switch-produits-ligneux")
    switch_transport_maritime: bool = Field(default=False, alias="switch-transport-maritime")


class DataFormSubmission(BaseModel):
    model_config = ConfigDict(extra="allow")

    projectId: str
    form: DataForm
