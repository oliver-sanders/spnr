from django import template
import calendar

register = template.Library()

@register.filter
def month_name(month_no):
    return calendar.month_abbr[int(month_no)]
