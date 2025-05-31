"""
Ephemeris calculations for horoscope API using Skyfield JPL ephemerides.
"""

from skyfield.api import load, Topos

valid = {
    'sun': 'SUN',
    'moon': 'MOON',
    'mercury': 'MERCURY BARYCENTER',
    'venus': 'VENUS BARYCENTER',
    'earth': 'EARTH BARYCENTER',
    'mars': 'MARS BARYCENTER',
    'jupiter': 'JUPITER BARYCENTER',
    'saturn': 'SATURN BARYCENTER',
    'uranus': 'URANUS BARYCENTER',
    'neptune': 'NEPTUNE BARYCENTER',
    'pluto': 'PLUTO BARYCENTER'
}

_TS = load.timescale()
_EPH = load("de421.bsp")
_EARTH = _EPH["earth"]


def get_ecliptic_longitude(
    planet_name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    latitude: float,
    longitude: float,
) -> float:
    """
    Return the ecliptic longitude (0 ≤ λ < 360 degrees) of a classical planet as seen
    from a given Earth latitude/longitude at a specific UTC date and time.

    Args:
        planet_name: Name of the planet ('sun','moon','mercury','venus','mars',
                     'jupiter','saturn','uranus','neptune','pluto').
        year: UTC year.
        month: UTC month (1-12).
        day: UTC day (1-31).
        hour: UTC hour (0-23).
        minute: UTC minute (0-59).
        second: UTC second (0-59).
        latitude: Observer latitude in degrees.
        longitude: Observer longitude in degrees.

    Returns:
        Ecliptic longitude in degrees [0, 360).

    Raises:
        ValueError: If planet_name is not a supported classical body.
    """
    name = planet_name.lower()
    try:
        planet_key = valid[name]
    except KeyError:
        raise ValueError(f"Ungültiger Planetname: {planet_name}")

    observer = _EARTH + Topos(latitude_degrees=latitude, longitude_degrees=longitude)
    t = _TS.utc(year, month, day, hour, minute, second)
    planet = _EPH[planet_key]
    astrometric = observer.at(t).observe(planet)
    ecliptic_latlon = astrometric.ecliptic_latlon()
    return ecliptic_latlon[1].degrees % 360
