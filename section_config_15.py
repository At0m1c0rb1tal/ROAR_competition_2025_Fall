"""
Recommended Section Configuration for 15 Sections

"""


SECTION_CONFIG = {
   # Section 0: Starting section (typically straight)
   0: {
       'friction': 0.15,
       'steer_multiplier': 1.2,
       'steer_multiplier_type': 'multiply',
       'waypoint_smoothing': {
           'offset': 5,
           'num_points': 2,
           'max_shift': 1.0,
       }
   },
  
   # Section 1: First corner/transition
   1: {
       'friction': 4.90,  # Higher grip for controlled entry
       'steer_multiplier': 1.7,
       'steer_multiplier_type': 'multiply',
       'waypoint_smoothing': {
           'offset': -2,  # Closer lookahead for precision
           'num_points': None,  # Default
           'max_shift': 0.2,  # Very tight control
       }
   },
  
   # Section 2: Second corner
   2: {
       'friction': 2.4,  # Standard
       'steer_multiplier': 1.2,
       'steer_multiplier_type': 'multiply',
       'waypoint_smoothing': {
           'offset': 20,  # Fixed offset
           'num_points': 1.0,
           'max_shift': 1.0,
       }
   },
  
   # Section 3: High-speed section
   3: {
       'friction': 0.67,
       'steer_multiplier': 0.7,
       'steer_multiplier_type': 'multiply',
       'steer_clip_min': None,
       'steer_clip_max': None,
       'waypoint_smoothing': {
           'offset': 10,
           'num_points': 0.8,  # More smoothing for high speed
           'max_shift': 0.5,
       }
   },
  
   # Section 4: High grip section
   4: {
       'friction': 0.9,
       'steer_multiplier': 0.7,
       'steer_multiplier_type': 'multiply',
       'steer_clip_min': None,
       'steer_clip_max': None,
       'waypoint_smoothing': {
           'offset': 10,
           'num_points': 0.8,  # More smoothing for high speed
           'max_shift': 0.5,
       }
   },
  
   # Section 5: High grip continuation
   5: {
       'friction': 2.8,
       'steer_multiplier': 1.4,
       'steer_multiplier_type': 'multiply',
       'steer_clip_min': None,
       'steer_clip_max': None,
       'waypoint_smoothing': {
           'offset': 10,
           'num_points': 0.6,  # More smoothing for high speed
           'max_shift': 0.5,
       }
   },
  
   # Section 6: Low grip / tricky corner
   6: {
       'friction': 0.8,  # Lower grip - slippery
       'steer_multiplier': 1.0,
       'steer_multiplier_type': 'multiply',
        'steer_clip_min': None,
       'steer_clip_max': None,
       'waypoint_smoothing': {
           'offset': 6,
           'num_points': 0.5,  # Less smoothing for tight control
           'max_shift': 0.4,
       }
   },
  
   # Section 7: Standard section
    7: {
       'friction': 0.4,
       'steer_multiplier': 0.7,
       'steer_multiplier_type': 'multiply',
       'steer_clip_min': None,
       'steer_clip_max': None,
       'waypoint_smoothing': {
           'offset': -2,
           'num_points': 3.0,  # More smoothing for high speed
           'max_shift': 0.5,
       }
   },
  
   # Section 8: Standard section
   8: {
       'friction': 0.55,
       'steer_multiplier': 1.0,
       'steer_multiplier_type': 'multiply',
       'waypoint_smoothing': {
           'offset': 12,
           'num_points': 0.8,
           'max_shift': 0.6,
       }
   },
  
   # Section 9: Medium grip corner
    9: {
       'friction': 3.2,
       'steer_multiplier': 1.2,
       'steer_multiplier_type': 'multiply',
       'steer_clip_min': None,
       'steer_clip_max': None,
       'waypoint_smoothing': {
           'offset': 10,
           'num_points': 0.,  # More smoothing for high speed
           'max_shift': 0.5,
       }
   },
  
   # Section 10: Low grip corner
   10: {
       'friction': 1.2,  # Low grip
       'steer_multiplier': 1.25,
       'steer_multiplier_type': 'clip',
       'steer_clip_min': 1.05,
       'steer_clip_max': 1.5,
       'waypoint_smoothing': {
           'offset': 12,
           'num_points': 2,  # Minimal smoothing
           'max_shift': 2.0,
       }
   },
  
   # Section 11: Additional sections (extended from 10 to 15)
   11: {
       'friction': 2.35,
       'steer_multiplier': 1.0,
       'steer_multiplier_type': 'multiply',
       'waypoint_smoothing': {
           'offset': None,
           'num_points': None,
           'max_shift': 2.0,
       }
   },
  
   12: {
       'friction': 2.5,  # Slightly higher grip
       'steer_multiplier': 1.2,
       'steer_multiplier_type': 'multiply',
       'waypoint_smoothing': {
           'offset': None,
           'num_points': 1.2,  # Multiplier
           'max_shift': 2.0,
       }
   },
  
   13: {
       'friction': 1.20,  # Slightly lower grip
       'steer_multiplier': 0.7,
       'steer_multiplier_type': 'multiply',
       'waypoint_smoothing': {
           'offset': 10,
           'num_points': 10,
           'max_shift': 1.0,
       }
   },
  
   14: {
       'friction': 0.15,
       'steer_multiplier': 1.2,
       'steer_multiplier_type': 'multiply',
       'waypoint_smoothing': {
           'offset': -1,
           'num_points': 2,
           'max_shift': 1.0,
       }
   },
}


# Helper function to get friction coefficient
def get_friction(section: int) -> float:
   return SECTION_CONFIG.get(section, {}).get('friction', 3.35)


# Helper function to apply steering multiplier
def apply_steer_multiplier(base_multiplier: float, section: int) -> float:
   """Apply section-specific steering multiplier."""
   config = SECTION_CONFIG.get(section, {})
   multiplier = config.get('steer_multiplier', 1.0)
   mult_type = config.get('steer_multiplier_type', 'multiply')
  
   if mult_type == 'multiply':
       return base_multiplier * multiplier
   elif mult_type == 'clip':
       result = base_multiplier * multiplier
       min_val = config.get('steer_clip_min')
       max_val = config.get('steer_clip_max')
       if min_val is not None or max_val is not None:
           import numpy as np
           return np.clip(result, min_val or -np.inf, max_val or np.inf)
       return result
   elif mult_type == 'max':
       return max(base_multiplier, multiplier)
   else:
       return base_multiplier


# Helper function to get waypoint smoothing parameters
def get_waypoint_smoothing_config(section: int) -> dict:
   """Get waypoint smoothing configuration for a section."""
   return SECTION_CONFIG.get(section, {}).get('waypoint_smoothing', {
       'offset': None,
       'num_points': None,
       'max_shift': 2.0
   })




