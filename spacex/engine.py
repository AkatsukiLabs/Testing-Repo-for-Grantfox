"""Deterministic in-memory SpaceX dataset and query execution engine."""

import copy
import re
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from spacex.exceptions import NotFoundError, ValidationError
from spacex.types import (
    Capsule,
    CompanyInfo,
    CrewMember,
    Launch,
    Launchpad,
    Payload,
    QueryResult,
    Rocket,
    Ship,
    Starlink,
)

T = TypeVar("T")

DEFAULT_ROCKETS: List[Dict[str, Any]] = [
    {
        "id": "5e9d0d95eda69955f709d1eb",
        "name": "Falcon 1",
        "type": "rocket",
        "active": False,
        "stages": 2,
        "boosters": 0,
        "cost_per_launch": 6700000,
        "success_rate_pct": 40,
        "first_flight": "2006-03-24",
        "country": "United States",
        "company": "SpaceX",
        "wikipedia": "https://en.wikipedia.org/wiki/Falcon_1",
        "description": "The Falcon 1 was an expendable launch system privately developed and manufactured by SpaceX.",
        "height": {"meters": 22.25, "feet": 73.0},
        "diameter": {"meters": 1.68, "feet": 5.5},
        "mass": {"kg": 30146, "lb": 66460},
        "engines": {
            "number": 1,
            "type": "merlin",
            "version": "1C",
            "layout": "single",
            "loss_max": 0,
            "propellant_1": "liquid oxygen",
            "propellant_2": "RP-1 kerosene",
            "thrust_sea_level": {"kN": 420, "lbf": 94000},
            "thrust_vacuum": {"kN": 480, "lbf": 110000},
            "thrust_to_weight": 96.0,
        },
        "first_stage": {
            "reusable": False,
            "engines": 1,
            "fuel_amount_tons": 21.5,
            "burn_time_sec": 169,
            "thrust_sea_level": {"kN": 420, "lbf": 94000},
            "thrust_vacuum": {"kN": 480, "lbf": 110000},
        },
        "second_stage": {
            "reusable": False,
            "engines": 1,
            "fuel_amount_tons": 3.9,
            "burn_time_sec": 378,
            "thrust": {"kN": 31, "lbf": 7000},
        },
        "flickr_images": [
            "https://farm1.staticflickr.com/972/40852720112_c764d2bda3_b.jpg"
        ],
    },
    {
        "id": "5e9d0d95eda69973a809d1ec",
        "name": "Falcon 9",
        "type": "rocket",
        "active": True,
        "stages": 2,
        "boosters": 0,
        "cost_per_launch": 50000000,
        "success_rate_pct": 98,
        "first_flight": "2010-06-04",
        "country": "United States",
        "company": "SpaceX",
        "wikipedia": "https://en.wikipedia.org/wiki/Falcon_9",
        "description": "Falcon 9 is a two-stage rocket designed and manufactured by SpaceX for the reliable and safe transport of satellites and the Dragon spacecraft into orbit.",
        "height": {"meters": 70.0, "feet": 229.6},
        "diameter": {"meters": 3.7, "feet": 12.0},
        "mass": {"kg": 549054, "lb": 1207920},
        "engines": {
            "number": 9,
            "type": "merlin",
            "version": "1D+",
            "layout": "octaweb",
            "loss_max": 2,
            "propellant_1": "liquid oxygen",
            "propellant_2": "RP-1 kerosene",
            "thrust_sea_level": {"kN": 845, "lbf": 190000},
            "thrust_vacuum": {"kN": 981, "lbf": 220500},
            "thrust_to_weight": 180.0,
        },
        "first_stage": {
            "reusable": True,
            "engines": 9,
            "fuel_amount_tons": 385.0,
            "burn_time_sec": 162,
            "thrust_sea_level": {"kN": 7607, "lbf": 1710000},
            "thrust_vacuum": {"kN": 8227, "lbf": 1849500},
        },
        "second_stage": {
            "reusable": False,
            "engines": 1,
            "fuel_amount_tons": 90.0,
            "burn_time_sec": 397,
            "thrust": {"kN": 934, "lbf": 210000},
        },
        "flickr_images": [
            "https://farm1.staticflickr.com/929/28787338307_3453a11a77_b.jpg",
            "https://farm4.staticflickr.com/3955/32915197674_eee74d81bb_b.jpg",
        ],
    },
    {
        "id": "5e9d0d95eda69974db09d1ed",
        "name": "Falcon Heavy",
        "type": "rocket",
        "active": True,
        "stages": 2,
        "boosters": 2,
        "cost_per_launch": 90000000,
        "success_rate_pct": 100,
        "first_flight": "2018-02-06",
        "country": "United States",
        "company": "SpaceX",
        "wikipedia": "https://en.wikipedia.org/wiki/Falcon_Heavy",
        "description": "With the ability to lift into orbit nearly 64 metric tons, Falcon Heavy can lift more than twice the payload of the next closest operational vehicle.",
        "height": {"meters": 70.0, "feet": 229.6},
        "diameter": {"meters": 12.2, "feet": 39.9},
        "mass": {"kg": 1420788, "lb": 3125735},
        "engines": {
            "number": 27,
            "type": "merlin",
            "version": "1D+",
            "layout": "octaweb",
            "loss_max": 6,
            "propellant_1": "liquid oxygen",
            "propellant_2": "RP-1 kerosene",
            "thrust_sea_level": {"kN": 845, "lbf": 190000},
            "thrust_vacuum": {"kN": 981, "lbf": 220500},
            "thrust_to_weight": 180.0,
        },
        "first_stage": {
            "reusable": True,
            "engines": 27,
            "fuel_amount_tons": 1155.0,
            "burn_time_sec": 162,
            "thrust_sea_level": {"kN": 22819, "lbf": 5130000},
            "thrust_vacuum": {"kN": 24681, "lbf": 5548500},
        },
        "second_stage": {
            "reusable": False,
            "engines": 1,
            "fuel_amount_tons": 90.0,
            "burn_time_sec": 397,
            "thrust": {"kN": 934, "lbf": 210000},
        },
        "flickr_images": [
            "https://farm5.staticflickr.com/4645/38583830575_3f0f7215e6_b.jpg"
        ],
    },
    {
        "id": "5e9d0d96eda699382d09d1ee",
        "name": "Starship",
        "type": "rocket",
        "active": True,
        "stages": 2,
        "boosters": 0,
        "cost_per_launch": 10000000,
        "success_rate_pct": 100,
        "first_flight": "2023-04-20",
        "country": "United States",
        "company": "SpaceX",
        "wikipedia": "https://en.wikipedia.org/wiki/SpaceX_Starship",
        "description": "Starship and Super Heavy constitute a fully reusable transportation system designed to carry both crew and cargo to Earth orbit, the Moon, Mars, and beyond.",
        "height": {"meters": 121.0, "feet": 397.0},
        "diameter": {"meters": 9.0, "feet": 29.5},
        "mass": {"kg": 5000000, "lb": 11000000},
        "engines": {
            "number": 33,
            "type": "raptor",
            "version": "2",
            "layout": "cluster",
            "loss_max": 3,
            "propellant_1": "liquid oxygen",
            "propellant_2": "liquid methane",
            "thrust_sea_level": {"kN": 2256, "lbf": 507000},
            "thrust_vacuum": {"kN": 2530, "lbf": 569000},
            "thrust_to_weight": 210.0,
        },
        "first_stage": {
            "reusable": True,
            "engines": 33,
            "fuel_amount_tons": 3400.0,
            "burn_time_sec": 160,
            "thrust_sea_level": {"kN": 74448, "lbf": 16730000},
            "thrust_vacuum": {"kN": 83490, "lbf": 18770000},
        },
        "second_stage": {
            "reusable": True,
            "engines": 6,
            "fuel_amount_tons": 1200.0,
            "burn_time_sec": 350,
            "thrust": {"kN": 14700, "lbf": 3300000},
        },
        "flickr_images": [
            "https://live.staticflickr.com/65535/51966567104_f145cf3558_k.jpg"
        ],
    },
]

