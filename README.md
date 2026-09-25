# Testing-Repo-for-Grantfox
Just for testing
Esto es una prueba

Esto es una contribucion en grantfox

test final

---

## SpaceX Python SDK & Spaceflight Mechanics Toolkit

Production-grade SpaceX API client, local deterministic flight execution engine, and spaceflight astrodynamics toolkit for Python.

### Features

- **Fleet Specifications**: Detailed vehicle profiles for Falcon 1, Falcon 9, Falcon Heavy, and Starship / Super Heavy.
- **Flight Manifests**: Historical launches (Flight 1 FalconSat, Flight 20 OG-2 RTLS landing, Flight 55 Falcon Heavy Starman, Flight 94 Demo-2, Flight 130 Inspiration4, Flight 150 Starlink, Flight 200 Starship Flight 5 catch).
- **Dragon Spacecraft & Crew**: Pressure vessel capsule statuses, reuse statistics, water landing counts, and astronaut manifests.
- **Infrastructure & Fleet**: Launchpads (SLC-40, LC-39A, SLC-4E, Starbase) and autonomous spaceport droneships (OCISLY, JRTI).
- **Orbital Astrodynamics**: Closed-form orbital velocity, Keplerian periods, Tsiolkovsky rocket equation delta-v, escape velocity, apoapsis/periapsis calculations, and Hohmann transfer delta-v.
- **Query Engine**: MongoDB-style query operators (`$eq`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$regex`), dot-notation paths, sorting, pagination, and relational population (`populate: ["rocket", "launchpad", "crew"]`).
- **Standard Library Only**: Zero third-party dependencies required.

### Quickstart

```python
from spacex import SpaceX, calculate_orbital_velocity, calculate_tsiolkovsky_delta_v

# Initialize client (offline mode enabled by default for deterministic local execution)
client = SpaceX()

# Inspect rocket vehicle specifications
f9 = client.rockets.get("5e9d0d95eda69973a809d1ec")
print(f"Vehicle: {f9.name}, Engines: {f9.engines.number}x {f9.engines.type}")

# Retrieve the latest completed flight
latest = client.launches.latest()
print(f"Latest Mission: {latest.name} (Flight #{latest.flight_number})")

# Query missions with relational population
result = client.launches.query(
    query={"flight_number": 94},
    options={"populate": ["rocket", "launchpad", "crew"]}
)
mission = result.docs[0]
print(f"Rocket: {mission.rocket['name']}, Launchpad: {mission.launchpad['name']}")

# Astrodynamics & Rocket Equations
v_orbit = calculate_orbital_velocity(altitude_km=400.0)
print(f"ISS Orbital Velocity: {v_orbit:.1f} m/s")

dv = calculate_tsiolkovsky_delta_v(dry_mass_kg=22200, propellant_mass_kg=395700, isp_sec=311)
print(f"Falcon 9 Stage 1 Delta-v: {dv:.1f} m/s")
```

### Running Tests

Execute the unit test suite with Python's built-in test runner:

```bash
python3 -m unittest discover -s tests -v
```

Or using `pytest`:

```bash
pytest -v
```
