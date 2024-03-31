from django_htmx_ui.views.properties.base import BaseProperty


class Static(BaseProperty):

    def __init__(self, value, name=None, add_in_context=False, cache=False) -> None:
        self.value = value
        super().__init__(name, add_in_context, cache)

    def __view__(self):
        return self.value


class Variable(BaseProperty):

    def __init__(self, value, name=None, add_in_context=False, cache=False) -> None:
        self.value = value
        super().__init__(name, add_in_context, cache)

    def __view__(self):
        return self.value

    def _set(self, instance, value):
        self.value = value


class Alias(BaseProperty):

    def __init__(self, alias, name=None, add_in_context=True, cache=True) -> None:
        self.alias = alias
        super().__init__(name, add_in_context, cache)

    @property
    def alias_name(self):
        return self.alias if type(self.alias) is str else self.alias.descriptor_name

    def __view__(self):
        return getattr(self.parent, self.alias_name)

    def _set(self, instance, value):
        return setattr(instance, self.alias_name, value)
