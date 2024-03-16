import importlib
import inspect
import os

from django.views.generic.base import TemplateResponseMixin, ContextMixin, View
from django.template.response import TemplateResponse
from markupsafe import Markup
from django_htmx_ui.utils import ContextCachedProperty, ContextProperty, to_snake_case


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
            app, views, crud = cls.__module__.split('.')
            return f'{app}/{crud}/'

    @classmethod
    @property
    def module_to_jinja_dir(cls):
        print(cls.__module__.split('.', 2))
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
    def html_id(self):
        return self.slug_global

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

    def context_from_properties(self, include=(), exclude=(), context=None):
        from django_htmx_ui.views.properties.base import BaseProperty, ForeignProperty
        from django_htmx_ui.views.properties.foreigners import ForeignContext

        def filter(member):
            if issubclass(type(member), BaseProperty):
                return member.add_in_context

            if issubclass(type(member), ForeignContext):
                if not context or member.name not in context:
                    
                    if member.required:
                        raise ValueError(f"Required context variable named '{member.name}' not found in the context of foreign descriptor '{self.foreigner_descriptor.descriptor_name}' in '{self.foreigner_descriptor.__class__}' for foreigner type '{self.foreigner.__class__}'")
                    
                    return False

            return True

        def context_key(descriptor_name, member):
            if issubclass(type(member), BaseProperty):
                return member.name
            
            return descriptor_name

        def context_value(descriptor_name, member):
            if issubclass(type(member), ForeignProperty):
                member.setup_foreigner(
                    instance=self,
                    descriptor=member,
                    context=context,
                )

            value = getattr(self, descriptor_name)
            
            if type(value) is self.response_class:
                value = Markup(value)
            
            return value

        return {
            context_key(descriptor_name, member): context_value(descriptor_name, member)
            for descriptor_name, member in self.get_properties(include, exclude, filter)
        }

    def get_context_data(self, **kwargs):
        from django_htmx_ui.views.properties.base import BaseProperty, ForeignProperty

        my_context = {
            **super().get_context_data(**kwargs),
            **self.context_from_properties(
                include=(
                    ContextProperty,
                    ContextCachedProperty,
                    BaseProperty,
                ),
                exclude=(
                    ForeignProperty,
                ),
            ),
            **getattr(self, '_context', {}),
        }
        foreign_context = self.context_from_properties(
            include=(
                ForeignProperty,
            ),
            context=my_context,
        )
        return {**my_context, **foreign_context}


class ExtendedContextMixin(ContextMixin):
    pass


class ExtendedView(View):
    pass


class ExtendedTemplateView(ExtendedTemplateResponseMixin, ExtendedContextMixin, ExtendedView):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