DEFAULT_CAPSULES: List[Dict[str, Any]] = [
    {
        "id": "5e9e2c5bf35918ed973b2664",
        "serial": "C101",
        "status": "retired",
        "type": "Dragon 1.0",
        "dragon": "5e9d0c83eda69976eb09d1e3",
        "reuse_count": 0,
        "water_landings": 1,
        "land_landings": 0,
        "last_update": "Reentered after orbital test flight.",
        "launches": ["5eb87cdaffd86e000604b32b"],
    },
    {
        "id": "5e9e2c5df359188bfb3b2675",
        "serial": "C206",
        "status": "active",
        "type": "Dragon 2.0",
        "dragon": "5e9d0c83eda69976eb09d1e4",
        "reuse_count": 4,
        "water_landings": 5,
        "land_landings": 0,
        "last_update": "Endeavour capsule in commercial crew rotation.",
        "launches": ["5eb87d46ffd86e000604b388"],
    },
    {
        "id": "5e9e2c5df3591816f23b2676",
        "serial": "C207",
        "status": "active",
        "type": "Dragon 2.0",
        "dragon": "5e9d0c83eda69976eb09d1e4",
        "reuse_count": 3,
        "water_landings": 4,
        "land_landings": 0,
        "last_update": "Resilience capsule in operational service.",
        "launches": ["600f9a8d05eb594d41c32980"],
    },
]

DEFAULT_CREW: List[Dict[str, Any]] = [
    {
        "id": "5ebf1a6e23a9a60006e03a7a",
        "name": "Robert Behnken",
        "agency": "NASA",
        "image": "https://imgur.com/0smMgMH.png",
        "wikipedia": "https://en.wikipedia.org/wiki/Bob_Behnken",
        "status": "retired",
        "launches": ["5eb87d46ffd86e000604b388"],
    },
    {
        "id": "5ebf1b7323a9a60006e03a7b",
        "name": "Douglas Hurley",
        "agency": "NASA",
        "image": "https://imgur.com/ooaA6pn.png",
        "wikipedia": "https://en.wikipedia.org/wiki/Doug_Hurley",
        "status": "retired",
        "launches": ["5eb87d46ffd86e000604b388"],
    },
    {
        "id": "607a37545a9634000662d558",
        "name": "Jared Isaacman",
        "agency": "Commercial",
        "image": "https://imgur.com/abc1234.png",
        "wikipedia": "https://en.wikipedia.org/wiki/Jared_Isaacman",
        "status": "active",
        "launches": ["600f9a8d05eb594d41c32980"],
    },
    {
        "id": "607a37545a9634000662d559",
        "name": "Sian Proctor",
        "agency": "Commercial",
        "image": "https://imgur.com/def5678.png",
        "wikipedia": "https://en.wikipedia.org/wiki/Sian_Proctor",
        "status": "active",
        "launches": ["600f9a8d05eb594d41c32980"],
    },
]

