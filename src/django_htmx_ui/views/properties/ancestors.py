
from django_htmx_ui.views.properties.base import ForeignProperty


class AscestorContext(ForeignProperty):

    def __init__(self, foreign_name=None, required=True, limit=None, name=None, add_in_context=True) -> None:
        super().__init__(name, add_in_context)
        self.required = required
        self.foreign_name = foreign_name
        self.limit = limit

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        if self.foreign_name is None:
            self.foreign_name = self.name

    def _get(self, instance, owner):
        try:
            ancestor = instance
            counter = 1
            while self.limit is None or counter <= self.limit:
                ancestor = ancestor.parent
                try:
                    return ancestor.context[self.foreign_name]
                except KeyError:
                    if counter + 1 == self.max_ancestors:
                        raise
                counter += 1
        except (KeyError, AttributeError):
            if self.required:
                raise ValueError(f"Required context variable '{self.foreign_name}' not found in the context of {self.limit} ancestor(s) of '{instance}'.'{self.descriptor_name}'.")


class ParentContext(AscestorContext):

    def __init__(self, foreign_name=None, required=True, name=None, add_in_context=True) -> None:
        limit = 1
        super().__init__(foreign_name, required, limit, name, add_in_context)
