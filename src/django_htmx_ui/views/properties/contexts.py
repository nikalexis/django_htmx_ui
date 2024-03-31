
from django_htmx_ui.defs import NotDefined
from django_htmx_ui.views.properties.base import BaseProperty


class BaseContextProperty(BaseProperty):
    pass


class ContextProperty(BaseContextProperty):

    _getter = None

    def __init__(self, getter, name=None) -> None:
        self._getter = getter
        super(BaseContextProperty, self).__init__(name, add_in_context=True, cache=False)

    def __view__(self):
        return self._getter(self.parent)


class ContextCachedProperty(ContextProperty):

    def __init__(self, getter, name=None) -> None:
        self._getter = getter
        super(BaseContextProperty, self).__init__(name, add_in_context=True, cache=True)

    def __view__(self):
        return self.parent.context.data.setdefault(
            self.name,
            self._getter(self.parent),
        )


class ContextStatic(BaseContextProperty):

    def __init__(self, value, name=None, add_in_context=True, cache=True) -> None:
        self.value = value
        super().__init__(name, add_in_context, cache)

    def __view__(self):
        return self.value


class ContextVariable(BaseContextProperty):

    _getter = None

    def __init__(self, default=NotDefined, converters=(), required=False, name=None, add_in_context=True, cache=True) -> None:
        self.default = default
        self.required = required
        self.converters = converters
        super().__init__(name, add_in_context, cache)

    def __call__(self, getter):
        self._getter = getter
        return self
    
    def apply_converters(self, value):
        for converter in reversed(self.converters):
            value = converter(value)
        return value

    def __view__(self):
        try:
            value = self.parent.context.data[self.name]
        except KeyError:
            if self._getter:
                value = self._getter(self.parent, self)

                value = self.apply_converters(value)

                if self.cache:
                    self.parent.context.data[self.name] = value

            else:
                value = self.apply_converters(self.default) if self.default is not NotDefined else self.default

        if self.required and value is NotDefined:
            raise ValueError(f"Required context variable '{self.name}' is not defined.")

        return value
    
    def _set(self, instance, value):
        instance.context.data[self.name] = self.apply_converters(value)


class ContextAncestor(BaseContextProperty):

    def __init__(self, foreign_name=None, required=True, limit=None, name=None, add_in_context=True) -> None:
        super().__init__(name, add_in_context, cache=False)
        self.required = required
        self.foreign_name = foreign_name
        self.limit = limit

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        if self.foreign_name is None:
            self.foreign_name = self.name

    def __view__(self):
        try:
            ancestor = self.parent
            counter = 1
            while self.limit is None or counter <= self.limit:
                ancestor = ancestor.parent
                try:
                    return ancestor.context[self.foreign_name]
                except KeyError:
                    if counter + 1 == self.limit:
                        raise
                counter += 1
        except (KeyError, AttributeError):
            if self.required:
                raise ValueError(f"Required context variable '{self.foreign_name}' not found in the context of {self.limit} ancestor(s) of '{instance}'.'{self.descriptor_name}'.")


class ContextParent(ContextAncestor):

    def __init__(self, foreign_name=None, required=True, name=None, add_in_context=True) -> None:
        limit = 1
        super().__init__(foreign_name, required, limit, name, add_in_context)
