from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

class IOrderRepository(ABC):
    @abstractmethod
    def insert(self, client: str, items_str: str, total: float, status: str, date: str, client_type: str) -> int:
        pass

    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[Tuple]:
        pass

    @abstractmethod
    def update_status(self, order_id: int, status: str) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Tuple]:
        pass

    @abstractmethod
    def get_by_client(self, client: str) -> List[Tuple]:
        pass

    @abstractmethod
    def get_distinct_clients(self) -> List[Tuple]:
        pass