from django import template
from django.utils.safestring import mark_safe
import markdown
from ..models import Objective

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

@register.inclusion_tag('blog/objectius/list.html')
def show_objectives():
    objs = Objective.incomplete.order_by('-priority')[:]
    return {'objectives': objs}
    
