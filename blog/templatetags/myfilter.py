#coding=utf-8
from django import template

register = template.Library()

@register.filter
def month_to_upper(value):
        x = value.replace(tzinfo=None)
        month=x.month
        switcher = {
            0: "一",
            1: "二",
            2: "三",
            4: "四",
            5: "五",
            6: "六",
            7: "七",
            8: "八",
            9: "九",
            10: "十",
            11: "十一",
            12: "十二",
        }
        return switcher.get(month, "nothing")
