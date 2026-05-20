"""
Fictional tactical data for SDDS demo.
Centered on a Kashmir-like highland terrain at approximately [75.5, 34.0].
All coordinates are [longitude, latitude] in WGS84 decimal degrees.
All zones, routes, and names are entirely fictional.
"""

TACTICAL_DATA = {
    "map_center": [75.5, 34.0],
    "map_zoom": 12,

    "zones": {
        "ALPHA_BASE": {
            "id": "ALPHA_BASE",
            "name": "ALPHA BASE",
            "type": "friendly",
            "description": "Forward Operating Base. Friendly forces, command element, and logistics.",
            "center": [75.52, 33.95],
            "polygon": [
                [75.49, 33.93], [75.55, 33.93],
                [75.55, 33.97], [75.49, 33.97],
                [75.49, 33.93]
            ],
            "color": "green"
        },
        "BRAVO_CAMP": {
            "id": "BRAVO_CAMP",
            "name": "BRAVO CAMP",
            "type": "hostile",
            "description": "Suspected enemy staging area. NW highland position with concealment advantage.",
            "center": [75.41, 34.09],
            "polygon": [
                [75.38, 34.07], [75.44, 34.07],
                [75.44, 34.11], [75.38, 34.11],
                [75.38, 34.07]
            ],
            "color": "red"
        },
        "CHARLIE_DEPOT": {
            "id": "CHARLIE_DEPOT",
            "name": "CHARLIE DEPOT",
            "type": "neutral",
            "description": "Forward supply depot. Ammunition and rations. Lightly defended.",
            "center": [75.58, 34.055],
            "polygon": [
                [75.56, 34.04], [75.60, 34.04],
                [75.60, 34.07], [75.56, 34.07],
                [75.56, 34.04]
            ],
            "color": "amber"
        },
        "DELTA_OP": {
            "id": "DELTA_OP",
            "name": "DELTA OP",
            "type": "friendly",
            "description": "Observation post on central ridge. Overlooks valley approaches and BRAVO.",
            "center": [75.465, 34.0],
            "polygon": [
                [75.455, 33.99], [75.475, 33.99],
                [75.475, 34.01], [75.455, 34.01],
                [75.455, 33.99]
            ],
            "color": "green"
        },
        "OPC_1": {
            "id": "OPC_1",
            "name": "OPC-1 NORTH RIDGE",
            "type": "camping",
            "description": "Op camping zone. North ridge position. High concealment. Good overwatch of BRAVO CAMP. Accessible via ROUTE FALCON.",
            "center": [75.43, 34.06],
            "polygon": [
                [75.415, 34.0475], [75.445, 34.0475],
                [75.445, 34.0725], [75.415, 34.0725],
                [75.415, 34.0475]
            ],
            "color": "cyan"
        },
        "OPC_2": {
            "id": "OPC_2",
            "name": "OPC-2 EAST RIDGE",
            "type": "camping",
            "description": "Op camping zone. East ridge. Good fallback position near CHARLIE DEPOT. Accessible via ROUTE COBRA.",
            "center": [75.54, 34.03],
            "polygon": [
                [75.5275, 34.02], [75.5525, 34.02],
                [75.5525, 34.04], [75.5275, 34.04],
                [75.5275, 34.02]
            ],
            "color": "cyan"
        },
        "OPC_3": {
            "id": "OPC_3",
            "name": "OPC-3 NORTH HEIGHTS",
            "type": "camping",
            "description": "Op camping zone. Remote north heights. Full valley overview. High elevation. Difficult access.",
            "center": [75.46, 34.12],
            "polygon": [
                [75.4425, 34.1075], [75.4775, 34.1075],
                [75.4775, 34.1325], [75.4425, 34.1325],
                [75.4425, 34.1075]
            ],
            "color": "cyan"
        }
    },

    "routes": {
        "MSR_TIGER": {
            "id": "MSR_TIGER",
            "name": "MSR TIGER",
            "type": "main_supply",
            "description": "Main Supply Route. Paved road through valley floor. Fastest route but most exposed. High vehicle traffic.",
            "coords": [
                [75.52, 33.95], [75.50, 33.98],
                [75.48, 34.00], [75.45, 34.03],
                [75.41, 34.09]
            ],
            "color": "amber"
        },
        "ROUTE_COBRA": {
            "id": "ROUTE_COBRA",
            "name": "ROUTE COBRA",
            "type": "alternate",
            "description": "Mountain pass route. Longer but avoids valley exposure. Difficult terrain. Suitable for vehicles with high clearance.",
            "coords": [
                [75.52, 33.95], [75.55, 33.99],
                [75.58, 34.02], [75.58, 34.055],
                [75.55, 34.08], [75.50, 34.10],
                [75.41, 34.09]
            ],
            "color": "amber"
        },
        "ROUTE_FALCON": {
            "id": "ROUTE_FALCON",
            "name": "ROUTE FALCON",
            "type": "covert",
            "description": "Covert mountain trail. Foot traffic only. Maximum concealment. Leads directly to OPC-1 NORTH RIDGE.",
            "coords": [
                [75.52, 33.95], [75.50, 34.01],
                [75.47, 34.04], [75.43, 34.06]
            ],
            "color": "cyan"
        },
        "SUPPLY_DELTA": {
            "id": "SUPPLY_DELTA",
            "name": "SUPPLY LINE DELTA",
            "type": "supply",
            "description": "Direct supply line from ALPHA BASE to CHARLIE DEPOT. Secondary road.",
            "coords": [
                [75.52, 33.95], [75.55, 33.99],
                [75.58, 34.055]
            ],
            "color": "amber"
        }
    },

    "landmarks": [
        {
            "id": "KILO_BRIDGE",
            "name": "KILO BRIDGE",
            "coords": [75.495, 33.98],
            "description": "River crossing. Critical chokepoint on MSR TIGER."
        },
        {
            "id": "RIDGELINE_SIERRA",
            "name": "RIDGELINE SIERRA",
            "coords": [75.46, 34.05],
            "description": "Dominant high ground. Controls observation of entire valley."
        },
        {
            "id": "RIVER_ZANSKAR",
            "name": "RIVER ZANSKAR",
            "coords": [
                [75.38, 33.92], [75.45, 33.97],
                [75.52, 34.02], [75.58, 34.10]
            ],
            "description": "Major river. Runs SW to NE. Restricts cross-country movement."
        }
    ]
}


