"""
Zodiac sign determination based on ecliptic longitude.
"""


def zodiac_sign(ecl_lon_deg: float) -> str:
    """
    Return the German zodiac sign name for a given ecliptic longitude in degrees.

    Args:
        ecl_lon_deg: Ecliptic longitude in degrees.

    Returns:
        Zodiac sign name in German.
    """
    lon = ecl_lon_deg % 360
    if 0 <= lon < 30:
        return "Widder"
    if 30 <= lon < 60:
        return "Stier"
    if 60 <= lon < 90:
        return "Zwillinge"
    if 90 <= lon < 120:
        return "Krebs"
    if 120 <= lon < 150:
        return "Löwe"
    if 150 <= lon < 180:
        return "Jungfrau"
    if 180 <= lon < 210:
        return "Waage"
    if 210 <= lon < 240:
        return "Skorpion"
    if 240 <= lon < 270:
        return "Schütze"
    if 270 <= lon < 300:
        return "Steinbock"
    if 300 <= lon < 330:
        return "Wassermann"
    return "Fische"
