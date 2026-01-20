"""
Expressive Gesture Library

Defines emotional gestures for the robot arm. Each gesture is a parameterized
motion pattern that can express human-like emotions and reactions.

Gestures are defined as sequences of keyframes with timing and easing.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum


class Emotion(Enum):
    """Emotional states that modify gesture expression"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    TIRED = "tired"
    CURIOUS = "curious"
    SURPRISED = "surprised"
    ANGRY = "angry"
    SHY = "shy"
    CONFIDENT = "confident"


@dataclass
class Keyframe:
    """A single position in a gesture"""
    base: float = 90      # Base rotation (0-180)
    shoulder: float = 90  # Shoulder angle
    elbow: float = 90     # Elbow angle
    gripper: float = 90   # Gripper (90=closed, 30=open)
    duration: float = 0.5 # Time to reach this position (seconds)

    def to_list(self) -> List[float]:
        return [self.base, self.shoulder, self.elbow, self.gripper]


@dataclass
class Gesture:
    """A complete gesture with keyframes and metadata"""
    name: str
    description: str
    keyframes: List[Keyframe]
    emotion: Emotion = Emotion.NEUTRAL
    speed_multiplier: float = 1.0
    amplitude_multiplier: float = 1.0
    loops: int = 1
    return_home: bool = True


# ============================================================
# GESTURE DEFINITIONS
# ============================================================

def home() -> Gesture:
    """Neutral resting position"""
    return Gesture(
        name="home",
        description="Return to neutral resting position",
        keyframes=[
            Keyframe(base=90, shoulder=90, elbow=90, gripper=60, duration=0.8)
        ],
        return_home=False
    )


def wave_friendly(speed: float = 1.0, amplitude: float = 1.0) -> Gesture:
    """Friendly wave greeting"""
    amp = 25 * amplitude
    return Gesture(
        name="wave_friendly",
        description="Friendly wave to greet someone",
        keyframes=[
            # Raise arm
            Keyframe(base=90, shoulder=60, elbow=45, gripper=30, duration=0.4),
            # Wave back and forth
            Keyframe(base=90+amp, shoulder=60, elbow=45, gripper=30, duration=0.2),
            Keyframe(base=90-amp, shoulder=60, elbow=45, gripper=30, duration=0.2),
            Keyframe(base=90+amp, shoulder=60, elbow=45, gripper=30, duration=0.2),
            Keyframe(base=90-amp, shoulder=60, elbow=45, gripper=30, duration=0.2),
            Keyframe(base=90+amp, shoulder=60, elbow=45, gripper=30, duration=0.2),
            Keyframe(base=90, shoulder=60, elbow=45, gripper=30, duration=0.2),
        ],
        emotion=Emotion.HAPPY,
        speed_multiplier=speed,
        loops=1
    )


def wave_excited(speed: float = 1.5, amplitude: float = 1.3) -> Gesture:
    """Enthusiastic excited wave"""
    amp = 30 * amplitude
    return Gesture(
        name="wave_excited",
        description="Excited, enthusiastic wave",
        keyframes=[
            Keyframe(base=90, shoulder=50, elbow=35, gripper=30, duration=0.3),
            Keyframe(base=90+amp, shoulder=45, elbow=30, gripper=30, duration=0.12),
            Keyframe(base=90-amp, shoulder=55, elbow=40, gripper=30, duration=0.12),
            Keyframe(base=90+amp, shoulder=45, elbow=30, gripper=30, duration=0.12),
            Keyframe(base=90-amp, shoulder=55, elbow=40, gripper=30, duration=0.12),
            Keyframe(base=90+amp, shoulder=45, elbow=30, gripper=30, duration=0.12),
            Keyframe(base=90-amp, shoulder=55, elbow=40, gripper=30, duration=0.12),
        ],
        emotion=Emotion.EXCITED,
        speed_multiplier=speed,
        loops=2
    )


