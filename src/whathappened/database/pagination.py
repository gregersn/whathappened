import math
from typing import Any, List, Optional


class Page:
    items: List[Any]
    prev_page: Optional[int]
    next_page: Optional[int]
    has_prev: bool
    prev_items: int
    has_next: bool
    total: int
    pages: int

    def __init__(self, items, page: int, page_size: int, total: int):
        self.items = items
        self.prev_page = None
        self.next_page = None
        self.has_prev = page > 1
        if self.has_prev:
            self.prev_page = page - 1
        prev_items = (page - 1) * page_size
        self.has_next = prev_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(math.ceil(total / float(page_size)))


def paginate(query, page: int, page_size: int = 25):
    if page <= 0:
        raise AttributeError("page must be >= 1")
    if page_size <= 0:
        raise AttributeError("page_size must be >= 1")

    items = query.limit(page_size).offset((page - 1) * page_size).all()
    total = query.order_by(None).count()

    return Page(items, page, page_size, total)
