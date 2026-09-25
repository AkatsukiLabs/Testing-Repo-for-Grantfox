"""Type definitions and dataclasses for SpaceX resources."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Dimension:
    """Measurement representing length, diameter, or height."""

    meters: Optional[float] = None
    feet: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Dimension":
        """Construct Dimension from dictionary payload."""
        if not data:
            return cls()
        return cls(
            meters=data.get("meters"),
            feet=data.get("feet"),
        )


@dataclass
class Mass:
    """Measurement representing object mass."""

    kg: Optional[float] = None
    lb: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Mass":
        """Construct Mass from dictionary payload."""
        if not data:
            return cls()
        return cls(
            kg=data.get("kg"),
            lb=data.get("lb"),
        )


@dataclass
class Thrust:
    """Measurement representing rocket engine thrust."""

    kN: Optional[float] = None
    lbf: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Thrust":
        """Construct Thrust from dictionary payload."""
        if not data:
            return cls()
        return cls(
            kN=data.get("kN"),
            lbf=data.get("lbf"),
        )


@dataclass
class EngineSpec:
    """Rocket propulsion specifications."""

    number: int = 0
    type: str = ""
    version: str = ""
    layout: Optional[str] = None
    loss_max: Optional[int] = None
    propellant_1: str = ""
    propellant_2: str = ""
    thrust_sea_level: Thrust = field(default_factory=Thrust)
    thrust_vacuum: Thrust = field(default_factory=Thrust)
    thrust_to_weight: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "EngineSpec":
        """Construct EngineSpec from dictionary payload."""
        if not data:
            return cls()
        return cls(
            number=data.get("number", 0),
            type=data.get("type", ""),
            version=data.get("version", ""),
            layout=data.get("layout"),
            loss_max=data.get("loss_max"),
            propellant_1=data.get("propellant_1", ""),
            propellant_2=data.get("propellant_2", ""),
            thrust_sea_level=Thrust.from_dict(data.get("thrust_sea_level")),
            thrust_vacuum=Thrust.from_dict(data.get("thrust_vacuum")),
            thrust_to_weight=data.get("thrust_to_weight"),
        )


@dataclass
class FirstStageSpec:
    """First stage technical specifications."""

    reusable: bool = False
    engines: int = 0
    fuel_amount_tons: float = 0.0
    burn_time_sec: Optional[int] = None
    thrust_sea_level: Thrust = field(default_factory=Thrust)
    thrust_vacuum: Thrust = field(default_factory=Thrust)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "FirstStageSpec":
        """Construct FirstStageSpec from dictionary payload."""
        if not data:
            return cls()
        return cls(
            reusable=data.get("reusable", False),
            engines=data.get("engines", 0),
            fuel_amount_tons=data.get("fuel_amount_tons", 0.0),
            burn_time_sec=data.get("burn_time_sec"),
            thrust_sea_level=Thrust.from_dict(data.get("thrust_sea_level")),
            thrust_vacuum=Thrust.from_dict(data.get("thrust_vacuum")),
        )


@dataclass
class SecondStageSpec:
    """Second stage technical specifications."""

    reusable: bool = False
    engines: int = 0
    fuel_amount_tons: float = 0.0
    burn_time_sec: Optional[int] = None
    thrust: Thrust = field(default_factory=Thrust)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "SecondStageSpec":
        """Construct SecondStageSpec from dictionary payload."""
        if not data:
            return cls()
        return cls(
            reusable=data.get("reusable", False),
            engines=data.get("engines", 0),
            fuel_amount_tons=data.get("fuel_amount_tons", 0.0),
            burn_time_sec=data.get("burn_time_sec"),
            thrust=Thrust.from_dict(data.get("thrust")),
        )


@dataclass
class Rocket:
    """Launch vehicle specifications and capabilities."""

    id: str
    name: str
    type: str
    active: bool
    stages: int
    boosters: int
    cost_per_launch: int
    success_rate_pct: int
    first_flight: str
    country: str
    company: str
    wikipedia: str
    description: str
    height: Dimension = field(default_factory=Dimension)
    diameter: Dimension = field(default_factory=Dimension)
    mass: Mass = field(default_factory=Mass)
    engines: EngineSpec = field(default_factory=EngineSpec)
    first_stage: FirstStageSpec = field(default_factory=FirstStageSpec)
    second_stage: SecondStageSpec = field(default_factory=SecondStageSpec)
    flickr_images: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Rocket":
        """Construct Rocket from dictionary payload."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", ""),
            active=data.get("active", False),
            stages=data.get("stages", 0),
            boosters=data.get("boosters", 0),
            cost_per_launch=data.get("cost_per_launch", 0),
            success_rate_pct=data.get("success_rate_pct", 0),
            first_flight=data.get("first_flight", ""),
            country=data.get("country", ""),
            company=data.get("company", ""),
            wikipedia=data.get("wikipedia", ""),
            description=data.get("description", ""),
            height=Dimension.from_dict(data.get("height")),
            diameter=Dimension.from_dict(data.get("diameter")),
            mass=Mass.from_dict(data.get("mass")),
            engines=EngineSpec.from_dict(data.get("engines")),
            first_stage=FirstStageSpec.from_dict(data.get("first_stage")),
            second_stage=SecondStageSpec.from_dict(data.get("second_stage")),
            flickr_images=data.get("flickr_images", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert rocket instance into serialized dictionary."""
        return asdict(self)


@dataclass
class Core:
    """Launch core usage and recovery metrics."""

    core_id: Optional[str] = None
    flight: Optional[int] = None
    gridfins: Optional[bool] = None
    legs: Optional[bool] = None
    reused: Optional[bool] = None
    landing_attempt: Optional[bool] = None
    landing_success: Optional[bool] = None
    landing_type: Optional[str] = None
    landpad: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Core":
        """Construct Core from dictionary payload."""
        if not data:
            return cls()
        return cls(
            core_id=data.get("core"),
            flight=data.get("flight"),
            gridfins=data.get("gridfins"),
            legs=data.get("legs"),
            reused=data.get("reused"),
            landing_attempt=data.get("landing_attempt"),
            landing_success=data.get("landing_success"),
            landing_type=data.get("landing_type"),
            landpad=data.get("landpad"),
        )


@dataclass
class FailureDetail:
    """Launch failure diagnostic record."""

    time: Optional[int] = None
    altitude: Optional[int] = None
    reason: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailureDetail":
        """Construct FailureDetail from dictionary payload."""
        return cls(
            time=data.get("time"),
            altitude=data.get("altitude"),
            reason=data.get("reason", ""),
        )


@dataclass
class LaunchLinks:
    """External URLs and media assets associated with a launch."""

    patch_small: Optional[str] = None
    patch_large: Optional[str] = None
    reddit_campaign: Optional[str] = None
    reddit_launch: Optional[str] = None
    reddit_media: Optional[str] = None
    presskit: Optional[str] = None
    webcast: Optional[str] = None
    youtube_id: Optional[str] = None
    article: Optional[str] = None
    wikipedia: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "LaunchLinks":
        """Construct LaunchLinks from dictionary payload."""
        if not data:
            return cls()
        patch = data.get("patch") or {}
        reddit = data.get("reddit") or {}
        return cls(
            patch_small=patch.get("small"),
            patch_large=patch.get("large"),
            reddit_campaign=reddit.get("campaign"),
            reddit_launch=reddit.get("launch"),
            reddit_media=reddit.get("media"),
            presskit=data.get("presskit"),
            webcast=data.get("webcast"),
            youtube_id=data.get("youtube_id"),
            article=data.get("article"),
            wikipedia=data.get("wikipedia"),
        )


@dataclass
class Launch:
    """Orbital mission and launch event metadata."""

    id: str
    flight_number: int
    name: str
    date_utc: str
    date_unix: int
    rocket: Any
    success: Optional[bool]
    upcoming: bool
    details: Optional[str] = None
    failures: List[FailureDetail] = field(default_factory=list)
    crew: List[Any] = field(default_factory=list)
    ships: List[Any] = field(default_factory=list)
    capsules: List[Any] = field(default_factory=list)
    payloads: List[Any] = field(default_factory=list)
    launchpad: Any = None
    cores: List[Core] = field(default_factory=list)
    links: LaunchLinks = field(default_factory=LaunchLinks)
    auto_update: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Launch":
        """Construct Launch from dictionary payload."""
        failures = [
            FailureDetail.from_dict(f) for f in data.get("failures", [])
        ]
        cores = [Core.from_dict(c) for c in data.get("cores", [])]
        links = LaunchLinks.from_dict(data.get("links"))
        return cls(
            id=data.get("id", ""),
            flight_number=data.get("flight_number", 0),
            name=data.get("name", ""),
            date_utc=data.get("date_utc", ""),
            date_unix=data.get("date_unix", 0),
            rocket=data.get("rocket"),
            success=data.get("success"),
            upcoming=data.get("upcoming", False),
            details=data.get("details"),
            failures=failures,
            crew=data.get("crew", []),
            ships=data.get("ships", []),
            capsules=data.get("capsules", []),
            payloads=data.get("payloads", []),
            launchpad=data.get("launchpad"),
            cores=cores,
            links=links,
            auto_update=data.get("auto_update", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert launch instance into serialized dictionary."""
        return asdict(self)


@dataclass
class Capsule:
    """Dragon spacecraft pressure vessel record."""

    id: str
    serial: str
    status: str
    type: str
    dragon: str
    reuse_count: int
    water_landings: int
    land_landings: int
    last_update: Optional[str] = None
    launches: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Capsule":
        """Construct Capsule from dictionary payload."""
        return cls(
            id=data.get("id", ""),
            serial=data.get("serial", ""),
            status=data.get("status", ""),
            type=data.get("type", ""),
            dragon=data.get("dragon", ""),
            reuse_count=data.get("reuse_count", 0),
            water_landings=data.get("water_landings", 0),
            land_landings=data.get("land_landings", 0),
            last_update=data.get("last_update"),
            launches=data.get("launches", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert capsule instance into serialized dictionary."""
        return asdict(self)


@dataclass
class CrewMember:
    """Astronaut identity and flight manifest record."""

    id: str
    name: str
    agency: str
    image: Optional[str] = None
    wikipedia: Optional[str] = None
    status: str = "active"
    launches: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrewMember":
        """Construct CrewMember from dictionary payload."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            agency=data.get("agency", ""),
            image=data.get("image"),
            wikipedia=data.get("wikipedia"),
            status=data.get("status", "active"),
            launches=data.get("launches", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert crew member instance into serialized dictionary."""
        return asdict(self)


@dataclass
class Launchpad:
    """Terrestrial launch facility infrastructure."""

    id: str
    name: str
    full_name: str
    status: str
    locality: str
    region: str
    timezone: str
    latitude: float
    longitude: float
    launch_attempts: int
    launch_successes: int
    rockets: List[str] = field(default_factory=list)
    launches: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Launchpad":
        """Construct Launchpad from dictionary payload."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            status=data.get("status", ""),
            locality=data.get("locality", ""),
            region=data.get("region", ""),
            timezone=data.get("timezone", ""),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            launch_attempts=data.get("launch_attempts", 0),
            launch_successes=data.get("launch_successes", 0),
            rockets=data.get("rockets", []),
            launches=data.get("launches", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert launchpad instance into serialized dictionary."""
        return asdict(self)


@dataclass
class Ship:
    """Autonomous drone ship, tug, or recovery vessel."""

    id: str
    name: str
    type: str
    active: bool
    roles: List[str] = field(default_factory=list)
    home_port: str = ""
    status: Optional[str] = None
    imo: Optional[int] = None
    mmsi: Optional[int] = None
    abs_number: Optional[int] = None
    class_type: Optional[int] = None
    mass_kg: Optional[float] = None
    mass_lbs: Optional[float] = None
    year_built: Optional[int] = None
    speed_kn: Optional[float] = None
    course_deg: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    link: Optional[str] = None
    image: Optional[str] = None
    launches: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ship":
        """Construct Ship from dictionary payload."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", ""),
            active=data.get("active", False),
            roles=data.get("roles", []),
            home_port=data.get("home_port", ""),
            status=data.get("status"),
            imo=data.get("imo"),
            mmsi=data.get("mmsi"),
            abs_number=data.get("abs"),
            class_type=data.get("class"),
            mass_kg=data.get("mass_kg"),
            mass_lbs=data.get("mass_lbs"),
            year_built=data.get("year_built"),
            speed_kn=data.get("speed_kn"),
            course_deg=data.get("course_deg"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            link=data.get("link"),
            image=data.get("image"),
            launches=data.get("launches", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ship instance into serialized dictionary."""
        return asdict(self)


@dataclass
class Payload:
    """Satellite, spacecraft, or instrumentation payload."""

    id: str
    name: str
    type: str
    reused: bool
    launch: Optional[str]
    customers: List[str] = field(default_factory=list)
    nationalities: List[str] = field(default_factory=list)
    manufacturers: List[str] = field(default_factory=list)
    mass_kg: Optional[float] = None
    mass_lbs: Optional[float] = None
    orbit: str = ""
    reference_system: str = ""
    regime: str = ""
    semi_major_axis_km: Optional[float] = None
    eccentricity: Optional[float] = None
    periapsis_km: Optional[float] = None
    apoapsis_km: Optional[float] = None
    inclination_deg: Optional[float] = None
    period_min: Optional[float] = None
    lifespan_years: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payload":
        """Construct Payload from dictionary payload."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", ""),
            reused=data.get("reused", False),
            launch=data.get("launch"),
            customers=data.get("customers", []),
            nationalities=data.get("nationalities", []),
            manufacturers=data.get("manufacturers", []),
            mass_kg=data.get("mass_kg"),
            mass_lbs=data.get("mass_lbs"),
            orbit=data.get("orbit", ""),
            reference_system=data.get("reference_system", ""),
            regime=data.get("regime", ""),
            semi_major_axis_km=data.get("semi_major_axis_km"),
            eccentricity=data.get("eccentricity"),
            periapsis_km=data.get("periapsis_km"),
            apoapsis_km=data.get("apoapsis_km"),
            inclination_deg=data.get("inclination_deg"),
            period_min=data.get("period_min"),
            lifespan_years=data.get("lifespan_years"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert payload instance into serialized dictionary."""
        return asdict(self)


@dataclass
class Starlink:
    """Broadband constellation satellite telemetric record."""

    id: str
    version: str
    launch: Optional[str]
    norad_id: Optional[int] = None
    epoch: Optional[str] = None
    mean_motion: Optional[float] = None
    eccentricity: Optional[float] = None
    inclination_deg: Optional[float] = None
    raan_deg: Optional[float] = None
    arg_of_pericenter_deg: Optional[float] = None
    mean_anomaly_deg: Optional[float] = None
    bstar: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    height_km: Optional[float] = None
    velocity_kms: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Starlink":
        """Construct Starlink from dictionary payload."""
        space_track = data.get("spaceTrack") or {}
        return cls(
            id=data.get("id", ""),
            version=data.get("version", ""),
            launch=data.get("launch"),
            norad_id=space_track.get("NORAD_CAT_ID"),
            epoch=space_track.get("EPOCH"),
            mean_motion=space_track.get("MEAN_MOTION"),
            eccentricity=space_track.get("ECCENTRICITY"),
            inclination_deg=space_track.get("INCLINATION"),
            raan_deg=space_track.get("RA_OF_ASC_NODE"),
            arg_of_pericenter_deg=space_track.get("ARG_OF_PERICENTER"),
            mean_anomaly_deg=space_track.get("MEAN_ANOMALY"),
            bstar=space_track.get("BSTAR"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            height_km=data.get("height_km"),
            velocity_kms=data.get("velocity_kms"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Starlink instance into serialized dictionary."""
        return asdict(self)


@dataclass
class CompanyInfo:
    """SpaceX corporate headquarters and operational summary."""

    name: str
    founder: str
    founded: int
    employees: int
    vehicles: int
    launch_sites: int
    test_sites: int
    ceo: str
    cto: str
    coo: str
    cto_propulsion: str
    valuation: int
    summary: str
    headquarters_address: str
    headquarters_city: str
    headquarters_state: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompanyInfo":
        """Construct CompanyInfo from dictionary payload."""
        headquarters = data.get("headquarters") or {}
        return cls(
            name=data.get("name", "SpaceX"),
            founder=data.get("founder", "Elon Musk"),
            founded=data.get("founded", 2002),
            employees=data.get("employees", 13000),
            vehicles=data.get("vehicles", 4),
            launch_sites=data.get("launch_sites", 3),
            test_sites=data.get("test_sites", 3),
            ceo=data.get("ceo", "Elon Musk"),
            cto=data.get("cto", "Elon Musk"),
            coo=data.get("coo", "Gwynne Shotwell"),
            cto_propulsion=data.get("cto_propulsion", "Tom Mueller"),
            valuation=data.get("valuation", 180000000000),
            summary=data.get("summary", ""),
            headquarters_address=headquarters.get("address", "Rocket Road"),
            headquarters_city=headquarters.get("city", "Hawthorne"),
            headquarters_state=headquarters.get("state", "California"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert CompanyInfo instance into serialized dictionary."""
        return asdict(self)


@dataclass
class QueryResult(Generic[T]):
    """Paginated collection returned by query operations."""

    docs: List[T]
    total_docs: int
    limit: int
    total_pages: int
    page: int
    paging_counter: int
    has_prev_page: bool
    has_next_page: bool
    prev_page: Optional[int]
    next_page: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert query result into serialized dictionary."""
        serialized_docs = []
        for doc in self.docs:
            if hasattr(doc, "to_dict"):
                serialized_docs.append(doc.to_dict())
            else:
                serialized_docs.append(doc)
        return {
            "docs": serialized_docs,
            "totalDocs": self.total_docs,
            "limit": self.limit,
            "totalPages": self.total_pages,
            "page": self.page,
            "pagingCounter": self.paging_counter,
            "hasPrevPage": self.has_prev_page,
            "hasNextPage": self.has_next_page,
            "prevPage": self.prev_page,
            "nextPage": self.next_page,
        }
