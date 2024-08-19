from dominate.tags import attr, get_current


class BaseDominated:

    default_directive = None

    def __getitem__(self, key):
        if self.default_directive:
            return getattr(self, self.default_directive)[key]
        else:
            raise NotImplementedError(f"`{self.__class__.__name__}` does not support a default directive.")

    def __setitem__(self, key, value):
        if self.default_directive:
            return getattr(self, self.default_directive)[key](value)
        else:
            raise NotImplementedError(f"`{self.__class__.__name__}` does not support a default directive.")

    def __call__(self, value):
        if self.default_directive:
            return getattr(self, self.default_directive)(value)
        else:
            raise NotImplementedError(f"`{self.__class__.__name__}` does not support a default directive.")


class BaseDirective:
    
    prefix = None
    directive = None
    instance = None

    fix_endswith_underscore = True
    fix_hyphen = True

    def __set_name__(self, owner, name):
        fixed_name = name

        if self.fix_endswith_underscore and fixed_name.endswith('_'):
            fixed_name = fixed_name[0:-1]
        
        if self.fix_hyphen:
            fixed_name = fixed_name.replace('_', '-')

        self.directive = fixed_name

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __set__(self, instance, value):
        self.__call__(value)

    def full_directive(self):
        return f"{self.prefix}{self.directive}"

    def make_attr(self, value):
        return {
            self.full_directive(): value
        }

    def current_attr(self):
        return get_current().attributes.get(self.full_directive(), None)

    def __call__(self, value):
        attr(**self.make_attr(value))
        return self.instance


class BaseModifierMixin:

    separator = ":"
    modifier = None

    def __getitem__(self, key):
        self.modifier = key
        return self

    def __setitem__(self, key, value):
        self.modifier = key
        self.__call__(value)
        return self

    def make_attr(self, value):
        attr = super().make_attr(value)
        
        if self.modifier:
            attr = {
                f"{key}{self.separator}{self.modifier}": value
                for key, value in attr.items()
            }
        
        return attr
