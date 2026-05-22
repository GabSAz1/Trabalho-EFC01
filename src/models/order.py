from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from datetime import datetime
import json

@dataclass
class Order:
    id: int
    client: str
    items: List[Dict[str, Any]]
    total: float
    status: str
    date: str
    client_type: str

    @classmethod
    def from_tuple(cls, data: Tuple[Any, ...]) -> 'Order':
        """Construtor alternativo para dados vindos do banco."""
        return cls(
            id=data[0],
            client=data[1],
            items=json.loads(data[2]),
            total=data[3],
            status=data[4],
            date=data[5],
            client_type=data[6]
        )

    @staticmethod
    def create_payload(client: str, items: List[Dict[str, Any]], total: float, client_type: str) -> Dict[str, Any]:
        """Factory Method: padroniza a criação da estrutura de um novo pedido."""
        return {
            'cli': client,
            'itens': items,
            'tot': total,
            'st': 'pendente',
            'dt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tp': client_type
        }