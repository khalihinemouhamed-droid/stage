from django import template

register = template.Library()

@register.filter
def format_retard(minutes):
    """
    Convertit un nombre de minutes en format lisible :
    0 → ''
    45 → '45min'
    60 → '1h00'
    125 → '2h05min'
    """
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        return ''

    if minutes <= 0:
        return ''

    heures = minutes // 60
    mins = minutes % 60

    if heures > 0 and mins > 0:
        return f"{heures}h{mins:02d}min"
    elif heures > 0:
        return f"{heures}h00"
    else:
        return f"{mins}min"
