"""
Recommended Section Configuration for 15 Sections
"""

SECTION_CONFIG = {
    0: {
        "friction": 1.25,
        "steer_multiplier": 1.1,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 1.0,
            "max_shift": 0.8,
        },
    },
    1: {
        "friction": 4.9,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    2: {
        "friction": 2.4,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    3: {
        "friction": 0.67,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    4: {
        "friction": 0.9,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    5: {
        "friction": 2.8,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    6: {
        "friction": 0.8,
        "steer_multiplier": 1.0,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 6,
            "num_points": 0.6,
            "max_shift": 0.4,
        },
    },
    7: {
        "friction": 0.6,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    8: {
        "friction": 0.55,
        "steer_multiplier": 1.0,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 6,
            "num_points": 0.6,
            "max_shift": 0.4,
        },
    },
    9: {
        "friction": 3.2,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    10: {
        "friction": 1.2,
        "steer_multiplier": 1.0,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 6,
            "num_points": 0.6,
            "max_shift": 0.4,
        },
    },
    11: {
        "friction": 2.4,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    12: {
        "friction": 2.5,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.8,
            "max_shift": 0.5,
        },
    },
    13: {
        "friction": 1.2,
        "steer_multiplier": 0.8,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 10,
            "num_points": 0.6,
            "max_shift": 1,
        },
    },
    14: {
        "friction": 0.15,
        "steer_multiplier": 1.0,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 6,
            "num_points": 0.6,
            "max_shift": 0.4,
        },
    },
    15: {
        "friction": 3.35,
        "steer_multiplier": 0.9,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {"offset": 6, "num_points": 6, "max_shift": 0.45},
    },
    16: {
        "friction": 3.35,
        "steer_multiplier": 0.7,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {"offset": 6, "num_points": 4, "max_shift": 0.25},
    },
    17: {
        "friction": 3.35,
        "steer_multiplier": 0.8,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {"offset": 4, "num_points": 4, "max_shift": 0.35},
    },
    18: {
        "friction": 3.35,
        "steer_multiplier": 1.1,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {"offset": 12, "num_points": 8, "max_shift": 0.5},
    },
    19: {
        "friction": 3.35,
        "steer_multiplier": 1.15,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 12,
            "num_points": 8,
            "max_shift": 0.5,
        },
    },
    20: {
        "friction": 3.35,
        "steer_multiplier": 0.7,
        "steer_multiplier_type": "multiply",
        "waypoint_smoothing": {
            "offset": 6,
            "num_points": 0.6,
            "max_shift": 0.25,
        },
    },
}


# Helper function to get friction coefficient
def get_friction(section: int) -> float:
    return SECTION_CONFIG.get(section, {}).get("friction", 3.35)


# Helper function to apply steering multiplier
def apply_steer_multiplier(base_multiplier: float, section: int) -> float:
    config = SECTION_CONFIG.get(section, {})
    multiplier = config.get("steer_multiplier", 1.0)
    mult_type = config.get("steer_multiplier_type", "multiply")

    if mult_type == "multiply":
        return base_multiplier * multiplier
    elif mult_type == "clip":
        result = base_multiplier * multiplier
        min_val = config.get("steer_clip_min")
        max_val = config.get("steer_clip_max")
        if min_val is not None or max_val is not None:
            import numpy as np

            return np.clip(result, min_val or -np.inf, max_val or np.inf)
        return result
    elif mult_type == "max":
        return max(base_multiplier, multiplier)
    else:
        return base_multiplier


# Helper function to get waypoint smoothing parameters
def get_waypoint_smoothing_config(section: int) -> dict:
    """Get waypoint smoothing configuration for a section."""
    return SECTION_CONFIG.get(section, {}).get(
        "waypoint_smoothing", {"offset": None, "num_points": None, "max_shift": 2.0}
    )
