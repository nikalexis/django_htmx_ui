import copy
from dataclasses import KW_ONLY, dataclass


class BasePropertyMetaclass(type):

    def __call__(self, *args, **kwargs):
        args, kwargs = self.__init_args__(self, *args, **kwargs)
        return type.__call__(self, *args, **kwargs)
    

@dataclass(eq=False)
class BaseProperty(metaclass=BasePropertyMetaclass):
    _: KW_ONLY
    name: str = None
    add_in_context: bool = True
    cache: bool = True

    view = None
    parent = None

    def __init_args__(self, *args, **kwargs):
        return args, kwargs

    def __set_name__(self, owner, name):
        self.owner = owner
        self.descriptor_name = name
        if self.name is None:
            self.name = name

    def copied_self(self, instance):
        view = getattr(instance, 'view', None)
        
        view_id = f'__property-view-{id(self)}'
        descriptor_id = f'__property-descriptor-{id(self)}'

        if view:
            instance_dict_key = view_id
        else:
            instance_dict_key = descriptor_id
        
        try:
            copied_self = instance.__dict__[instance_dict_key]
        except KeyError:
            copied_self = copy.copy(instance.__dict__.get(descriptor_id, self) if view else self)
            copied_self.view = view
            copied_self.parent = instance
            instance.__dict__[instance_dict_key] = copied_self
        return copied_self

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            copied_self = self.copied_self(instance)
            return copied_self._get(instance, owner)
    
    def _get(self, instance, owner):
        if self.view:
            return self.__view__()
        else:
            return self

    def __set__(self, instance, value):
        if not isinstance(value, type(self)):
            self.copied_self(instance)._set(instance, value)
    
    def _set(self, instance, value):
        raise AttributeError(f"Cannot set attribute, a _set function is not defined for '{self}'.")

    def __delete__(self, instance):
        self.copied_self(instance)._del(instance)

    def _del(self, instance):
        raise AttributeError(f"Cannot delete attribute, a _del function is not defined for '{self}'.")

    def __view__(self):
        return self
