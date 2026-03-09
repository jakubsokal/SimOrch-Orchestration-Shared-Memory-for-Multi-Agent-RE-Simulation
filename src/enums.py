from enum import Enum

from agents.helper_agent import HelperAgent
from agents.re_agent import REAgent
from agents.user_agent import UserAgent

class ExperienceLevel(str, Enum):
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"

class QuestioningStrategy(str, Enum):
    STRUCTURED = "structured"
    EXPLORATORY = "exploratory"

class ProbingIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RequirementFocus(str, Enum):
    FUNCTIONAL = "functional"
    BALANCED = "balanced"
    QUALITY_ORIENTED = "quality_oriented"

class Tone(str, Enum):
    FORMAL = "formal"
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"

class CommunicationStyle(str, Enum):
    COOPERATIVE = "cooperative"
    VAGUE = "vague"
    VERBOSE = "verbose"
    CONCISE = "concise"
    IMPATIENT = "impatient"

class DomainKnowledge(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ClarityLevel(str, Enum):
    CLEAR = "clear"
    PARTIALLY_CLEAR = "partially_clear"
    UNCLEAR = "unclear"

class RevelationStrategy(str, Enum):
    REACTIVE = "reactive"
    PROACTIVE = "proactive"
    RELUCTANT = "reluctant"

class RevelationRate(str, Enum):
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"