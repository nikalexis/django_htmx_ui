import functools
import inspect
import re

from django.urls import path, include
from django.shortcuts import redirect
from django_htmx.http import HttpResponseClientRedirect


class ContextProperty(property):
    pass


class ContextCachedProperty(functools.cached_property):
    pass


def collect_paths(module, app_name):
    from django_htmx_ui.views.generic import PublicTemplateView
    members = inspect.getmembers(
        module,
        lambda o:
        inspect.isclass(o) and issubclass(o, PublicTemplateView) and o.__module__ == module.__name__
    )
    slug = getattr(module, 'SLUG', module.__name__.split('.')[-1])
    path_root = getattr(module, 'PATH_ROOT', slug + '/')
    includes = [
        klass.path
        for name, klass in members
        if hasattr(klass, 'path')
    ]
    paths = path(path_root, include((includes, app_name), namespace=slug))
    return paths


def x_redirect(request,  url):
    if request.htmx:
        return HttpResponseClientRedirect(url)
    else:
        return redirect(url)


def paginated(items_per_page):
    def inner(func):
        def wrapper(self, *args, **kwargs):
            page = max(1, int(self.request.GET.get('page', 1)))
            index = (page - 1) * items_per_page
            return func(self, *args, **kwargs)[index:index+items_per_page]
        return wrapper
    return inner


def indexed(field, items_per_round, reverse=False):
    def inner(func):
        def wrapper(self, *args, **kwargs):
            qs = func(self, *args, **kwargs).order_by(f'-{field}' if reverse else field)
            last_field = getattr(self, f'last_{field}', self.request.GET.get(f'last_{field}'))
            if last_field:
                qs = qs.filter(**{
                    f'{field}__' + ('lt' if reverse else 'gt'): last_field,
                })
            return qs[0:items_per_round]
        return wrapper
    return inner


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def to_camel_case(name):
    return ''.join(word.title() for word in name.split('_'))


def merge(a, b, path=None, raise_conflicts=True):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif raise_conflicts:
                raise ValueError('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a
