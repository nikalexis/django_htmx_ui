

class BaseProperty:

    def __init__(self, name=None, add_in_context=True) -> None:
        self.name = name
        self.add_in_context = add_in_context

    def __set_name__(self, owner, name):
        self.owner = owner
        self.descriptor_name = name
        if self.name is None:
            self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return self._get(instance, owner)
    
    def _get(self, instance, owner):
        return self


class ForeignProperty(BaseProperty):
    pass
