
from django_htmx_ui.views.properties.base import ForeignProperty


class ForeignContext(ForeignProperty):

    def __init__(self, foreign_name=None, required=True, name=None, add_in_context=True) -> None:
        super().__init__(name, add_in_context)
        self.required = required
        self.foreign_name = foreign_name

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        if self.foreign_name is None:
            self.foreign_name = self.name

    def _get(self, instance, owner):
        try:
            return instance.context.parent[self.foreign_name]
        except KeyError:
            if self.required:
                raise ValueError(f"Required context variable '{self.foreign_name}' not found in the context of foreign instance '{instance}'.")
