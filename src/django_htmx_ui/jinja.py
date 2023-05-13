from functools import cached_property

import django.forms.renderers
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django_htmx.jinja import django_htmx_script
from django.utils.translation import gettext, ngettext
import humanize

from jinja2 import Environment


def environment(**options):
    options.update({'extensions':['jinja2.ext.i18n']})
    env = Environment(**options)
    env.install_gettext_callables(gettext=gettext, ngettext=ngettext, newstyle=True)
    env.globals.update({
        'static': static,
        'url': reverse,
        'humanize': humanize,
        'now': timezone.now,
        'django_htmx_script': django_htmx_script,
    })
    return env


class Jinja2DivFormRenderer(django.forms.renderers.Jinja2DivFormRenderer):

    @cached_property
    def engine(self):
        for b in settings.TEMPLATES:
            if b['BACKEND'] == 'django.template.backends.jinja2.Jinja2':
                return self.backend(
                    {
                        'NAME': 'Jinja2DivFormRenderer',
                        'DIRS': b['DIRS'],
                        'APP_DIRS': b['APP_DIRS'],
                        'OPTIONS': b['OPTIONS'],
                    }
                )

def fix_django_admin_templates():
    from django.contrib import admin
    from django.forms.renderers import DjangoTemplates

    class ModelAdmin(admin.ModelAdmin):
        def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)
            form.default_renderer = DjangoTemplates
            return form

    setattr(admin, 'ModelAdmin', ModelAdmin)

def get_form_renderer(fix_django_admin=True):
    if fix_django_admin:
        fix_django_admin_templates()
    return 'django_htmx_ui.jinja.Jinja2DivFormRenderer'
