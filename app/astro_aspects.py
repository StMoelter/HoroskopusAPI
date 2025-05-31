from typing import Dict, List

ASPECTS = {
    "Konjunktion": (0.0, 8.0),
    "Sextil": (60.0, 6.0),
    "Quadrat": (90.0, 6.0),
    "Trigon": (120.0, 6.0),
    "Opposition": (180.0, 8.0),
}


def find_aspects(planet_positions: Dict[str, float]) -> List[Dict]:
    """
    Identifies astrological aspects between planet positions.

    Args:
        planet_positions: Mapping of planet names to their ecliptic longitudes in degrees.

    Returns:
        A list of dicts, each containing:
            'p1': first planet name,
            'p2': second planet name,
            'aspect': aspect name,
            'orb': difference from exact aspect angle (rounded to 2 decimals).
    """
    results: List[Dict] = []
    names = list(planet_positions.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1 = names[i]
            p2 = names[j]
            l1 = planet_positions[p1]
            l2 = planet_positions[p2]
            diff = abs((l1 - l2 + 180) % 360 - 180)
            for aspect_name, (exact_angle, orb) in ASPECTS.items():
                delta = abs(diff - exact_angle)
                if delta <= orb:
                    results.append(
                        {
                            "p1": p1,
                            "p2": p2,
                            "aspect": aspect_name,
                            "orb": round(delta, 2),
                        }
                    )
                    break
    return results
