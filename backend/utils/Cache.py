from gc import collect

class Cache:
    def __init__(self, src, cvt):
        self._src = src
        self._cvt = cvt
    
    def reset(self, length: int):
        self._arr = [None] * length
        collect()

    def __getitem__(self, idx: int):
        item = self._arr[idx]
        if item is None:
            item = self._cvt(self._src, idx)
            self._arr[idx] = item
        return item

    def __len__(self):
        return len(self._arr)
