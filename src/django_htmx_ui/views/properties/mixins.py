import inspect


class GetterMixin:

    getter = None

    def __call__(self, getter):
        if self.parent and self.name in self.parent.context.data:
            raise ValueError('Cannot set a getter function after setting up a value for the ContextVariable property.')
        self.getter = getter
        return self
    
    @property
    def getter_ancestor(self):
        candidates = [ancestor for ancestor in self.ancestors if type(ancestor) is inspect._findclass(self.getter)]
        if not candidates:
            raise ValueError(f"Getter function '{self.getter}' cannot be found in ancestors list for object '{self}'.")
        elif len(candidates) > 1:
            raise ValueError(f"Getter function '{self.getter}' found in {len(candidates)} ancestors for object '{self}'.")
        return candidates[0]
    
    @property
    def getter_value(self):
        return self.getter(self.getter_ancestor)
