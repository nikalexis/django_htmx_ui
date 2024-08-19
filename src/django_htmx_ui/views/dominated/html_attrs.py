from django_htmx_ui.views.dominated.base import BaseDirective, BaseDominated


class KlassDirective(BaseDirective):
    prefix = ''

    def get_classes(self):
        return [
            c
            for c in (self.current_attr() or '').split(' ')
            if c != ''
        ]
    
    def join_classes(self, *classes, include_current=True):
        return " ".join(
                self.get_classes() + list(classes) if include_current else list(classes)
            )

    def add(self, *classes):
        return self.__call__(
            self.join_classes(*classes)
        )

    def __add__(self, other):
        if type(other) is str:
            return self.join_classes(other)
        else:
            return self.join_classes(*other)

    def remove_classes(self, *classes):
        return self.join_classes(*[c for c in self.get_classes() if c not in classes], include_current=False)

    def remove(self, *classes):
        return self.__call__(
            self.remove_classes(*classes)
        )

    def __sub__(self, other):
        if type(other) is str:
            return self.remove_classes(other)
        else:
            return self.remove_classes(*other)


class HtmlAttrsDominated(BaseDominated):
    default_directive = 'klass'

    klass = class_ = KlassDirective()
