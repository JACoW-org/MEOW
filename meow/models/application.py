
from dataclasses import dataclass
from meow.models.infra.base import BaseModel
from meow.models.infra.fields import TextIndexField

@dataclass
class Credential(BaseModel):
    """ """

    label: str
    secret: str

    class SearchIndex:
        db = 'meow'
        name = 'credential'
        fields = [
            TextIndexField(
                field_code="$.label",
                field_name="label",
                is_sortable=True
            ),
            TextIndexField(
                field_code="$.secret",
                field_name="secret",
                is_sortable=True
            ),
        ]
