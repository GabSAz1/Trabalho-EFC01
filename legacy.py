from typing import List, Dict, Any, Optional
from src.repositories.order_repository import SQLiteOrderRepository
from src.services.notification_service import NotificationService
from src.services.order_service import OrderService
import json
from datetime import datetime

class Sis:
    def __init__(self) -> None:
        self.repo = SQLiteOrderRepository('loja.db')
        self.notifier = NotificationService()
        self.service = OrderService(self.repo, self.notifier)

    def add_ped(self, n: str, its: List[Dict[str, Any]], t: str) -> int:
        return self.service.add_ped(n, its, t)

    def get_ped(self, id: int) -> Optional[Dict[str, Any]]:
        return self.service.get_ped(id)

    def upd_st(self, id: int, s: str) -> None:
        self.service.upd_st(id, s)

    def calc_tot_cli(self, n: str) -> float:
        return self.service.calc_tot_cli(n)

    def gerar_rel(self, tipo: str) -> None:
        self.service.gerar_rel(tipo)

    def proc_pag(self, id: int, m: str, vl: float) -> bool:
        return self.service.proc_pag(id, m, vl)

    def validar_estoque(self, its: List[Dict[str, Any]]) -> bool:
        return self.service.validar_estoque(its)

    def cancelar_pedido(self, id: int) -> None:
        self.repo.update_status(id, 'cancelado')
        print(f"Pedido {id} cancelado")

    def close(self) -> None:
        pass

class PedEspecial(Sis):
    def add_ped(self, n: str, its: List[Dict[str, Any]], t: str) -> int:
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tot = 0.0
        for i in its:
            if i['tipo'] == 'normal':
                tot += i['p'] * i['q']
            elif i['tipo'] == 'desc10':
                tot += i['p'] * i['q'] * 0.9
            elif i['tipo'] == 'desc20':
                tot += i['p'] * i['q'] * 0.8
        tot = tot * 1.15
        
        items_str = json.dumps(its)
        order_id = self.repo.insert(n, items_str, tot, 'pendente', dt, t)
        print(f"Email especial enviado para {n}: Pedido especial recebido!")
        return order_id

    def upd_st(self, id: int, s: str) -> None:
        p = self.get_ped(id)
        if p:
            self.repo.update_status(id, s)
            print(f"Pedido especial {id} -> {s}")

def main() -> None:
    pass

if __name__ == '__main__':
    main()