def get_map_data() -> dict:
    return TACTICAL_DATA


def get_system_context() -> str:
    """Return a compact text description of the AO for the LLM system prompt."""
    return """
=== AREA OF OPERATIONS (AO) ===
Fictional highland conflict zone. Coordinates: [longitude, latitude] WGS84.

--- FRIENDLY ZONES ---
ALPHA BASE (Forward Operating Base)
  Center: [75.52, 33.95]
  Polygon: [[75.49,33.93],[75.55,33.93],[75.55,33.97],[75.49,33.97],[75.49,33.93]]

DELTA OP (Observation Post — central ridge)
  Center: [75.465, 34.0]
  Polygon: [[75.455,33.99],[75.475,33.99],[75.475,34.01],[75.455,34.01],[75.455,33.99]]

--- HOSTILE ZONES ---
BRAVO CAMP (Enemy Staging Area — NW highlands)
  Center: [75.41, 34.09]
  Polygon: [[75.38,34.07],[75.44,34.07],[75.44,34.11],[75.38,34.11],[75.38,34.07]]

--- SUPPLY/NEUTRAL ---
CHARLIE DEPOT (Supply Depot — NE position)
  Center: [75.58, 34.055]
  Polygon: [[75.56,34.04],[75.60,34.04],[75.60,34.07],[75.56,34.07],[75.56,34.04]]

--- OP CAMPING ZONES (suitable for overnight ops, high concealment) ---
OPC-1 NORTH RIDGE — overlooks BRAVO CAMP, accessible via ROUTE FALCON
  Center: [75.43, 34.06]
  Polygon: [[75.415,34.0475],[75.445,34.0475],[75.445,34.0725],[75.415,34.0725],[75.415,34.0475]]

OPC-2 EAST RIDGE — fallback position near CHARLIE DEPOT, accessible via ROUTE COBRA
  Center: [75.54, 34.03]
  Polygon: [[75.5275,34.02],[75.5525,34.02],[75.5525,34.04],[75.5275,34.04],[75.5275,34.02]]

OPC-3 NORTH HEIGHTS — remote, full valley overview, difficult access
  Center: [75.46, 34.12]
  Polygon: [[75.4425,34.1075],[75.4775,34.1075],[75.4775,34.1325],[75.4425,34.1325],[75.4425,34.1075]]

--- ROUTES ---
MSR TIGER (Main Supply Route — paved, fast, EXPOSED)
  [[75.52,33.95],[75.50,33.98],[75.48,34.00],[75.45,34.03],[75.41,34.09]]

ROUTE COBRA (Mountain pass — longer, difficult, LOW EXPOSURE)
  [[75.52,33.95],[75.55,33.99],[75.58,34.02],[75.58,34.055],[75.55,34.08],[75.50,34.10],[75.41,34.09]]

ROUTE FALCON (Covert trail — foot only, MAXIMUM CONCEALMENT, ends at OPC-1)
  [[75.52,33.95],[75.50,34.01],[75.47,34.04],[75.43,34.06]]

SUPPLY LINE DELTA (Alpha to Charlie direct)
  [[75.52,33.95],[75.55,33.99],[75.58,34.055]]

--- LANDMARKS ---
KILO BRIDGE (River crossing, MSR TIGER chokepoint): [75.495, 33.98]
RIDGELINE SIERRA (Dominant high ground, full valley observation): [75.46, 34.05]
RIVER ZANSKAR (Major river, SW to NE, restricts movement): [[75.38,33.92],[75.45,33.97],[75.52,34.02],[75.58,34.10]]
""".strip()
