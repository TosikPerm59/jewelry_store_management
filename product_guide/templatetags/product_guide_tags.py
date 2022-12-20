from django import template

from product_guide.models import Jewelry

register = template.Library()


@register.simple_tag(name='field_name')
def get_field_name(field=None):
    if field is not None and field != '':

        verbose_name = Jewelry._meta.get_field(field).verbose_name
        return verbose_name
