from django_htmx_ui.views.dominated.base import BaseDirective, BaseDominated


class KlassDirective(BaseDirective):
    prefix = ''
    
    def add(self, *args):
        return self.__call__(
            (self.current_attr() or '') + f' {" ".join(args)}'
        )

    def __iadd__(self, other):
        self.add(other)
        return self


class HtmlAttrsDominated(BaseDominated):
    default_directive = 'klass'

    klass = class_ = KlassDirective()
