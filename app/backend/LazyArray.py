from gc import collect
from typing import TypeVar, Generic, List, Iterable, Optional, Callable

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")

TTransform = Callable[[TSource], TResult]

class LazyArray(Generic[TSource, TResult]):
    def __init__(self, source: Iterable[TSource], fn: TTransform, reserve: Optional[int] = None):
        self.__transform = fn
        self.__source = list(source)
        self.__cache: List[Optional[TResult]] = [None] * reserve if reserve else[]

    def clear(self):
        self.__cache = []
        collect()

    def setTransform(self, fn: TTransform):
        self.__transform = fn
        self.clear()

    def __getitem__(self, idx: int) -> TResult:
        item = self.__cache[idx]
        if item is None:
            item = self.__transform(self.__source[idx])
            self.__cache[idx] = item
        return item

