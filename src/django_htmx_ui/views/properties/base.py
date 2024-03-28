import copy


class BaseProperty:

    view = None
    parent = None

    def __init__(self, name=None, add_in_context=True) -> None:
        self.name = name
        self.add_in_context = add_in_context

    def __set_name__(self, owner, name):
        self.owner = owner
        self.descriptor_name = name
        if self.name is None:
            self.name = name

    def copied_self(self, instance):
        view = getattr(instance, 'view', None)
        
        if view:
            instance_dict_key = f'__property__{self.descriptor_name}'
            try:
                copied_self = instance.__dict__[instance_dict_key]
            except KeyError:
                copied_self = copy.copy(self)
                copied_self.view = view
                copied_self.parent = instance
                instance.__dict__[instance_dict_key] = copied_self
            return copied_self
        else:
            self.parent = instance
            return self

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return self.copied_self(instance)._get(instance, owner)
    
    def _get(self, instance, owner):
        raise AttributeError(f"Cannot get attribute, a _get function is not defined for '{self}'.")

    def __set__(self, instance, value):
        self.copied_self(instance)._set(instance, value)
    
    def _set(self, instance, value):
        raise AttributeError(f"Cannot set attribute, a _set function is not defined for '{self}'.")

    def __delete__(self, instance):
        self.copied_self(instance)._del(instance)

    def _del(self, instance):
        raise AttributeError(f"Cannot delete attribute, a _del function is not defined for '{self}'.")


class ForeignProperty(BaseProperty):
    pass
