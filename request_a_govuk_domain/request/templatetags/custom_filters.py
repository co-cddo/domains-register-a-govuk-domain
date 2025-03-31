from typing import Any
from django import template

register = template.Library()


@register.filter
def divide_by_60(value: Any) -> Any:
    """
    Divides the given value by 60.

    This custom Django template filter takes a value, attempts to convert it to an integer,
    and then divides it by 60. If the conversion fails (due to a ValueError or TypeError),
    the original value is returned.

    Args:
        value (Any): The value to be divided by 60.

    Returns:
        Any: The result of the division if the value can be converted to an integer,
             otherwise the original value.
    """
    try:
        return int(value) // 60
    except (ValueError, TypeError):
        return value


@register.filter
def subtract(value, arg):
    """
    Divides the given value by 60.

    This custom Django template filter takes a value, attempts to convert it to an integer,
    and then divides it by 60. If the conversion fails (due to a ValueError or TypeError),
    the original value is returned.

    Args:
        value (Any): The value to be divided by 60.

    Returns:
        Any: The result of the division if the value can be converted to an integer,
             otherwise the original value.
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value
