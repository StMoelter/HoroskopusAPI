"""
House calculation utilities for horoscope API using Jean Meeus algorithms.
"""

import math
from typing import Dict
from math import radians, cos, tan, sin, atan2, degrees, asin
from app.astro_zodiac import zodiac_sign


def julian_day(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
) -> float:
    """
    Calculate the Julian Day for a given UTC date and time (Meeus, Chap. 7.1).
    """
    y = year
    m = month
    if m <= 2:
        y -= 1
        m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    jd_day = (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + day
        + B
        - 1524.5
    )
    frac = (hour + minute / 60 + second / 3600) / 24
    return jd_day + frac


def greenwich_sidereal_time(jd: float) -> float:
    """
    Calculate Greenwich Mean Sidereal Time in hours [0..24) (Meeus, Chap. 12.4).
    """
    T = (jd - 2451545.0) / 36525
    gmst_sec = (
        67310.54841
        + (8766003600 + 8640184.812866) * T
        + 0.093104 * T**2
        - 6.2e-6 * T**3
    )
    gmst_hours = (gmst_sec / 3600) % 24
    return gmst_hours


def local_sidereal_time(jd: float, longitude_deg: float) -> float:
    """
    Calculate Local Sidereal Time in degrees for given Julian Day and longitude.
    """
    gmst_hours = greenwich_sidereal_time(jd)
    lst_hours = (gmst_hours + longitude_deg / 15) % 24
    return lst_hours * 15


def calculate_ascendant(
    lst_deg: float,
    latitude_deg: float,
    epsilon_deg: float = 23.4392911,
) -> float:
    """
    Calculate the Ascendant (rising degree) in degrees (Meeus, Chap. 13.1).
    """
    lat_rad = radians(latitude_deg)
    eps_rad = radians(epsilon_deg)
    numerator = -cos(lat_rad)
    denominator = tan(eps_rad) * sin(lat_rad)
    ha_asc_rad = atan2(numerator, denominator)
    ha_asc_deg = degrees(ha_asc_rad)
    return (ha_asc_deg + lst_deg) % 360


def calculate_midheaven(
    lst_deg: float,
    latitude_deg: float,
    epsilon_deg: float = 23.4392911,
) -> float:
    """
    Calculate the Midheaven (MC) in degrees (Meeus, Chap. 13.2).
    """
    lst_rad = radians(lst_deg)
    lat_rad = radians(latitude_deg)
    eps_rad = radians(epsilon_deg)
    delta_mc_rad = asin(
        sin(lat_rad) * sin(eps_rad) + cos(lat_rad) * cos(eps_rad) * sin(lst_rad)
    )
    numerator = sin(lst_rad) * cos(eps_rad) - tan(lat_rad) * sin(eps_rad)
    denominator = cos(lst_rad)
    alpha_mc_rad = atan2(numerator, denominator)
    lambda_mc_rad = atan2(tan(alpha_mc_rad), cos(eps_rad))
    return (degrees(lambda_mc_rad) + 360) % 360


def equal_house_cusps(asc_deg: float) -> Dict[str, float]:
    """
    Return equal house cusps H1 through H12 starting from the Ascendant.
    """
    return {f"H{i}": (asc_deg + (i - 1) * 30) % 360 for i in range(1, 13)}


def calculate_placidus_houses(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    latitude_deg: float,
    longitude_deg: float,
    use_equal: bool = False,
) -> Dict[str, float]:
    """
    Calculate house cusps using the Placidus system (simplified).

    Note: real Placidus iterations for houses H2, H3, H11, and H12 are not implemented.
    """
    # compute Julian Day, sidereal time, ascendant and midheaven
    jd = julian_day(year, month, day, hour, minute, second)
    lst_deg = local_sidereal_time(jd, longitude_deg)
    asc_deg = calculate_ascendant(lst_deg, latitude_deg)
    mc_deg = calculate_midheaven(lst_deg, latitude_deg)

    houses = equal_house_cusps(asc_deg)
    if use_equal:
        return houses

    houses["H10"] = mc_deg
    return houses

def assign_planets_to_houses(planet_positions: Dict[str, float], house_cusps: Dict[str, float]) -> Dict[str, str]:
    """
    Assign each planet to a house based on their ecliptic longitudes.
    For each planet angle, find the house cusp interval [start, next_start), wrapping at 360°.
    """
    sorted_cusps = sorted(house_cusps.items(), key=lambda item: item[1])
    house_names = [name for name, _ in sorted_cusps]
    angles = [angle for _, angle in sorted_cusps]
    n = len(sorted_cusps)
    result: Dict[str, str] = {}
    for planet, pos in planet_positions.items():
        angle = pos % 360
        assigned = None
        for i in range(n):
            start = angles[i]
            end = angles[(i + 1) % n]
            if i < n - 1:
                if start <= angle < end:
                    assigned = house_names[i]
                    break
            else:
                if angle >= start or angle < angles[0]:
                    assigned = house_names[i]
                    break
        if assigned is None:
            raise ValueError(f"Could not assign planet {planet} with angle {pos}")
        result[planet] = assigned
    return result

def assign_houses_to_signs(house_cusps: Dict[str, float]) -> Dict[str, str]:
    """
    Assign each house to a zodiac sign based on its cusp ecliptic longitude.
    """
    result: Dict[str, str] = {}
    for house, cusp in house_cusps.items():
        result[house] = zodiac_sign(cusp)
    return result
