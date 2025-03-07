from enum import Enum

class TicketState(Enum):
    DORMANT = 0
    NEW = 1
    QUEUED = 2
    RESOLVING = 3
    RESOLVED = 4
    UNRESOLVED = 5