def salute() -> Gesture:
    """Military-style salute"""
    return Gesture(
        name="salute",
        description="Respectful salute gesture",
        keyframes=[
            # Raise to salute position
            Keyframe(base=70, shoulder=45, elbow=140, gripper=90, duration=0.5),
            # Hold salute
            Keyframe(base=70, shoulder=45, elbow=140, gripper=90, duration=0.8),
            # Lower slightly (acknowledgment)
            Keyframe(base=70, shoulder=50, elbow=135, gripper=90, duration=0.2),
            Keyframe(base=70, shoulder=45, elbow=140, gripper=90, duration=0.2),
        ],
        emotion=Emotion.CONFIDENT
    )


def nod_yes(speed: float = 1.0) -> Gesture:
    """Nodding yes - agreement"""
    return Gesture(
        name="nod_yes",
        description="Nodding to indicate yes/agreement",
        keyframes=[
            Keyframe(base=90, shoulder=75, elbow=90, gripper=60, duration=0.3),
            Keyframe(base=90, shoulder=105, elbow=90, gripper=60, duration=0.25),
            Keyframe(base=90, shoulder=75, elbow=90, gripper=60, duration=0.25),
            Keyframe(base=90, shoulder=105, elbow=90, gripper=60, duration=0.25),
            Keyframe(base=90, shoulder=75, elbow=90, gripper=60, duration=0.25),
        ],
        speed_multiplier=speed,
        loops=1
    )


def shake_no(speed: float = 1.0) -> Gesture:
    """Shaking no - disagreement"""
    return Gesture(
        name="shake_no",
        description="Shaking to indicate no/disagreement",
        keyframes=[
            Keyframe(base=90, shoulder=70, elbow=60, gripper=60, duration=0.3),
            Keyframe(base=120, shoulder=70, elbow=60, gripper=60, duration=0.2),
            Keyframe(base=60, shoulder=70, elbow=60, gripper=60, duration=0.2),
            Keyframe(base=120, shoulder=70, elbow=60, gripper=60, duration=0.2),
            Keyframe(base=60, shoulder=70, elbow=60, gripper=60, duration=0.2),
            Keyframe(base=90, shoulder=70, elbow=60, gripper=60, duration=0.2),
        ],
        speed_multiplier=speed,
        loops=1
    )


def thinking() -> Gesture:
    """Thinking/pondering pose"""
    return Gesture(
        name="thinking",
        description="Thoughtful thinking pose",
        keyframes=[
            # Move to thinking position (like hand on chin)
            Keyframe(base=75, shoulder=55, elbow=130, gripper=70, duration=0.6),
            # Slight movements while "thinking"
            Keyframe(base=75, shoulder=53, elbow=128, gripper=70, duration=0.4),
            Keyframe(base=78, shoulder=55, elbow=132, gripper=70, duration=0.4),
            Keyframe(base=73, shoulder=54, elbow=129, gripper=70, duration=0.4),
            # Small "aha" lift
            Keyframe(base=80, shoulder=50, elbow=120, gripper=50, duration=0.3),
        ],
        emotion=Emotion.CURIOUS
    )


def surprised() -> Gesture:
    """Surprised reaction - quick jerk back"""
    return Gesture(
        name="surprised",
        description="Surprised/startled reaction",
        keyframes=[
            # Quick jerk up and back
            Keyframe(base=90, shoulder=50, elbow=50, gripper=30, duration=0.15),
            # Hold surprised pose
            Keyframe(base=90, shoulder=55, elbow=55, gripper=30, duration=0.4),
            # Slight tremor
            Keyframe(base=92, shoulder=53, elbow=53, gripper=30, duration=0.1),
            Keyframe(base=88, shoulder=57, elbow=57, gripper=30, duration=0.1),
            Keyframe(base=90, shoulder=55, elbow=55, gripper=30, duration=0.2),
        ],
        emotion=Emotion.SURPRISED
    )


