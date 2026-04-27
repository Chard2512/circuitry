import math
import random
import string
from typing import List, Any, Tuple, cast

def closest_divisors(n: int) -> Tuple[int, int]:
    for i in range(int(math.isqrt(n)), 0, -1):
        if n % i == 0:
            return (i, n // i)
    return (0, 0)

def flatten_recursive(nested: List[Any]) -> List[Any]:
    result: List[Any] = []
    for item in nested:
        if isinstance(item, List):
            item = cast(List[Any], item)
            result.extend(flatten_recursive(item))
        else:
            result.append(item)
    return result

def random_id() -> str:
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + "-" + "_"
    return ''.join(random.choice(characters) for _ in range(11))