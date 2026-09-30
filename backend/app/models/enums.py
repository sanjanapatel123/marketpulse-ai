from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class RunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class EventType(str, Enum):
    TEXT_DELTA = "text_delta"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    RUN_INTERRUPTED = "run_interrupted"

class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"


class Currency(str, Enum):
    INR = "INR"


class MarketDataStatus(str, Enum):
    SIMULATED = "simulated"
    DELAYED = "delayed"
    REALTIME = "realtime"
    STALE = "stale"

class TransactionSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class PriceAlertCondition(str, Enum):
    PRICE_ABOVE = "PRICE_ABOVE"
    PRICE_BELOW = "PRICE_BELOW"


class PriceAlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    DISABLED = "DISABLED"