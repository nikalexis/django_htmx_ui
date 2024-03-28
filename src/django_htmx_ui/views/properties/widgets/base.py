from markupsafe import Markup
from django_htmx_ui.views.base import ExtendedContextMixin, ExtendedTemplateResponseMixin
from django_htmx_ui.views.properties.base import ForeignProperty


class BaseWidget(ExtendedTemplateResponseMixin, ExtendedContextMixin, ForeignProperty):

    def __new__(cls, *args, **kwargs):
        cls._template_names_cro = [
            c.template_name for c in cls.mro() if issubclass(c, BaseWidget)
        ]
        return super().__new__(cls)

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        splits = owner.template_name.rsplit('.', 1)
        self._template_names_cro = [f'{splits[0]}_{self.name}.{splits[1]}'] + self._template_names_cro

    def get_template_names(self):
        return self._template_names_cro

    def rendered_response(self):
        response = self.render_to_response(
            self.get_context_data()
        )
        response.render()
        return Markup(response)

    def _get(self, instance, owner):
        return self.rendered_response()

    @property
    def slug_property(self):
        return f'{self.descriptor_name}' if hasattr(self, 'owner') else None

    @property
    def slug_global(self):
        return f'{self.owner.slug_global}_{self.slug_property}' if hasattr(self, 'owner') else super().slug_global
