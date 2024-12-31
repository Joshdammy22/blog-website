# blog/templatetags/blog_filters.py

from django import template
from blog.models import Blog

register = template.Library()

@register.filter
def reaction_count(blog, reaction_type):
    return blog.get_reaction_count(reaction_type)
