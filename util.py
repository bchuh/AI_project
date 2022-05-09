from dataclasses import dataclass, field
from typing import Any
import sys
import os

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)



def getRealCwd():
    if getattr(sys, 'frozen', False) :
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.dirname(__file__)
    return path