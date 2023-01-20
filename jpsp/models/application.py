
from dataclasses import dataclass
from jpsp.models.infra.base import BaseModel
from jpsp.models.infra.fields import TextIndexField

@dataclass
class Credential(BaseModel):
    """ """

    label: str
    secret: str

    class SearchIndex:
        db = 'jpsp'
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
