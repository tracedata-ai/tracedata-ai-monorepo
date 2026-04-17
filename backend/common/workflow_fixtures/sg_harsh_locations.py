"""50-entry Singapore harsh event location pool with weights."""

from __future__ import annotations

import random

# (lat, lon, place_name, weight)
# weight: 1.0 = nominal, 2.0–3.0 = known accident blackspot
_BASE_LOCATIONS: list[tuple[float, float, str, float]] = [
    # Expressway interchanges
    (1.3521, 103.8198, "PIE/CTE interchange, Toa Payoh", 3.0),
    (1.3380, 103.7060, "AYE/PIE interchange, Jurong West", 2.5),
    (1.3690, 103.8480, "CTE/SLE interchange, Ang Mo Kio", 2.5),
    (1.4390, 103.8360, "Woodlands Checkpoint approach, SLE", 3.0),
    (1.3220, 103.9280, "ECP/KPE interchange, Kallang", 2.0),
    (1.3030, 103.8320, "MCE/ECP merge, Marina South", 2.0),
    (1.3310, 103.7460, "BKE/PIE interchange, Bukit Timah", 2.5),
    (1.3800, 103.7480, "KJE/BKE interchange, Kranji", 2.0),
    (1.3920, 103.9990, "TPE/SLE interchange, Punggol", 2.0),
    (1.3250, 103.9050, "PIE/KPE interchange, Paya Lebar", 2.5),
    # Signalised heavy junctions
    (1.3230, 103.7080, "Jurong Town Hall Rd / Jurong Port Rd junction", 2.0),
    (1.3360, 103.7220, "Boon Lay Way / Pioneer Rd junction", 1.5),
    (1.3080, 103.8200, "Havelock Rd / River Valley Rd junction", 1.5),
    (1.2970, 103.8540, "Shenton Way / Robinson Rd junction, CBD", 2.0),
    (1.3140, 103.8990, "Paya Lebar Rd / Geylang Rd junction", 2.0),
    (1.3540, 103.8680, "Upper Serangoon Rd / Hougang Ave 3 junction", 1.5),
    (1.3870, 103.7460, "Choa Chu Kang Rd / Bukit Batok Rd junction", 1.5),
    (1.3440, 103.7310, "Jurong East Ave 1 / International Rd junction", 1.5),
    (1.3760, 103.8450, "Ang Mo Kio Ave 3 / Yio Chu Kang Rd junction", 1.5),
    (1.4230, 103.7980, "Woodlands Ave 12 / Marsiling Rd junction", 1.5),
    # Cargo/logistics hub approaches
    (1.2990, 103.6360, "Tuas Checkpoint / Tuas Ave 1 approach", 3.0),
    (1.2870, 103.6480, "Tuas South Ave 3 industrial zone", 2.0),
    (1.3360, 103.9580, "Changi Cargo Rd / Airport Boulevard junction", 2.5),
    (1.3180, 103.9700, "Changi Business Park / Upper Changi Rd junction", 1.5),
    (1.2580, 103.8190, "PSA HarbourFront / Telok Blangah Rd approach", 2.0),
    (1.2720, 103.7990, "Keppel Rd / Kampong Bahru Rd junction", 2.0),
    (1.3480, 103.7130, "Jurong Port Rd / Pandan Rd junction", 2.5),
    (1.3310, 103.9620, "Loyang Ave / Pasir Ris industrial approach", 1.5),
    (1.3400, 103.7100, "Tuas Rd / Pioneer Rd North junction", 1.5),
    (1.3750, 103.9550, "Pasir Ris Dr 12 / Tampines Ave 10 junction", 1.5),
    # Expressway on/off ramps — high braking frequency
    (1.3490, 103.8390, "CTE Exit 5 ramp, Braddell Rd", 2.0),
    (1.3280, 103.8450, "PIE Exit 27 ramp, Thomson Rd", 2.0),
    (1.3050, 103.9060, "ECP Exit 5 ramp, Tanjong Katong Rd", 2.0),
    (1.3370, 103.7080, "AYE Exit 8 ramp, Clementi Rd", 2.0),
    (1.4050, 103.7960, "SLE Exit 7 ramp, Mandai Rd", 2.0),
    (1.3600, 103.9950, "TPE Exit 4 ramp, Tampines Ave 5", 1.5),
    (1.3030, 103.8200, "MCE Exit 1 ramp, Anson Rd", 1.5),
    (1.2960, 103.7760, "AYE Exit 2 ramp, West Coast Rd", 1.5),
    (1.3210, 103.8740, "KPE Exit 2 ramp, Macpherson Rd", 1.5),
    (1.3690, 103.8980, "TPE Exit 1 ramp, Hougang Ave 8", 1.5),
    # Industrial district slow-zone approaches
    (1.3300, 103.7060, "International Rd / Benoi Rd junction", 1.0),
    (1.3150, 103.7610, "Clementi Ave 6 / Commonwealth Ave West junction", 1.0),
    (1.3560, 103.9180, "Tampines Industrial Pk A / Tampines Ave 1 junction", 1.0),
    (1.3810, 103.7830, "Choa Chu Kang Loop / Tech Park Crescent junction", 1.0),
    (1.2840, 103.8380, "Alexandra Rd / Queensway junction", 1.0),
    (1.3190, 103.8610, "Kallang Ave / Lavender St junction", 1.0),
    (1.3470, 103.8940, "Bartley Rd / Upper Paya Lebar Rd junction", 1.0),
    (1.3920, 103.8450, "Yio Chu Kang Rd / Seletar Aerospace Dr junction", 1.0),
    (1.3040, 103.7540, "West Coast Hwy / AYE service rd junction", 1.0),
    (1.2910, 103.7900, "Pasir Panjang Rd / South Buona Vista Rd junction", 1.0),
]

HARSH_LOCATION_POOL: list[tuple[float, float, str, float]] = _BASE_LOCATIONS
_WEIGHTS: list[float] = [e[3] for e in _BASE_LOCATIONS]


def pick_sg_harsh_location(rng: random.Random) -> tuple[float, float, str]:
    """Weighted random pick. Returns (lat, lon, place_name) with ~77m jitter."""
    lat, lon, place_name, _ = rng.choices(_BASE_LOCATIONS, weights=_WEIGHTS, k=1)[0]
    return (
        round(lat + rng.uniform(-0.0007, 0.0007), 6),
        round(lon + rng.uniform(-0.0007, 0.0007), 6),
        place_name,
    )
