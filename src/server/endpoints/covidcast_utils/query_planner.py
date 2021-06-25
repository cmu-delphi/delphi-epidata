from typing import Callable, Dict, Iterable, List, Tuple
from ..._params import SourceSignalPair


def repeat_iterator_generator(it: Iterable[Dict], repeat_dict: Dict, prop: Callable) -> Iterable[Dict]:
    memory = {}
    for x in it:
        key = prop(x)
        if repeat_dict.get(key) is not None and repeat_dict[key] > 1:
            if memory.get(key) is None:
                memory[key] = []
            memory[key].append(x)
        x["_tag"] = 0
        yield x

    for key in memory:
        for i in range(repeat_dict[key]-1):
            for x in memory[key]:
                x = x.copy()
                x["_tag"] = 1 + i
                yield x


def signal_pairs_to_repeat_dict(source_signal_pairs: List[SourceSignalPair]) -> Tuple[List[SourceSignalPair], Dict]:
    ...


def apply_ops_iterator(it: Iterable[Dict], repeat_dict: Dict, prop: Callable) -> Iterable[Dict]:
    rit = repeat_iterator_generator(it, repeat_dict, prop)
