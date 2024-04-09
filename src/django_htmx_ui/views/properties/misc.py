from dataclasses import KW_ONLY, dataclass
from typing import Any
from django_htmx_ui.views.properties.base import BaseProperty


@dataclass(eq=False)
class Static(BaseProperty):
    value: Any
    _: KW_ONLY
    add_in_context: bool = False
    cache: bool = False

    def __view__(self):
        return self.value


@dataclass(eq=False)
class Variable(BaseProperty):
    value: Any
    _: KW_ONLY
    add_in_context: bool = False
    cache: bool = False

    def __view__(self):
        return self.value

    def _set(self, instance, value):
        self.value = value


@dataclass(eq=False)
class Alias(BaseProperty):
    alias: Any
    _: KW_ONLY
    cache: bool = False

    @property
    def alias_name(self):
        return self.alias if type(self.alias) is str else self.alias.descriptor_name

    def __view__(self):
        return getattr(self.parent, self.alias_name)

    def _set(self, instance, value):
        return setattr(instance, self.alias_name, value)
