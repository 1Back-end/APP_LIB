from pydantic import BaseModel


class Msg(BaseModel):
    message: str  # Ce champ doit correspondre à la clé dans vos données retournées

class BoolStatus(BaseModel):
    status: bool


class DataDisplay(BaseModel):
    data: str
