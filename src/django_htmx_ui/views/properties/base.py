import copy
from dataclasses import KW_ONLY, dataclass


properties_dataclass = dataclass(eq=False)


class BasePropertyMetaclass(type):

    def __call__(self, *args, **kwargs):
        args, kwargs = self.__init_args__(self, *args, **kwargs)

        self.magic_kwargs = {key: value for key, value in kwargs.items() if '__' in key}
        if self.magic_kwargs:
            kwargs = {key: value for key, value in kwargs.items() if key not in self.magic_kwargs}
        
        new_self = type.__call__(self, *args, **kwargs)

        for key, value in self.magic_kwargs.items():
            *attrs, last = key.split('__')
            p = new_self
            for attr in attrs:
                p = getattr(p, attr)
            setattr(p, last, value)

        return new_self
    

@properties_dataclass
class BaseProperty(metaclass=BasePropertyMetaclass):
    _: KW_ONLY
    name: str = None
    add_in_context: bool = True
    cache: bool = True

    magic_kwargs = None

    view = None
    parent = None
    copy_of = None

    @property
    def ancestors(self):
        ancestor = self.parent
        while ancestor:
            yield ancestor
            ancestor = getattr(ancestor, 'parent', None)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        properties_dataclass(cls)

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
            copy_of = instance.__dict__.get(descriptor_id, self) if view else self
            copied_self = copy.copy(copy_of)
            copied_self.view = view
            copied_self.parent = instance
            copied_self.copy_of = copy_of
            instance.__dict__[instance_dict_key] = copied_self
        return copied_self

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            copied_self = self.copied_self(instance)
            return copied_self._get(instance, owner)
    
    def _get(self, instance, owner):
        return self

    def __set__(self, instance, value):
        if value is not self:
            self.copied_self(instance)._set(instance, value)
    
    def _set(self, instance, value):
        raise AttributeError(f"Cannot set attribute, a _set function is not defined for '{self}'.")

    def __delete__(self, instance):
        self.copied_self(instance)._del(instance)

    def _del(self, instance):
        raise AttributeError(f"Cannot delete attribute, a _del function is not defined for '{self}'.")

    def __context__(self):
        return self

    def __str__(self):
        raise NotImplementedError()


@properties_dataclass
class BasePropertyMixin(metaclass=BasePropertyMetaclass):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        properties_dataclass(cls)


class BaseValueProperty(BaseProperty):

    def _get(self, instance, owner):
        home = list(self.ancestors)[-1]
        if isinstance(home, BaseProperty) and not home.copy_of:
            return self
        else:
            return self.__context__()

    def __context__(self):
        raise NotImplementedError()

    def __str__(self):
        return str(self.__context__())
