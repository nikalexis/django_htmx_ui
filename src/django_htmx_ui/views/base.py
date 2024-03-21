import importlib
import inspect
import os

from django.views.generic.base import TemplateResponseMixin, ContextMixin, View
from django.template.response import TemplateResponse
from django_htmx_ui.utils import ContextCachedProperty, ContextProperty, to_snake_case
from django_htmx_ui.views.properties.managers.context import ContextManager


class ExtendedTemplateResponse(TemplateResponse):

    def __str__(self):
        return self.content.decode(self.charset)


class ExtendedTemplateResponseMixin(TemplateResponseMixin):

    response_class = ExtendedTemplateResponse
    
    # TODO: Add also SimpleTemplateResponse and remove next line
    request = None

    @classmethod
    @property
    def module(cls):
        return importlib.import_module(cls.__module__)

    @classmethod
    @property
    def slug(cls):
        return to_snake_case(cls.__name__)

    @classmethod
    @property
    def instance_slug(cls):
        return cls.slug

    @classmethod
    @property
    def slug_module(cls):
        slug = getattr(cls.module, 'SLUG', cls.__module__.replace('.', '_'))
        return slug

    @classmethod
    @property
    def slug_global(cls):
        return f'{cls.slug_module}_{cls.slug}'

    @classmethod
    @property
    def templates_dir(cls):
        if hasattr(cls.module, 'TEMPLATES_DIR'):
            return cls.module.TEMPLATES_DIR
        else:
            return cls.module_to_jinja_dir

    @classmethod
    @property
    def module_to_jinja_dir(cls):
        app, views, path = cls.__module__.split('.', 2)
        return f'{app}/{path.replace(".", "/")}/'

    @classmethod
    @property
    def template_file(cls):
        return cls.slug + '.html'

    @classmethod
    @property
    def template_name(cls):
        return cls.templates_dir + cls.template_file

    @ContextProperty
    def slug_panel(self):
        return self.slug_module

    @ContextProperty
    def title(self):
        return getattr(self.module, 'TITLE', self.project_title)

    @ContextProperty
    def icon(self):
        return getattr(self.module, 'ICON', '')

    @ContextProperty
    def project_title(self):
        return os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]

    def get_properties(self, include=(), exclude=(), filter=bool):
        members = inspect.getmembers_static(
            self.__class__,
            lambda o:
                isinstance(o, include) and not isinstance(o, exclude) and filter(o)
        )
        return members


class ExtendedContextMixin(ContextMixin):
    
    context = ContextManager()

    def get_context_data(self, **kwargs):
        context = {
            **super().get_context_data(**kwargs),
            **{key: self.context[key] for key in self.context.keys()},
            **getattr(self, '_context', {}),
        }
        return context


class ExtendedView(View):
    pass


class ExtendedTemplateView(ExtendedTemplateResponseMixin, ExtendedContextMixin, ExtendedView):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