DEFAULT_LAUNCHPADS: List[Dict[str, Any]] = [
    {
        "id": "5e9e4501f3591823a93b2628",
        "name": "SLC-40",
        "full_name": "Space Launch Complex 40",
        "status": "active",
        "locality": "Cape Canaveral",
        "region": "Florida",
        "timezone": "America/New_York",
        "latitude": 28.5618571,
        "longitude": -80.577366,
        "launch_attempts": 180,
        "launch_successes": 178,
        "rockets": ["5e9d0d95eda69973a809d1ec"],
        "launches": ["5eb87d03ffd86e000604b350", "600f9a8d05eb594d41c32982"],
    },
    {
        "id": "5e9e4502f35918c0803b262d",
        "name": "LC-39A",
        "full_name": "Launch Complex 39A",
        "status": "active",
        "locality": "Cape Canaveral",
        "region": "Florida",
        "timezone": "America/New_York",
        "latitude": 28.6080585,
        "longitude": -80.6039558,
        "launch_attempts": 75,
        "launch_successes": 75,
        "rockets": ["5e9d0d95eda69973a809d1ec", "5e9d0d95eda69974db09d1ed"],
        "launches": [
            "5eb87d13ffd86e000604b360",
            "5eb87d46ffd86e000604b388",
            "600f9a8d05eb594d41c32980",
        ],
    },
    {
        "id": "5e9e4502f3591855c03b262e",
        "name": "SLC-4E",
        "full_name": "Space Launch Complex 4E",
        "status": "active",
        "locality": "Vandenberg Space Force Base",
        "region": "California",
        "timezone": "America/Los_Angeles",
        "latitude": 34.632093,
        "longitude": -120.610829,
        "launch_attempts": 45,
        "launch_successes": 45,
        "rockets": ["5e9d0d95eda69973a809d1ec"],
        "launches": [],
    },
    {
        "id": "5e9e4502f3591855c03b262f",
        "name": "Starbase",
        "full_name": "Starbase Orbital Launch Pad 1",
        "status": "active",
        "locality": "Boca Chica",
        "region": "Texas",
        "timezone": "America/Chicago",
        "latitude": 25.997164,
        "longitude": -97.155422,
        "launch_attempts": 4,
        "launch_successes": 3,
        "rockets": ["5e9d0d96eda699382d09d1ee"],
        "launches": ["65a3d0f005eb594d41c32999"],
    },
]

DEFAULT_SHIPS: List[Dict[str, Any]] = [
    {
        "id": "5ea6ed2e080df40006979607",
        "name": "Of Course I Still Love You",
        "type": "Barge",
        "active": True,
        "roles": ["ASDS barge", "Droneship"],
        "home_port": "Port of Long Beach",
        "status": "operational",
        "imo": 0,
        "mmsi": 368023450,
        "abs": 0,
        "class": 0,
        "mass_kg": 3500000.0,
        "mass_lbs": 7716179.0,
        "year_built": 2015,
        "speed_kn": 0.0,
        "course_deg": 0.0,
        "latitude": 33.74,
        "longitude": -118.26,
        "link": "https://en.wikipedia.org/wiki/Autonomous_spaceport_drone_ship",
        "image": "https://i.imgur.com/e5t98N1.jpg",
        "launches": ["5eb87d03ffd86e000604b350", "5eb87d46ffd86e000604b388"],
    },
    {
        "id": "5ea6ed2e080df40006979608",
        "name": "Just Read The Instructions",
        "type": "Barge",
        "active": True,
        "roles": ["ASDS barge", "Droneship"],
        "home_port": "Port Canaveral",
        "status": "operational",
        "imo": 0,
        "mmsi": 368023451,
        "abs": 0,
        "class": 0,
        "mass_kg": 3500000.0,
        "mass_lbs": 7716179.0,
        "year_built": 2015,
        "speed_kn": 0.0,
        "course_deg": 0.0,
        "latitude": 28.41,
        "longitude": -80.61,
        "link": "https://en.wikipedia.org/wiki/Autonomous_spaceport_drone_ship",
        "image": "https://i.imgur.com/7VMC0Gn.jpg",
        "launches": ["600f9a8d05eb594d41c32980", "600f9a8d05eb594d41c32982"],
    },
]

