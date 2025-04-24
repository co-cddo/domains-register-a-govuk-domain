from zoneinfo import ZoneInfo
from datetime import datetime
from django import template
from django.contrib.auth.models import User

from request_a_govuk_domain.request.models import Application

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
        return ", ".join(changes) if changes else "No Changes"
    return "Initial Data"


@register.filter
def application_admin_url(value, arg):
    return "admin:%s_%s_%s" % ("request", "application", arg)


@register.inclusion_tag(
    "simple_history/_review_object_history_list.html", takes_context=True
)
def display_review_list(context):
    context["application_history"] = Application.history.filter(
        id=context["object"].application.id
    ).order_by("-pk")
    return context


@register.inclusion_tag(
    "simple_history/_application_object_history_list.html", takes_context=True
)
def display_application_list(context):
    return context


@register.filter(is_safe=True)
def owner_filter(application):
    """
    Extract the owner information from the application object.
    """
    return (
        f"{application.last_updated_by.username}"
        if application.last_updated_by != application.owner
        else f"{application.last_updated_by.username} (owner)"
    )


@register.simple_tag
def history_type(action, **kwargs):
    return str(action[0].instance_type.__name__)


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
        or action.next_record.status != action.status
        or action.next_record.last_updated_by != action.last_updated_by
        or action.next_record.owner != action.owner
    )


@register.filter(is_safe=True)
def format_date(date):
    return (
        date.astimezone(ZoneInfo("Europe/London")).strftime("%d %b %Y %H:%M:%S %p")
        if date
        else "-"
    )


@register.filter(is_safe=True)
def days_since(value):
    now = datetime.now(tz=value.tzinfo) if value.tzinfo else datetime.now()
    delta = now - value
    if delta.days < 1:
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours} hours ago"
        else:
            minutes = delta.seconds // 60
            return f"{minutes} minutes ago"
    else:
        return f"{delta.days} days ago"


@register.filter(is_safe=True)
def format_username(user: User) -> str:
    if user.first_name != "":
        return user.first_name
    elif user.first_name != "" and user.last_name != "":
        return f"{user.first_name} {user.last_name}"
    else:
        return user.username


@register.filter(is_safe=True)
def format_username_or_me(user: User, logged_in_username: str) -> str:
    if user.username == logged_in_username:
        return "me"
    else:
        return format_username(user)
