"""
Set custom variables in a Django template
"""

# Django
from django import template

register = template.Library()


class SetVarNode(template.Node):
    """
    SetVarNode
    """

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        """
        Render context
        :param context:
        :return:
        """

        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""

        context[self.var_name] = value

        return ""


@register.tag(name="set_template_variable")
def set_template_variable(parser, token):
    """
    Set a template variable
    Usage: {% set_template_variable <var_name> = <var_value> %}
    :param parser:
    :param token:
    :return:
    """

    parts = token.split_contents()

    if len(parts) < 4:
        raise template.TemplateSyntaxError(
            "'set_template_variable' tag must be of the form: "
            "{% set_template_variable <var_name> = <var_value> %}"
        )

    return SetVarNode(parts[1], parts[3])