def sad_droop() -> Gesture:
    """Sad, drooping posture"""
    return Gesture(
        name="sad_droop",
        description="Sad, dejected drooping motion",
        keyframes=[
            # Slow droop down
            Keyframe(base=90, shoulder=110, elbow=120, gripper=80, duration=1.2),
            # Small sigh-like movement
            Keyframe(base=90, shoulder=115, elbow=125, gripper=85, duration=0.8),
            Keyframe(base=90, shoulder=112, elbow=122, gripper=82, duration=0.6),
        ],
        emotion=Emotion.SAD,
        speed_multiplier=0.6  # Slower for sadness
    )


def excited_bounce() -> Gesture:
    """Excited bouncing up and down"""
    return Gesture(
        name="excited_bounce",
        description="Excited bouncing motion",
        keyframes=[
            Keyframe(base=90, shoulder=70, elbow=70, gripper=40, duration=0.15),
            Keyframe(base=90, shoulder=90, elbow=90, gripper=50, duration=0.15),
            Keyframe(base=90, shoulder=65, elbow=65, gripper=35, duration=0.15),
            Keyframe(base=90, shoulder=95, elbow=95, gripper=55, duration=0.15),
            Keyframe(base=90, shoulder=68, elbow=68, gripper=38, duration=0.15),
            Keyframe(base=90, shoulder=92, elbow=92, gripper=52, duration=0.15),
        ],
        emotion=Emotion.EXCITED,
        loops=2
    )


def celebrate() -> Gesture:
    """Victory/celebration gesture"""
    return Gesture(
        name="celebrate",
        description="Victory celebration - arm pump",
        keyframes=[
            # Wind up
            Keyframe(base=90, shoulder=100, elbow=110, gripper=90, duration=0.3),
            # Pump up!
            Keyframe(base=90, shoulder=40, elbow=40, gripper=90, duration=0.2),
            # Hold high
            Keyframe(base=90, shoulder=35, elbow=35, gripper=90, duration=0.4),
            # Pump again
            Keyframe(base=90, shoulder=50, elbow=50, gripper=90, duration=0.15),
            Keyframe(base=90, shoulder=35, elbow=35, gripper=90, duration=0.15),
        ],
        emotion=Emotion.HAPPY,
        loops=2
    )


def shy_retreat() -> Gesture:
    """Shy, retreating motion"""
    return Gesture(
        name="shy_retreat",
        description="Shy, timid retreating motion",
        keyframes=[
            # Pull back slightly
            Keyframe(base=90, shoulder=100, elbow=110, gripper=90, duration=0.5),
            # Peek out a little
            Keyframe(base=85, shoulder=95, elbow=105, gripper=85, duration=0.4),
            # Retreat again
            Keyframe(base=90, shoulder=105, elbow=115, gripper=95, duration=0.3),
        ],
        emotion=Emotion.SHY,
        speed_multiplier=0.8
    )


def curious_look() -> Gesture:
    """Curious, examining motion"""
    return Gesture(
        name="curious_look",
        description="Curious examining motion - like looking at something",
        keyframes=[
            # Extend forward curiously
            Keyframe(base=90, shoulder=70, elbow=70, gripper=40, duration=0.5),
            # Tilt/examine from different angles
            Keyframe(base=110, shoulder=65, elbow=65, gripper=40, duration=0.4),
            Keyframe(base=70, shoulder=75, elbow=75, gripper=40, duration=0.4),
            Keyframe(base=90, shoulder=60, elbow=60, gripper=35, duration=0.3),
            # Get closer
            Keyframe(base=90, shoulder=55, elbow=55, gripper=30, duration=0.3),
        ],
        emotion=Emotion.CURIOUS
    )


