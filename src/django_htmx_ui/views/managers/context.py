import copy
from django_htmx_ui.utils import ContextCachedProperty, ContextProperty
from django_htmx_ui.views.properties.base import BaseProperty
from collections.abc import Mapping, MutableMapping


class Context:

    def __init__(self, instance, owner, name, include=(), exclude=(), context=None) -> None:
        self.instance = instance
        self.owner = owner
        self.name = name
        self._include = tuple(include)
        self._exclude = tuple(exclude)

        self._descriptors = {
            getattr(member, 'name', descriptor_name): descriptor_name
            for descriptor_name, member in self.instance.get_properties(self._include, self._exclude, self.filter)
        }

        self.data = context or {}

    @property
    def parent(self):
        return self.instance.parent.context

    @staticmethod
    def filter(descriptor):
        return getattr(descriptor, 'add_in_context', True)

    def read_from_instance(self, descriptor_name):
        return getattr(self.instance, descriptor_name)

    def include(self, *args):
        include = set(self._include) | set(args)
        context = self.data.copy()
        for descriptor_name, member in self.instance.get_properties(include, self._exclude, self.filter):
            key = getattr(member, 'name', descriptor_name)
            if key in self.data and key not in self._descriptors:
                del context[key]
        return Context(self.instance, self.owner, self.name, include=include, exclude=self._exclude, context=context)

    def exclude(self, *args):
        exclude=set(self._exclude) | set(args)
        context = self.data.copy()
        for descriptor_name, member in self.instance.get_properties(self._include, exclude, self.filter):
            key = getattr(member, 'name', descriptor_name)
            if key in self.data and key in self._descriptors:
                del context[key]
        return Context(self.instance, self.owner, self.name, include=self._include, exclude=exclude, context=context)

    def __delitem__(self, key):
        del self.data[key]

    def __getitem__(self, key):
        if key not in self.keys():
            raise KeyError(f"'{key}' not found in context properties.")

        if key not in self.data:
            self.data[key] = self.read_from_instance(self._descriptors[key])

        return self.data[key]
    
    def __setitem__(self, key, value):
        if key in self._descriptors:
            raise KeyError(f"'{key}' cannot be set, it is used by the descriptor property named '{self._descriptors[key]}' in {self.instance}.")
        self.data[key] = value

    def __iter__(self):
        for key in self.keys():
            yield key, self.__getitem__(key)

    def __len__(self) -> int:
        return len(self.keys)

    def keys(self):
        return self._descriptors.keys() | self.data.keys()
    
    def items(self):
        for key in self.keys():
            yield key, self.__getitem__(key)

    def setdefault(self, key, default):
        if key in self._descriptors:
            raise KeyError(f"'{key}' cannot be set, it is used by the descriptor property named '{self._descriptors[key]}' in {self.instance}.")
        self.data.setdefault(key, default)


class ContextManager:

    PROPERTY_TYPES = (ContextProperty, ContextCachedProperty, BaseProperty)
    CONTEXT_TYPE = Context

    def __init__(self, name=None) -> None:
        self.name = name

    def __set_name__(self, owner, name):
        self.descriptor_name = name
        if not self.name:
            self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            instance_dict_key = f'__context_manager__{self.descriptor_name}'
            try:
                context = instance.__dict__[instance_dict_key]
            except KeyError:
                context = instance.__dict__[instance_dict_key] = self.CONTEXT_TYPE(
                    instance,
                    owner,
                    self.name,
                    self.PROPERTY_TYPES,
                )

            if context.instance is not instance:
                context = instance.__dict__[instance_dict_key] = self.CONTEXT_TYPE(
                    instance,
                    owner,
                    self.name,
                    context._include,
                    context._exclude,
                    copy.copy(context.data),
                )

            return context