DEFAULT_PAYLOADS: List[Dict[str, Any]] = [
    {
        "id": "5eb0e4b5b6c3bb0006eeb1e1",
        "name": "FalconSat",
        "type": "Satellite",
        "reused": False,
        "launch": "5eb87cdaffd86e000604b32b",
        "customers": ["DARPA"],
        "nationalities": ["United States"],
        "manufacturers": ["Surrey Satellite Technology Ltd"],
        "mass_kg": 19.5,
        "mass_lbs": 43.0,
        "orbit": "LEO",
        "reference_system": "geocentric",
        "regime": "low-earth",
        "semi_major_axis_km": 6821.0,
        "eccentricity": 0.001,
        "periapsis_km": 440.0,
        "apoapsis_km": 460.0,
        "inclination_deg": 9.3,
        "period_min": 93.5,
        "lifespan_years": 1.0,
    },
    {
        "id": "5eb0e4bdb6c3bb0006eeb1eb",
        "name": "Tesla Roadster",
        "type": "Payload",
        "reused": False,
        "launch": "5eb87d13ffd86e000604b360",
        "customers": ["SpaceX"],
        "nationalities": ["United States"],
        "manufacturers": ["Tesla"],
        "mass_kg": 1250.0,
        "mass_lbs": 2750.0,
        "orbit": "HCO",
        "reference_system": "heliocentric",
        "regime": "solar",
        "semi_major_axis_km": 198000000.0,
        "eccentricity": 0.256,
        "periapsis_km": 147000000.0,
        "apoapsis_km": 249000000.0,
        "inclination_deg": 1.08,
        "period_min": 796320.0,
        "lifespan_years": 1000000.0,
    },
    {
        "id": "5eb0e4d0b6c3bb0006eeb253",
        "name": "Crew Dragon DM-2",
        "type": "Crew Dragon",
        "reused": False,
        "launch": "5eb87d46ffd86e000604b388",
        "customers": ["NASA (CCtCap)"],
        "nationalities": ["United States"],
        "manufacturers": ["SpaceX"],
        "mass_kg": 9616.0,
        "mass_lbs": 21200.0,
        "orbit": "ISS",
        "reference_system": "geocentric",
        "regime": "low-earth",
        "semi_major_axis_km": 6791.0,
        "eccentricity": 0.0005,
        "periapsis_km": 416.0,
        "apoapsis_km": 424.0,
        "inclination_deg": 51.64,
        "period_min": 92.8,
        "lifespan_years": 0.5,
    },
    {
        "id": "607a37545a9634000662d55a",
        "name": "Inspiration4",
        "type": "Crew Dragon",
        "reused": True,
        "launch": "600f9a8d05eb594d41c32980",
        "customers": ["Shift4 Payments"],
        "nationalities": ["United States"],
        "manufacturers": ["SpaceX"],
        "mass_kg": 12519.0,
        "mass_lbs": 27600.0,
        "orbit": "LEO",
        "reference_system": "geocentric",
        "regime": "low-earth",
        "semi_major_axis_km": 6956.0,
        "eccentricity": 0.0002,
        "periapsis_km": 583.0,
        "apoapsis_km": 587.0,
        "inclination_deg": 51.64,
        "period_min": 96.4,
        "lifespan_years": 0.1,
    },
    {
        "id": "607a37545a9634000662d55b",
        "name": "Starlink Group 4-1",
        "type": "Satellite",
        "reused": False,
        "launch": "600f9a8d05eb594d41c32982",
        "customers": ["SpaceX"],
        "nationalities": ["United States"],
        "manufacturers": ["SpaceX"],
        "mass_kg": 15600.0,
        "mass_lbs": 34392.0,
        "orbit": "VLEO",
        "reference_system": "geocentric",
        "regime": "very-low-earth",
        "semi_major_axis_km": 6911.0,
        "eccentricity": 0.0001,
        "periapsis_km": 539.0,
        "apoapsis_km": 541.0,
        "inclination_deg": 53.2,
        "period_min": 95.3,
        "lifespan_years": 5.0,
    },
]

DEFAULT_STARLINK: List[Dict[str, Any]] = [
    {
        "id": "5eed770f096e59000698560d",
        "version": "v1.5",
        "launch": "600f9a8d05eb594d41c32982",
        "spaceTrack": {
            "NORAD_CAT_ID": 44713,
            "EPOCH": "2023-01-15T12:00:00.000000",
            "MEAN_MOTION": 15.06,
            "ECCENTRICITY": 0.00014,
            "INCLINATION": 53.22,
            "RA_OF_ASC_NODE": 128.45,
            "ARG_OF_PERICENTER": 74.12,
            "MEAN_ANOMALY": 286.01,
            "BSTAR": 0.000021,
        },
        "latitude": 34.05,
        "longitude": -118.25,
        "height_km": 540.2,
        "velocity_kms": 7.59,
    },
]