def tired_stretch() -> Gesture:
    """Tired stretching motion"""
    return Gesture(
        name="tired_stretch",
        description="Tired stretching, like waking up",
        keyframes=[
            # Start low
            Keyframe(base=90, shoulder=110, elbow=110, gripper=70, duration=0.8),
            # Slow stretch up
            Keyframe(base=90, shoulder=50, elbow=50, gripper=30, duration=1.5),
            # Hold stretch
            Keyframe(base=100, shoulder=45, elbow=45, gripper=30, duration=0.6),
            Keyframe(base=80, shoulder=45, elbow=45, gripper=30, duration=0.6),
            # Relax back down slowly
            Keyframe(base=90, shoulder=95, elbow=95, gripper=60, duration=1.0),
        ],
        emotion=Emotion.TIRED,
        speed_multiplier=0.7
    )


def angry_shake() -> Gesture:
    """Angry shaking fist motion"""
    return Gesture(
        name="angry_shake",
        description="Angry fist shaking",
        keyframes=[
            # Clench and raise
            Keyframe(base=90, shoulder=60, elbow=70, gripper=95, duration=0.3),
            # Shake aggressively
            Keyframe(base=95, shoulder=55, elbow=65, gripper=95, duration=0.1),
            Keyframe(base=85, shoulder=65, elbow=75, gripper=95, duration=0.1),
            Keyframe(base=98, shoulder=52, elbow=62, gripper=95, duration=0.1),
            Keyframe(base=82, shoulder=68, elbow=78, gripper=95, duration=0.1),
            Keyframe(base=95, shoulder=55, elbow=65, gripper=95, duration=0.1),
            Keyframe(base=85, shoulder=65, elbow=75, gripper=95, duration=0.1),
        ],
        emotion=Emotion.ANGRY,
        speed_multiplier=1.3,
        loops=2
    )


def point_forward() -> Gesture:
    """Pointing forward gesture"""
    return Gesture(
        name="point_forward",
        description="Pointing forward - indicating direction",
        keyframes=[
            Keyframe(base=90, shoulder=75, elbow=45, gripper=90, duration=0.4),
            # Extend to point
            Keyframe(base=90, shoulder=60, elbow=30, gripper=90, duration=0.3),
            # Hold point
            Keyframe(base=90, shoulder=60, elbow=30, gripper=90, duration=0.6),
            # Slight emphasis
            Keyframe(base=90, shoulder=58, elbow=28, gripper=90, duration=0.15),
            Keyframe(base=90, shoulder=60, elbow=30, gripper=90, duration=0.15),
        ],
        emotion=Emotion.CONFIDENT
    )


def shrug() -> Gesture:
    """Shrugging - I don't know"""
    return Gesture(
        name="shrug",
        description="Shrugging gesture - uncertainty",
        keyframes=[
            # Raise up in shrug
            Keyframe(base=90, shoulder=70, elbow=100, gripper=50, duration=0.4),
            # Hold shrug
            Keyframe(base=90, shoulder=65, elbow=105, gripper=50, duration=0.5),
            # Slight emphasis
            Keyframe(base=90, shoulder=62, elbow=108, gripper=50, duration=0.2),
            Keyframe(base=90, shoulder=68, elbow=102, gripper=50, duration=0.3),
        ],
        emotion=Emotion.NEUTRAL
    )


def beckoning() -> Gesture:
    """Beckoning/come here gesture"""
    return Gesture(
        name="beckoning",
        description="Come here beckoning motion",
        keyframes=[
            # Extend outward
            Keyframe(base=90, shoulder=70, elbow=60, gripper=30, duration=0.4),
            # Curl in (beckoning)
            Keyframe(base=90, shoulder=80, elbow=90, gripper=60, duration=0.3),
            Keyframe(base=90, shoulder=70, elbow=60, gripper=30, duration=0.3),
            Keyframe(base=90, shoulder=80, elbow=90, gripper=60, duration=0.3),
            Keyframe(base=90, shoulder=70, elbow=60, gripper=30, duration=0.3),
        ],
        loops=2
    )


