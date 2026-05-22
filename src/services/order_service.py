import json
from typing import List, Dict, Any, Optional
from src.repositories.interfaces import IOrderRepository
from src.services.notification_service import NotificationService
from src.models.order import Order # <-- Importamos o Model aqui
from src.strategies.payment_strategy import CreditCardPayment, PixPayment, BoletoPayment
from src.strategies.discount_strategy import (
    NormalDiscount, Discount10, Discount20, FreeShipping,
    VIPOrderDiscount, CorpOrderDiscount, NormalOrderDiscount, SpecialOrderDiscount
)

class OrderService:
    def __init__(self, repository: IOrderRepository, notifier: NotificationService) -> None:
        self.repo = repository
        self.notifier = notifier
        self._observers: List[Any] = [] # Lista de ouvintes
        
        self.item_discounts = {
            'normal': NormalDiscount(),
            'desc10': Discount10(),
            'desc20': Discount20(),
            'frete_gratis': FreeShipping()
        }
        self.order_discounts = {
            'normal': NormalOrderDiscount(),
            'vip': VIPOrderDiscount(),
            'corporativo': CorpOrderDiscount(),
            'especial': SpecialOrderDiscount()
        }
        self.payment_methods = {
            'cartao': CreditCardPayment(),
            'pix': PixPayment(),
            'boleto': BoletoPayment()
        }

    # Sistema de Inscrição (Observer)
    def attach(self, observer: Any) -> None:
        self._observers.append(observer)

    def _notify_observers(self, event_type: str, order_data: Dict[str, Any]) -> None:
        for obs in self._observers:
            obs.update(event_type, order_data)

    def add_ped(self, client: str, items: List[Dict[str, Any]], client_type: str) -> int:
        tot = self._calculate_total(items, client_type)
        
        # Uso do Factory Method do próprio Model
        order_dict = Order.create_payload(client, items, tot, client_type)
        items_str = json.dumps(order_dict['itens'])
        
        order_id = self.repo.insert(
            order_dict['cli'], items_str, order_dict['tot'], 
            order_dict['st'], order_dict['dt'], order_dict['tp']
        )
        
        order_payload = {'id': order_id, 'cli': client, 'tp': client_type, 'tot': tot}
        self._notify_observers('created', order_payload)
        
        return order_id

    def _calculate_total(self, items: List[Dict[str, Any]], client_type: str) -> float:
        tot = 0.0
        for i in items:
            strategy = self.item_discounts.get(i['tipo'], NormalDiscount())
            tot += strategy.calculate(i['p'], i['q'])

        order_strategy = self.order_discounts.get(client_type, NormalOrderDiscount())
        return order_strategy.apply_discount(tot)
            
    def get_ped(self, order_id: int) -> Optional[Dict[str, Any]]:
        r = self.repo.get_by_id(order_id)
        if r:
            return {'id': r[0], 'cli': r[1], 'itens': json.loads(str(r[2])),
                    'tot': r[3], 'st': r[4], 'dt': r[5], 'tp': r[6]}
        return None

    def upd_st(self, order_id: int, status: str) -> None:
        p = self.get_ped(order_id)
        if p:
            self.repo.update_status(order_id, status)
            self._notify_observers(status, p)

    def proc_pag(self, order_id: int, method: str, value: float) -> bool:
        p = self.get_ped(order_id)
        if not p:
            return False
        if value < p['tot']:
            print("Valor insuficiente!")
            return False
        
        payment_strategy = self.payment_methods.get(method)
        if not payment_strategy:
            print("Metodo de pagamento invalido!")
            return False
            
        if payment_strategy.process(value):
            if not payment_strategy.requires_manual_approval():
                self.upd_st(order_id, 'aprovado')
            return True
        return False
            
    def validar_estoque(self, items: List[Dict[str, Any]]) -> bool:
        est = {'produto1': 100, 'produto2': 50, 'produto3': 75}
        for i in items:
            if i['nome'] not in est:
                print(f"Produto {i['nome']} nao encontrado!")
                return False
            if est[i['nome']] < i['q']:
                print(f"Estoque insuficiente para {i['nome']}!")
                return False
        return True

    def calc_tot_cli(self, client: str) -> float:
        orders = self.repo.get_by_client(client)
        return sum(float(r[3]) for r in orders)

    def gerar_rel(self, tipo: str) -> None:
        if tipo == 'vendas':
            orders = self.repo.get_all()
            print("=== RELATORIO DE VENDAS ===")
            tot_g = sum(r[3] for r in orders)
            for r in orders:
                print(f"Pedido #{r[0]} - Cliente: {r[1]} - Total: R${r[3]:.2f} - Status: {r[4]}")
            print(f"Total Geral: R${tot_g:.2f}")
            with open('rel_vendas.txt', 'w') as f:
                f.write(f"Total de vendas: {tot_g}")
                
        elif tipo == 'clientes':
            clients = self.repo.get_distinct_clients()
            print("=== RELATORIO DE CLIENTES ===")
            with open('rel_clientes.txt', 'w') as f:
                for r in clients:
                    n, tp = r[0], r[1]
                    tot = self.calc_tot_cli(n)
                    print(f"Cliente: {n} ({tp}) - Total gasto: R${tot:.2f}")
                    f.write(f"{n},{tp}\n")