DEFAULT_LAUNCHES: List[Dict[str, Any]] = [
    {
        "id": "5eb87cdaffd86e000604b32b",
        "flight_number": 1,
        "name": "FalconSat",
        "date_utc": "2006-03-24T22:30:00.000Z",
        "date_unix": 1143239400,
        "rocket": "5e9d0d95eda69955f709d1eb",
        "success": False,
        "upcoming": False,
        "details": "Engine failure at 33 seconds and loss of vehicle.",
        "failures": [
            {
                "time": 33,
                "altitude": 1000,
                "reason": "merlin engine loss due to fuel line leak",
            }
        ],
        "crew": [],
        "ships": [],
        "capsules": ["5e9e2c5bf35918ed973b2664"],
        "payloads": ["5eb0e4b5b6c3bb0006eeb1e1"],
        "launchpad": "5e9e4501f3591823a93b2628",
        "cores": [
            {
                "core": "5e9e289df35918033d3b2623",
                "flight": 1,
                "gridfins": False,
                "legs": False,
                "reused": False,
                "landing_attempt": False,
                "landing_success": None,
                "landing_type": None,
                "landpad": None,
            }
        ],
        "links": {
            "patch": {
                "small": "https://images2.imgbox.com/40/e0/7Vlaakmr_o.png",
                "large": "https://images2.imgbox.com/94/f2/NNfield7_o.png",
            },
            "reddit": {
                "campaign": None,
                "launch": None,
                "media": None,
            },
            "presskit": None,
            "webcast": "https://www.youtube.com/watch?v=0a_00nJ_Y88",
            "youtube_id": "0a_00nJ_Y88",
            "article": "https://www.space.com/2196-spacex-inaugural-falcon-1-rocket-lost-launch.html",
            "wikipedia": "https://en.wikipedia.org/wiki/Falcon_1",
        },
        "auto_update": True,
    },
    {
        "id": "5eb87d03ffd86e000604b350",
        "flight_number": 20,
        "name": "OG2 Mission 2",
        "date_utc": "2015-12-22T01:29:00.000Z",
        "date_unix": 1450747740,
        "rocket": "5e9d0d95eda69973a809d1ec",
        "success": True,
        "upcoming": False,
        "details": "First successful primary orbital booster recovery landing at Landing Zone 1.",
        "failures": [],
        "crew": [],
        "ships": ["5ea6ed2e080df40006979607"],
        "capsules": [],
        "payloads": ["5eb0e4b5b6c3bb0006eeb1e1"],
        "launchpad": "5e9e4501f3591823a93b2628",
        "cores": [
            {
                "core": "5e9e289ef35918416a3b2624",
                "flight": 1,
                "gridfins": True,
                "legs": True,
                "reused": False,
                "landing_attempt": True,
                "landing_success": True,
                "landing_type": "RTLS",
                "landpad": "5e9e3032383ecb267a34e7c7",
            }
        ],
        "links": {
            "patch": {
                "small": "https://images2.imgbox.com/3c/0e/T8iJcSN3_o.png",
                "large": "https://images2.imgbox.com/4f/e3/I0ikt3W7_o.png",
            },
            "reddit": {
                "campaign": "https://www.reddit.com/r/spacex/comments/3wqq1a",
                "launch": "https://www.reddit.com/r/spacex/comments/3xp936",
                "media": None,
            },
            "presskit": "http://www.spacex.com/sites/spacex/files/orbcomm_og2_press_kit.pdf",
            "webcast": "https://www.youtube.com/watch?v=O5bTbVbe4e4",
            "youtube_id": "O5bTbVbe4e4",
            "article": "http://www.nasaspaceflight.com/2015/12/spacex-falcon-9-og2-mission/",
            "wikipedia": "https://en.wikipedia.org/wiki/Falcon_9_flight_20",
        },
        "auto_update": True,
    },
    {
        "id": "5eb87d13ffd86e000604b360",
        "flight_number": 55,
        "name": "Falcon Heavy Test Flight",
        "date_utc": "2018-02-06T20:45:00.000Z",
        "date_unix": 1517949900,
        "rocket": "5e9d0d95eda69974db09d1ed",
        "success": True,
        "upcoming": False,
        "details": "Maiden flight of Falcon Heavy carrying Elon Musk's Tesla Roadster into heliocentric orbit.",
        "failures": [],
        "crew": [],
        "ships": ["5ea6ed2e080df40006979607"],
        "capsules": [],
        "payloads": ["5eb0e4bdb6c3bb0006eeb1eb"],
        "launchpad": "5e9e4502f35918c0803b262d",
        "cores": [
            {
                "core": "5e9e28a5f359187f273b2647",
                "flight": 1,
                "gridfins": True,
                "legs": True,
                "reused": False,
                "landing_attempt": True,
                "landing_success": True,
                "landing_type": "RTLS",
                "landpad": "5e9e3032383ecb267a34e7c7",
            },
            {
                "core": "5e9e28a5f3591823123b2648",
                "flight": 1,
                "gridfins": True,
                "legs": True,
                "reused": False,
                "landing_attempt": True,
                "landing_success": True,
                "landing_type": "RTLS",
                "landpad": "5e9e3032383ecb90a834e7c8",
            },
        ],
        "links": {
            "patch": {
                "small": "https://images2.imgbox.com/39/53/781qLqZ0_o.png",
                "large": "https://images2.imgbox.com/62/1e/I2f7Vf41_o.png",
            },
            "reddit": {
                "campaign": "https://www.reddit.com/r/spacex/comments/7tpuy7",
                "launch": "https://www.reddit.com/r/spacex/comments/7vcj18",
                "media": None,
            },
            "presskit": "http://www.spacex.com/sites/spacex/files/falconheavytestflightpresskit.pdf",
            "webcast": "https://www.youtube.com/watch?v=wbSwFU6tY1c",
            "youtube_id": "wbSwFU6tY1c",
            "article": "https://spaceflightnow.com/2018/02/06/falcon-heavy-demo-launch/",
            "wikipedia": "https://en.wikipedia.org/wiki/Falcon_Heavy_test_flight",
        },
        "auto_update": True,
    },
    {
        "id": "5eb87d46ffd86e000604b388",
        "flight_number": 94,
        "name": "CCtCap Demo Mission 2",
        "date_utc": "2020-05-30T19:22:00.000Z",
        "date_unix": 1590866520,
        "rocket": "5e9d0d95eda69973a809d1ec",
        "success": True,
        "upcoming": False,
        "details": "Crew Dragon Demo-2 carrying NASA astronauts Bob Behnken and Doug Hurley to ISS.",
        "failures": [],
        "crew": ["5ebf1a6e23a9a60006e03a7a", "5ebf1b7323a9a60006e03a7b"],
        "ships": ["5ea6ed2e080df40006979607"],
        "capsules": ["5e9e2c5df359188bfb3b2675"],
        "payloads": ["5eb0e4d0b6c3bb0006eeb253"],
        "launchpad": "5e9e4502f35918c0803b262d",
        "cores": [
            {
                "core": "5e9e28a6f3591835563b265d",
                "flight": 1,
                "gridfins": True,
                "legs": True,
                "reused": False,
                "landing_attempt": True,
                "landing_success": True,
                "landing_type": "ASDS",
                "landpad": "5e9e3032383ecb6bb234e7ca",
            }
        ],
        "links": {
            "patch": {
                "small": "https://images2.imgbox.com/ab/79/Wyc9KcpB_o.png",
                "large": "https://images2.imgbox.com/52/09/eRN9i8Dg_o.png",
            },
            "reddit": {
                "campaign": "https://www.reddit.com/r/spacex/comments/g8a1eg",
                "launch": "https://www.reddit.com/r/spacex/comments/gt1f12",
                "media": None,
            },
            "presskit": None,
            "webcast": "https://youtu.be/xY96v0OIcK0",
            "youtube_id": "xY96v0OIcK0",
            "article": "https://spaceflightnow.com/2020/05/30/nasa-astronauts-launch-from-us-soil-for-first-time-in-nine-years/",
            "wikipedia": "https://en.wikipedia.org/wiki/Crew_Dragon_Demo-2",
        },
        "auto_update": True,
    },
    {
        "id": "600f9a8d05eb594d41c32980",
        "flight_number": 130,
        "name": "Inspiration4",
        "date_utc": "2021-09-16T00:02:00.000Z",
        "date_unix": 1631750520,
        "rocket": "5e9d0d95eda69973a809d1ec",
        "success": True,
        "upcoming": False,
        "details": "First all-civilian orbital spaceflight mission.",
        "failures": [],
        "crew": ["607a37545a9634000662d558", "607a37545a9634000662d559"],
        "ships": ["5ea6ed2e080df40006979608"],
        "capsules": ["5e9e2c5df3591816f23b2676"],
        "payloads": ["607a37545a9634000662d55a"],
        "launchpad": "5e9e4502f35918c0803b262d",
        "cores": [
            {
                "core": "5e9e28a6f35918c0803b265e",
                "flight": 3,
                "gridfins": True,
                "legs": True,
                "reused": True,
                "landing_attempt": True,
                "landing_success": True,
                "landing_type": "ASDS",
                "landpad": "5e9e3033383ecbb9e534e7cc",
            }
        ],
        "links": {
            "patch": {
                "small": "https://images2.imgbox.com/39/53/781qLqZ0_o.png",
                "large": "https://images2.imgbox.com/62/1e/I2f7Vf41_o.png",
            },
            "reddit": {
                "campaign": "https://www.reddit.com/r/spacex/comments/p0x1q8",
                "launch": "https://www.reddit.com/r/spacex/comments/ppi40g",
                "media": None,
            },
            "presskit": None,
            "webcast": "https://youtu.be/3pv01sSq44w",
            "youtube_id": "3pv01sSq44w",
            "article": "https://spaceflightnow.com/2021/09/16/tourist-crew-blasts-off-on-historic-orbital-flight/",
            "wikipedia": "https://en.wikipedia.org/wiki/Inspiration4",
        },
        "auto_update": True,
    },
    {
        "id": "600f9a8d05eb594d41c32982",
        "flight_number": 150,
        "name": "Starlink Group 4-1",
        "date_utc": "2021-11-13T12:19:00.000Z",
        "date_unix": 1636805940,
        "rocket": "5e9d0d95eda69973a809d1ec",
        "success": True,
        "upcoming": False,
        "details": "Deployment of 53 Starlink broadband satellites to low Earth orbit.",
        "failures": [],
        "crew": [],
        "ships": ["5ea6ed2e080df40006979608"],
        "capsules": [],
        "payloads": ["607a37545a9634000662d55b"],
        "launchpad": "5e9e4501f3591823a93b2628",
        "cores": [
            {
                "core": "5e9e28a7f3591811563b265f",
                "flight": 9,
                "gridfins": True,
                "legs": True,
                "reused": True,
                "landing_attempt": True,
                "landing_success": True,
                "landing_type": "ASDS",
                "landpad": "5e9e3033383ecbb9e534e7cc",
            }
        ],
        "links": {
            "patch": {
                "small": "https://images2.imgbox.com/94/f2/NNfield7_o.png",
                "large": "https://images2.imgbox.com/40/e0/7Vlaakmr_o.png",
            },
            "reddit": {
                "campaign": None,
                "launch": None,
                "media": None,
            },
            "presskit": None,
            "webcast": "https://youtu.be/starlink41",
            "youtube_id": "starlink41",
            "article": "https://spaceflightnow.com/2021/11/13/starlink-4-1-launch/",
            "wikipedia": "https://en.wikipedia.org/wiki/Starlink",
        },
        "auto_update": True,
    },
    {
        "id": "65a3d0f005eb594d41c32999",
        "flight_number": 200,
        "name": "Starship Flight 5",
        "date_utc": "2024-10-13T12:25:00.000Z",
        "date_unix": 1728822300,
        "rocket": "5e9d0d96eda699382d09d1ee",
        "success": True,
        "upcoming": False,
        "details": "First historical catch of the Super Heavy booster by the Mechazilla launch tower chopstick arms.",
        "failures": [],
        "crew": [],
        "ships": [],
        "capsules": [],
        "payloads": [],
        "launchpad": "5e9e4502f3591855c03b262f",
        "cores": [
            {
                "core": "super_heavy_b12",
                "flight": 1,
                "gridfins": True,
                "legs": False,
                "reused": False,
                "landing_attempt": True,
                "landing_success": True,
                "landing_type": "Chopsticks",
                "landpad": "5e9e4502f3591855c03b262f",
            }
        ],
        "links": {
            "patch": {"small": None, "large": None},
            "reddit": {"campaign": None, "launch": None, "media": None},
            "presskit": None,
            "webcast": "https://x.com/SpaceX/status/starship-flight-5",
            "youtube_id": "starship-flight-5",
            "article": "https://spaceflightnow.com/2024/10/13/spacex-starship-flight-5/",
            "wikipedia": "https://en.wikipedia.org/wiki/Starship_flight_test_5",
        },
        "auto_update": True,
    },
    {
        "id": "65a3d0f005eb594d41c33001",
        "flight_number": 201,
        "name": "Starlink Group 6-50",
        "date_utc": "2026-10-01T15:00:00.000Z",
        "date_unix": 1790866800,
        "rocket": "5e9d0d95eda69973a809d1ec",
        "success": None,
        "upcoming": True,
        "details": "Future scheduled deployment mission for v2-mini Starlink satellites.",
        "failures": [],
        "crew": [],
        "ships": ["5ea6ed2e080df40006979607"],
        "capsules": [],
        "payloads": ["607a37545a9634000662d55b"],
        "launchpad": "5e9e4501f3591823a93b2628",
        "cores": [
            {
                "core": "5e9e28a7f3591811563b265f",
                "flight": 10,
                "gridfins": True,
                "legs": True,
                "reused": True,
                "landing_attempt": True,
                "landing_success": None,
                "landing_type": "ASDS",
                "landpad": "5e9e3032383ecb6bb234e7ca",
            }
        ],
        "links": {
            "patch": {"small": None, "large": None},
            "reddit": {"campaign": None, "launch": None, "media": None},
            "presskit": None,
            "webcast": None,
            "youtube_id": None,
            "article": None,
            "wikipedia": None,
        },
        "auto_update": True,
    },
]

