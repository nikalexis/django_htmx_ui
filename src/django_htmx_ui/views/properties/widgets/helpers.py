from django_htmx_ui.utils import ContextCachedProperty, ContextProperty, NotDefined
from django_htmx_ui.views.properties.base import BaseProperty
from django_htmx_ui.views.properties.widgets.base import BaseWidget


class ContextVariable(BaseProperty):

    _getter = None

    def __init__(self, default=NotDefined, required=False, name=None, add_in_context=True) -> None:
        self.default = default
        self.required = required
        super().__init__(name, add_in_context)

    def __call__(self, getter):
        self._getter = getter
        return self
    
    def _get(self, instance, owner):
        if self._getter:
            getter_value = self._getter(instance, self)

        value = instance.context.data.get(
            self.name,
            getter_value if self._getter and getter_value is not None else self.default
        )

        if self.required and value is NotDefined:
            raise ValueError(f"Required context variable '{self.name}' is not defined.")

        return value
    
    def _set(self, instance, value):
        instance.context.data[self.name] = value


class LocalProperties(BaseWidget):

    def __init__(self, *include_args, include=(), exclude=(), filter=bool, separator='', name=None, add_in_context=True) -> None:
        self.include = tuple(set(include_args) | set(include))
        self.exclude = exclude
        self.filter = filter
        self._separator = separator
        super().__init__(name, add_in_context)

    @ContextProperty
    def separator(self):
        return self._separator

    @ContextCachedProperty
    def contents(self):
        return [
            getattr(self.parent, descriptor_name)
            for descriptor_name, member in self.parent.get_properties(include=self.include, exclude=self.exclude, filter=self.filter)
        ]
