
from django_htmx_ui.views.properties.base import BaseWidget, ForeignProperty


class ForeignView(ForeignProperty):

    def __init__(self, view, name=None, add_in_context=True, context_mapping=None) -> None:
        super().__init__(name, add_in_context)
        self.view = view
        self.context_mapping = context_mapping

    def setup_foreigner(self, instance, descriptor, context):
        super().setup_foreigner(instance, descriptor, context)
        self.view.foreigner = self.foreigner

    def _get(self, instance, owner):
        v = self.view()
        v.setup(v.foreigner.instance.request)
        response = v.render_to_response(
            v.get_context_data()
        )
        response.render()
        return response


class ForeignContext(ForeignProperty):

    def __init__(self, name=None, required=True, add_in_context=True) -> None:
        super().__init__(name, add_in_context)
        self.required = required

    def _get(self, instance, owner):
        context_mapping = instance.foreigner.descriptor.context_mapping
        return instance.foreigner.context[
            context_mapping.get(self.name, self.name) if context_mapping else self.name
        ]