DEFAULT_COMPANY: Dict[str, Any] = {
    "name": "SpaceX",
    "founder": "Elon Musk",
    "founded": 2002,
    "employees": 13000,
    "vehicles": 4,
    "launch_sites": 3,
    "test_sites": 3,
    "ceo": "Elon Musk",
    "cto": "Elon Musk",
    "coo": "Gwynne Shotwell",
    "cto_propulsion": "Tom Mueller",
    "valuation": 180000000000,
    "summary": "SpaceX designs, manufactures and launches advanced rockets and spacecraft.",
    "headquarters": {
        "address": "Rocket Road",
        "city": "Hawthorne",
        "state": "California",
    },
}


class SpaceXEngine:
    """In-memory data store and filtering/query evaluator."""

    def __init__(self) -> None:
        self.rockets = copy.deepcopy(DEFAULT_ROCKETS)
        self.launches = copy.deepcopy(DEFAULT_LAUNCHES)
        self.capsules = copy.deepcopy(DEFAULT_CAPSULES)
        self.crew = copy.deepcopy(DEFAULT_CREW)
        self.launchpads = copy.deepcopy(DEFAULT_LAUNCHPADS)
        self.ships = copy.deepcopy(DEFAULT_SHIPS)
        self.payloads = copy.deepcopy(DEFAULT_PAYLOADS)
        self.starlink = copy.deepcopy(DEFAULT_STARLINK)
        self.company = copy.deepcopy(DEFAULT_COMPANY)

    def get_collection(self, name: str) -> List[Dict[str, Any]]:
        """Retrieve dataset list by collection name."""
        mapping = {
            "rockets": self.rockets,
            "launches": self.launches,
            "capsules": self.capsules,
            "crew": self.crew,
            "launchpads": self.launchpads,
            "ships": self.ships,
            "payloads": self.payloads,
            "starlink": self.starlink,
        }
        if name not in mapping:
            raise ValidationError(f"Unknown collection: {name}")
        return mapping[name]

    def find_one(self, collection_name: str, item_id: str) -> Dict[str, Any]:
        """Locate single record by unique identifier."""
        collection = self.get_collection(collection_name)
        for item in collection:
            if item.get("id") == item_id:
                return copy.deepcopy(item)
        raise NotFoundError(
            f"{collection_name[:-1].capitalize()} with id '{item_id}' not found",
            resource_id=item_id,
        )

    def find_all(self, collection_name: str) -> List[Dict[str, Any]]:
        """Return all records in a collection."""
        return copy.deepcopy(self.get_collection(collection_name))

    def evaluate_filter(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Test document against query condition dictionary."""
        for field_path, criterion in query.items():
            val = self._extract_path(doc, field_path)
            if not self._match_criterion(val, criterion):
                return False
        return True

    def _extract_path(self, doc: Dict[str, Any], path: str) -> Any:
        parts = path.split(".")
        current: Any = doc
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def _match_criterion(self, value: Any, criterion: Any) -> bool:
        if isinstance(criterion, dict):
            for op, expected in criterion.items():
                if op == "$eq":
                    if value != expected:
                        return False
                elif op == "$ne":
                    if value == expected:
                        return False
                elif op == "$gt":
                    if value is None or value <= expected:
                        return False
                elif op == "$gte":
                    if value is None or value < expected:
                        return False
                elif op == "$lt":
                    if value is None or value >= expected:
                        return False
                elif op == "$lte":
                    if value is None or value > expected:
                        return False
                elif op == "$in":
                    if not isinstance(expected, (list, tuple, set)):
                        raise ValidationError("$in operator expects iterable")
                    if isinstance(value, list):
                        if not any(v in expected for v in value):
                            return False
                    elif value not in expected:
                        return False
                elif op == "$nin":
                    if not isinstance(expected, (list, tuple, set)):
                        raise ValidationError("$nin operator expects iterable")
                    if isinstance(value, list):
                        if any(v in expected for v in value):
                            return False
                    elif value in expected:
                        return False
                elif op == "$exists":
                    exists = value is not None
                    if exists != bool(expected):
                        return False
                elif op == "$regex":
                    if value is None:
                        return False
                    pattern = re.compile(str(expected))
                    if not pattern.search(str(value)):
                        return False
                else:
                    raise ValidationError(f"Unsupported query operator: {op}")
            return True
        if isinstance(value, list) and not isinstance(criterion, list):
            return criterion in value
        return value == criterion

    def execute_query(
        self,
        collection_name: str,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        target_cls: Optional[Type[T]] = None,
    ) -> QueryResult[Any]:
        """Perform filtered, sorted, paginated query on a collection."""
        raw_items = self.find_all(collection_name)
        active_query = query or {}
        active_opts = options or {}

        filtered = [
            item for item in raw_items
            if self.evaluate_filter(item, active_query)
        ]

        sort_spec = active_opts.get("sort")
        if sort_spec:
            filtered = self._apply_sort(filtered, sort_spec)

        populate_fields = active_opts.get("populate", [])
        if populate_fields:
            filtered = [
                self._populate_relations(item, populate_fields)
                for item in filtered
            ]

        select_fields = active_opts.get("select")
        if select_fields and isinstance(select_fields, list):
            filtered = [
                self._project_fields(item, select_fields)
                for item in filtered
            ]

        total_docs = len(filtered)
        limit = int(active_opts.get("limit", 10))
        if limit <= 0:
            limit = 10
        page = int(active_opts.get("page", 1))
        if page <= 0:
            page = 1

        offset = active_opts.get("offset")
        if offset is not None:
            start_idx = int(offset)
        else:
            start_idx = (page - 1) * limit

        end_idx = start_idx + limit
        paginated_items = filtered[start_idx:end_idx]

        total_pages = max(1, (total_docs + limit - 1) // limit)
        has_prev_page = page > 1 and page <= total_pages + 1
        has_next_page = page < total_pages
        prev_page = page - 1 if has_prev_page else None
        next_page = page + 1 if has_next_page else None
        paging_counter = start_idx + 1 if total_docs > 0 else 0

        instantiated_docs: List[Any] = []
        for item in paginated_items:
            if target_cls and hasattr(target_cls, "from_dict"):
                instantiated_docs.append(target_cls.from_dict(item))
            else:
                instantiated_docs.append(item)

        return QueryResult(
            docs=instantiated_docs,
            total_docs=total_docs,
            limit=limit,
            total_pages=total_pages,
            page=page,
            paging_counter=paging_counter,
            has_prev_page=has_prev_page,
            has_next_page=has_next_page,
            prev_page=prev_page,
            next_page=next_page,
        )

    def _apply_sort(
        self,
        items: List[Dict[str, Any]],
        sort_spec: Any,
    ) -> List[Dict[str, Any]]:
        if not isinstance(sort_spec, dict):
            return items
        sorted_items = list(items)
        for field_name, direction in reversed(list(sort_spec.items())):
            reverse = direction in (-1, "desc", "descending")

            def sort_key(doc: Dict[str, Any]) -> Tuple[int, Any]:
                val = self._extract_path(doc, field_name)
                if val is None:
                    return (1, "")
                return (0, val)

            sorted_items.sort(key=sort_key, reverse=reverse)
        return sorted_items

    def _populate_relations(
        self,
        doc: Dict[str, Any],
        populate_fields: List[str],
    ) -> Dict[str, Any]:
        enriched = copy.deepcopy(doc)
        for field_name in populate_fields:
            if field_name == "rocket" and isinstance(enriched.get("rocket"), str):
                try:
                    enriched["rocket"] = self.find_one("rockets", enriched["rocket"])
                except NotFoundError:
                    pass
            elif field_name == "launchpad" and isinstance(enriched.get("launchpad"), str):
                try:
                    enriched["launchpad"] = self.find_one("launchpads", enriched["launchpad"])
                except NotFoundError:
                    pass
            elif field_name == "crew" and isinstance(enriched.get("crew"), list):
                populated_crew = []
                for crew_id in enriched["crew"]:
                    if isinstance(crew_id, str):
                        try:
                            populated_crew.append(self.find_one("crew", crew_id))
                        except NotFoundError:
                            populated_crew.append(crew_id)
                    else:
                        populated_crew.append(crew_id)
                enriched["crew"] = populated_crew
            elif field_name == "payloads" and isinstance(enriched.get("payloads"), list):
                populated_payloads = []
                for p_id in enriched["payloads"]:
                    if isinstance(p_id, str):
                        try:
                            populated_payloads.append(self.find_one("payloads", p_id))
                        except NotFoundError:
                            populated_payloads.append(p_id)
                    else:
                        populated_payloads.append(p_id)
                enriched["payloads"] = populated_payloads
            elif field_name == "ships" and isinstance(enriched.get("ships"), list):
                populated_ships = []
                for s_id in enriched["ships"]:
                    if isinstance(s_id, str):
                        try:
                            populated_ships.append(self.find_one("ships", s_id))
                        except NotFoundError:
                            populated_ships.append(s_id)
                    else:
                        populated_ships.append(s_id)
                enriched["ships"] = populated_ships
        return enriched

    def _project_fields(
        self,
        doc: Dict[str, Any],
        select_fields: List[str],
    ) -> Dict[str, Any]:
        projected = {"id": doc.get("id")}
        for f in select_fields:
            if f in doc:
                projected[f] = doc[f]
        return projected
