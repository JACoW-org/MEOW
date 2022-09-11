import pydantic as pd

from jpsp.models.infra.base import BaseModel
from jpsp.models.infra.fields import TextIndexField


class Settings(BaseModel):
    """ """

    id: str = '0'
    indico_http_url: str = pd.Field()
    indico_api_key: str = pd.Field()

    class SearchIndex:
        db = 'jpsp'
        name = 'settings'
        fields = [
            TextIndexField(
                field_code="$.indico_http_url",
                field_name="indico_http_url",
                is_sortable=True
            ),
            TextIndexField(
                field_code="$.indico_api_key",
                field_name="indico_api_key",
                is_sortable=False
            ),
        ]
