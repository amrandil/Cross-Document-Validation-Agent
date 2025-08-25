"""ReAct agent for multi-document fraud detection."""

# Import old agent components (optional)
try:
    from .core import FraudDetectionAgent
    OLD_AGENT_AVAILABLE = True
except ImportError:
    OLD_AGENT_AVAILABLE = False
    FraudDetectionAgent = None

# Import new ReAct agent components
try:
    from .react_agent import ReActFraudDetectionAgent, Observer, Thinker, Actor
    REACT_AGENT_AVAILABLE = True
except ImportError:
    REACT_AGENT_AVAILABLE = False
    ReActFraudDetectionAgent = None
    Observer = None
    Thinker = None
    Actor = None

# Import other components
try:
    from .executor import FraudDetectionExecutor
    from .prompts import AGENT_SYSTEM_PROMPT, get_agent_prompt_template
    from .memory import FraudDetectionMemory
    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False
    FraudDetectionExecutor = None
    AGENT_SYSTEM_PROMPT = None
    get_agent_prompt_template = None
    FraudDetectionMemory = None

__all__ = [
    "FraudDetectionAgent",
    "ReActFraudDetectionAgent",
    "Observer",
    "Thinker", 
    "Actor",
    "FraudDetectionExecutor",
    "AGENT_SYSTEM_PROMPT",
    "get_agent_prompt_template",
    "FraudDetectionMemory",
    "OLD_AGENT_AVAILABLE",
    "REACT_AGENT_AVAILABLE",
    "EXECUTOR_AVAILABLE"
]
