from abc import ABC

from redis.commands.search.field import Field, TextField, NumericField, TagField


class IndexField(ABC):
    """ """

    NUMERIC = "NUMERIC"
    TEXT = "TEXT"
    TAG = "TAG"

    def __init__(self, index_type: str, field_code: str, field_name: str, is_sortable: bool):
        self.index_type: str = index_type
        self.field_code: str = field_code
        self.field_name: str = field_name
        self.is_sortable: bool = is_sortable

    def get_redis_field(self) -> Field | None:
        pass


class NumericIndexField(IndexField):
    """ """

    def __init__(self, field_code: str, field_name: str, is_sortable: bool):
        super().__init__(IndexField.NUMERIC, field_code, field_name, is_sortable)

    def get_redis_field(self) -> NumericField:
        return NumericField(
            name=self.field_code,
            as_name=self.field_name,
            sortable=self.is_sortable,
        )


class TextIndexField(IndexField):
    """ """

    def __init__(self, field_code: str, field_name: str, is_sortable: bool):
        super().__init__(IndexField.TEXT, field_code, field_name, is_sortable)

    def get_redis_field(self) -> TextField:
        return TextField(
            name=self.field_code,
            as_name=self.field_name,
            sortable=self.is_sortable,
        )


class TagIndexField(IndexField):
    """ """

    def __init__(self, field_code: str, field_name: str, is_sortable: bool):
        super().__init__(IndexField.TAG, field_code, field_name, is_sortable)

    def get_redis_field(self) -> TagField:
        return TagField(
            name=self.field_code,
            as_name=self.field_name,
            sortable=self.is_sortable,
        )