def bow() -> Gesture:
    """Respectful bow"""
    return Gesture(
        name="bow",
        description="Respectful bowing motion",
        keyframes=[
            # Lower into bow
            Keyframe(base=90, shoulder=120, elbow=60, gripper=60, duration=0.8),
            # Hold bow
            Keyframe(base=90, shoulder=125, elbow=55, gripper=60, duration=0.6),
            # Rise back up
            Keyframe(base=90, shoulder=90, elbow=90, gripper=60, duration=0.7),
        ],
        emotion=Emotion.NEUTRAL
    )


def dance_groove() -> Gesture:
    """Fun dancing groove"""
    return Gesture(
        name="dance_groove",
        description="Fun dancing motion",
        keyframes=[
            Keyframe(base=110, shoulder=70, elbow=70, gripper=40, duration=0.25),
            Keyframe(base=70, shoulder=80, elbow=80, gripper=50, duration=0.25),
            Keyframe(base=100, shoulder=60, elbow=90, gripper=35, duration=0.25),
            Keyframe(base=80, shoulder=85, elbow=65, gripper=55, duration=0.25),
            Keyframe(base=115, shoulder=65, elbow=75, gripper=45, duration=0.25),
            Keyframe(base=65, shoulder=75, elbow=85, gripper=40, duration=0.25),
        ],
        emotion=Emotion.HAPPY,
        loops=3
    )


# ============================================================
# GESTURE REGISTRY
# ============================================================

GESTURE_REGISTRY: Dict[str, Callable[..., Gesture]] = {
    "home": home,
    "wave": wave_friendly,
    "wave_friendly": wave_friendly,
    "wave_excited": wave_excited,
    "salute": salute,
    "nod": nod_yes,
    "nod_yes": nod_yes,
    "shake": shake_no,
    "shake_no": shake_no,
    "thinking": thinking,
    "think": thinking,
    "surprised": surprised,
    "surprise": surprised,
    "sad": sad_droop,
    "sad_droop": sad_droop,
    "excited": excited_bounce,
    "excited_bounce": excited_bounce,
    "celebrate": celebrate,
    "victory": celebrate,
    "shy": shy_retreat,
    "shy_retreat": shy_retreat,
    "curious": curious_look,
    "curious_look": curious_look,
    "tired": tired_stretch,
    "tired_stretch": tired_stretch,
    "angry": angry_shake,
    "angry_shake": angry_shake,
    "point": point_forward,
    "point_forward": point_forward,
    "shrug": shrug,
    "beckon": beckoning,
    "beckoning": beckoning,
    "come_here": beckoning,
    "bow": bow,
    "dance": dance_groove,
    "dance_groove": dance_groove,
    "groove": dance_groove,
}


def get_gesture(name: str, **kwargs) -> Optional[Gesture]:
    """Get a gesture by name with optional parameters"""
    if name.lower() in GESTURE_REGISTRY:
        return GESTURE_REGISTRY[name.lower()](**kwargs)
    return None


def list_gestures() -> List[str]:
    """List all available gesture names"""
    return list(set(GESTURE_REGISTRY.keys()))


def get_gesture_for_emotion(emotion: Emotion) -> List[str]:
    """Get gestures appropriate for a given emotion"""
    emotion_map = {
        Emotion.HAPPY: ["wave_friendly", "celebrate", "dance_groove", "excited_bounce"],
        Emotion.SAD: ["sad_droop", "shy_retreat"],
        Emotion.EXCITED: ["wave_excited", "excited_bounce", "celebrate", "dance_groove"],
        Emotion.TIRED: ["tired_stretch", "sad_droop"],
        Emotion.CURIOUS: ["curious_look", "thinking"],
        Emotion.SURPRISED: ["surprised"],
        Emotion.ANGRY: ["angry_shake", "shake_no"],
        Emotion.SHY: ["shy_retreat", "bow"],
        Emotion.CONFIDENT: ["salute", "point_forward", "celebrate"],
        Emotion.NEUTRAL: ["home", "nod_yes", "shake_no", "shrug", "bow"],
    }
    return emotion_map.get(emotion, ["home"])
