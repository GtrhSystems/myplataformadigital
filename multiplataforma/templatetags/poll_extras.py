from django import template

register = template.Library()

@register.filter(name='two_decimal')
def two_decimal(value, arg):

    value_dot= round(value, arg)
    return str(value_dot).replace(",", ".")


