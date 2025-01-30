from typing import Any
from django import template

register = template.Library()


@register.filter
def divide_by_60(value: Any) -> Any:
    try:
        return int(value) // 60
    except (ValueError, TypeError):
        return value
