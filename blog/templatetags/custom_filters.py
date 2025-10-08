from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """给表单字段添加CSS类的过滤器"""
    return field.as_widget(attrs={"class": css_class})
