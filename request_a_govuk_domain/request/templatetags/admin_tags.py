from django import template

register = template.Library()


@register.filter(is_safe=True)
def changed_fields(obj):
    """
    Function to derive the changed fields from an object.
    If none of the fields are changed and still, there is a history object, then it suggests
    that the application was saved while updating the review.
    :param obj:
    :return:
    """
    if obj.prev_record:
        delta = obj.diff_against(obj.prev_record)
        changes = list(filter(lambda x: x != "last_updated_by", delta.changed_fields))
        return changes if changes else "Updated through review"
    return "-"


@register.filter(is_safe=True)
def owner_filter(app):
    """
    Extract the owner information from the application object.
    """
    return (
        f"{app.last_updated_by.username}"
        if app.last_updated_by != app.owner
        else f"{app.last_updated_by.username} (owner)"
    )


@register.simple_tag
def should_display(action, **kwargs):
    """
    Check the given history object should be displayed.
    Returns true if this is the last record in the history or if there is a difference in the following
    fields.
     # status
     # last_updated_by
     # owner
    :param action:
    :param kwargs:
    :return:
    """
    return (
        not action.next_record
        or action.next_record.history_object.status != action.history_object.status
        or action.next_record.history_object.last_updated_by
        != action.history_object.last_updated_by
        or action.next_record.history_object.owner != action.history_object.owner
    )
