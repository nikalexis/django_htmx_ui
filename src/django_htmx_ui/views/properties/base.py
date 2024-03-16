
from django_htmx_ui.views.base import ExtendedContextMixin, ExtendedTemplateResponseMixin


class BaseProperty:

    def __init__(self, name=None, add_in_context=True) -> None:
        self.name = name
        self.add_in_context = add_in_context

    def __set_name__(self, owner, name):
        self.descriptor_name = name
        if not self.name:
            self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return self._get(instance, owner)
    
    def _get(self, instance, owner):
        return self

    @property
    def slug_property(self):
        return f'{self.descriptor_name}'

    @property
    def slug_global(self):
        return super().slug_global + '_' + self.slug_property


class ForeignProperty(BaseProperty):

    class Foreigner:

        def __init__(self, instance, descriptor, context) -> None:
            self.instance = instance
            self.descriptor = descriptor
            self.context = context

    foreigner = None

    def setup_foreigner(self, instance, descriptor, context):
        self.foreigner = ForeignProperty.Foreigner(instance, descriptor, context)


class BaseWidget(ExtendedTemplateResponseMixin, ExtendedContextMixin, ForeignProperty):
    
    def get_template_names(self):
        splits = self.foreigner.instance.template_name.rsplit('.', 1)
        return [f'{splits[0]}_{self.name}.{splits[1]}'] + super().get_template_names()
