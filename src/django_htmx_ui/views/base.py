import importlib
import inspect
import os

from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin, ContextMixin, View
from django.template.response import TemplateResponse
from django_htmx_ui.utils import ContextCachedProperty, ContextProperty, to_snake_case
from django_htmx_ui.views.managers.context import ContextManager
from dominate.util import container
from dominate.all import *


class RawResponse(HttpResponse):

    def __str__(self):
        return self.content.decode(self.charset)


class RawResponseMixin:

    raw_method_origin = '__raw_origin__'
    raw_method_partial = '__raw__'
    raw_response_class = RawResponse

    def render_to_response(self, method=None):
        return self.raw_response_class(
            (method or self.get_raw_method())()
        )

    def get_raw_method(self):
        raw_attr = self.raw_method_origin if getattr(self, 'is_origin_request', False) else self.raw_method_partial
        return getattr(self, raw_attr, None)


class DominateResponse(HttpResponse):

    def __init__(self, dominate_container, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = dominate_container

    def __str__(self):
        return self.content.decode(self.charset)


class DominateResponseMixin:

    dominate_method_origin = '__dominate_origin__'
    dominate_method_partial = '__dominate__'
    dominate_response_class = DominateResponse

    def render_to_response(self, method=None):
        return self.dominate_response_class(self.__render_dominate__(method))

    def get_dominate_method(self):
        dominate_attr = self.dominate_method_origin if getattr(self, 'is_origin_request', False) else self.dominate_method_partial
        return getattr(self, dominate_attr, None)

    def __render_dominate__(self, method=None):
        container_ = container()
        with container_:
            (method or self.get_dominate_method)()

        if getattr(method, 'auto_add_html_id', True):
            if method.__name__ != self.dominate_method_origin:
                clean_children = [
                    child
                    for child in container_
                    if 'hx-swap-oob' not in child.attributes
                ]
                if len(clean_children) == 1:
                    child = clean_children[0]
                    if type(child) not in (document, html, head, body, meta, title, style, script):
                        child.attributes.setdefault('id', self.slug_global)
        
        return container_


class ExtendedTemplateResponse(TemplateResponse):

    def __str__(self):
        self.render()
        return self.content.decode(self.charset)


class ExtendedTemplateResponseMixin(RawResponseMixin, DominateResponseMixin, TemplateResponseMixin):

    response_class = ExtendedTemplateResponse
    
    # TODO: Add also SimpleTemplateResponse and remove next line
    request = None

    def render_to_response(self, *args, **kwargs):
        if raw_method := self.get_raw_method():
            return RawResponseMixin.render_to_response(self, raw_method)
        elif dominate_method := self.get_dominate_method():
            return DominateResponseMixin.render_to_response(self, dominate_method)
        else:
            context = self.get_context_data(**kwargs)
            return TemplateResponseMixin.render_to_response(self, context)

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
            **self.context.all(),
            **getattr(self, '_context', {}),
        }
        return context


class ExtendedView(View):

    def __init__(self, **kwargs):
        self.view = self
        super().__init__(**kwargs)


class ExtendedTemplateView(ExtendedTemplateResponseMixin, ExtendedContextMixin, ExtendedView):

    def get(self, request, *args, **kwargs):
        return self.render_to_response(*args, **kwargs)
