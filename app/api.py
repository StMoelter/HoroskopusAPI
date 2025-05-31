"""
API endpoints for the Horoskop-API using Flask-RESTX.
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields


from . import astro_ephemeris, astro_zodiac, astro_aspects, astro_houses


def create_app() -> Flask:
    """
    Create and configure the Flask application with RESTX API.
    """
    app = Flask(__name__)
    api = Api(
        app,
        version="1.0",
        title="Horoskop-API",
        description="Erstellt Geburtshoroskop (Planeten, Aspekte, Häuser)",
        doc="/docs",
    )

    coords_model = api.model(
        "Coordinates",
        {
            "latitude": fields.Float(required=True, description="Breitengrad"),
            "longitude": fields.Float(required=True, description="Längengrad"),
        },
    )

    request_model = api.model(
        "HoroscopeRequest",
        {
            "year": fields.Integer(
                required=True, description="Geburtsjahr (z.B. 2025)"
            ),
            "month": fields.Integer(required=True, description="Geburtsmonat (1–12)"),
            "day": fields.Integer(required=True, description="Geburtstag (1–31)"),
            "hour": fields.Integer(
                required=True, description="Geburtsstunde UTC (0–23)"
            ),
            "minute": fields.Integer(
                required=True, description="Geburtsminute UTC (0–59)"
            ),
            "second": fields.Integer(
                required=False, default=0, description="Geburtssekunde UTC (0–59)"
            ),
            "coordinates": fields.Nested(
                coords_model, description="Geburtsort-Koordinaten"
            ),
            "house_system": fields.String(
                required=False,
                default="placidus",
                description="'placidus' oder 'equal'",
            ),
        },
    )

    planet_position = api.model(
        "PlanetPosition",
        {
            "name": fields.String(description="Planet"),
            "ecliptic_longitude": fields.Float(description="Ekliptikale Länge (Grad)"),
            "zodiac": fields.String(description="Tierkreiszeichen"),
        },
    )

    aspect_item = api.model(
        "AspectItem",
        {
            "p1": fields.String(description="Planet 1"),
            "p2": fields.String(description="Planet 2"),
            "aspect": fields.String(description="Aspektname"),
            "orb": fields.Float(description="Orb in Grad"),
        },
    )

    house_cusp = api.model(
        "HouseCusp",
        {
            "house": fields.String(description="Hausname (H1–H12)"),
            "cusp": fields.Float(description="Ekliptikale Länge (Grad)"),
        },
    )

    response_model = api.model(
        "HoroscopeResponse",
        {
            "planets": fields.List(fields.Nested(planet_position)),
            "aspects": fields.List(fields.Nested(aspect_item)),
            "houses": fields.List(fields.Nested(house_cusp)),
        },
    )

    ns = api.namespace("horoscope", description="Horoskop-Operationen")

    @ns.route("/")
    class Horoscope(Resource):
        @ns.expect(request_model, validate=True)
        @ns.marshal_with(response_model)
        def post(self):
            data = request.json

            year = data["year"]
            month = data["month"]
            day = data["day"]
            hour = data["hour"]
            minute = data["minute"]
            second = data.get("second", 0)
            lat = data["coordinates"]["latitude"]
            lon = data["coordinates"]["longitude"]
            house_system = data.get("house_system", "placidus").lower()

            planet_names = [
                "sun",
                "moon",
                "mercury",
                "venus",
                "mars",
                "jupiter",
                "saturn",
                "uranus",
                "neptune",
                "pluto",
            ]
            planet_positions = {}
            for pname in planet_names:
                lon_deg = astro_ephemeris.get_ecliptic_longitude(
                    planet_name=pname,
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    second=second,
                    latitude=lat,
                    longitude=lon,
                )
                planet_positions[pname.capitalize()] = lon_deg

            planets_out = []
            for pname, lon_deg in planet_positions.items():
                sign = astro_zodiac.zodiac_sign(lon_deg)
                planets_out.append(
                    {
                        "name": pname,
                        "ecliptic_longitude": round(lon_deg, 6),
                        "zodiac": sign,
                    }
                )

            aspects_raw = astro_aspects.find_aspects(planet_positions)
            aspects_out = [
                {"p1": a["p1"], "p2": a["p2"], "aspect": a["aspect"], "orb": a["orb"]}
                for a in aspects_raw
            ]

            use_equal = house_system == "equal"
            raw_houses = astro_houses.calculate_placidus_houses(
                year, month, day, hour, minute, second, lat, lon, use_equal=use_equal
            )
            houses_out = [
                {"house": h, "cusp": round(cusp, 6)} for h, cusp in raw_houses.items()
            ]

            planets_in_houses_raw = astro_houses.assign_planets_to_houses(
                planet_positions, raw_houses
            )
            planets_in_houses = [
                {"planet": p, "house": h} for p, h in planets_in_houses_raw.items()
            ]

            signs_in_houses_raw = astro_houses.assign_houses_to_signs(raw_houses)
            signs_in_houses = [
                {"house": h, "sign": s} for h, s in signs_in_houses_raw.items()
            ]

            asc_cusp = raw_houses.get("H1")
            desc_cusp = raw_houses.get("H7")
            ascendant = {
                "cusp": round(asc_cusp, 6),
                "sign": astro_zodiac.zodiac_sign(asc_cusp),
            }
            descendant = {
                "cusp": round(desc_cusp, 6),
                "sign": astro_zodiac.zodiac_sign(desc_cusp),
            }

            return {
                "planets": planets_out,
                "aspects": aspects_out,
                "houses": houses_out,
                "planets_in_houses": planets_in_houses,
                "signs_in_houses": signs_in_houses,
                "ascendant": ascendant,
                "descendant": descendant,
            }

    return app
