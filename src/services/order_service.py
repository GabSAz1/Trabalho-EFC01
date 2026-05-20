import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.repositories.interfaces import IOrderRepository
from src.services.notification_service import NotificationService

class OrderService:
    def __init__(self, repository: IOrderRepository, notifier: NotificationService) -> None:
        self.repo = repository
        self.notifier = notifier

    def add_ped(self, client: str, items: List[Dict[str, Any]], client_type: str) -> int:
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tot = self._calculate_total(items, client_type)
        
        items_str = json.dumps(items)
        order_id = self.repo.insert(client, items_str, tot, 'pendente', dt, client_type)
        
        self._notify_creation(client, client_type)
        return order_id

    def _calculate_total(self, items: List[Dict[str, Any]], client_type: str) -> float:
        tot = 0.0
        for i in items:
            if i['tipo'] == 'normal':
                tot += i['p'] * i['q']
            elif i['tipo'] == 'desc10':
                tot += i['p'] * i['q'] * 0.9
            elif i['tipo'] == 'desc20':
                tot += i['p'] * i['q'] * 0.8
            elif i['tipo'] == 'frete_gratis':
                tot += i['p'] * i['q']

        if client_type == 'vip':
            tot *= 0.95
        elif client_type == 'corporativo':
            tot *= 0.90
        return tot

    def _notify_creation(self, client: str, client_type: str) -> None:
        if client_type == 'normal':
            self.notifier.send_email(client, "Pedido recebido!")
        elif client_type == 'vip':
            self.notifier.send_email(client, "Pedido recebido!")
            self.notifier.send_sms(client, "Pedido VIP recebido!")
        elif client_type == 'corporativo':
            self.notifier.send_email(client, "Pedido recebido!")
            self.notifier.notify_manager(client)
            
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
            self._handle_status_change_side_effects(p, status)

    def _handle_status_change_side_effects(self, p: Dict[str, Any], status: str) -> None:
        if status == 'aprovado':
            self.notifier.send_email(p['cli'], "Pedido aprovado!")
            if p['tp'] == 'vip':
                self.notifier.send_sms(p['cli'], "Pedido aprovado!")
        elif status == 'enviado':
            self.notifier.send_email(p['cli'], "Pedido enviado!")
        elif status == 'entregue':
            self.notifier.send_email(p['cli'], "Pedido entregue!")
            self._award_points(p)

    def _award_points(self, p: Dict[str, Any]) -> None:
        if p['tp'] == 'vip':
            pts = int(p['tot'] * 2)
            print(f"Cliente VIP ganhou {pts} pontos!")
        elif p['tp'] == 'corporativo':
            pts = int(p['tot'] * 1.5)
            print(f"Cliente corporativo ganhou {pts} pontos!")
        else:
            pts = int(p['tot'])
            print(f"Cliente ganhou {pts} pontos!")

    def proc_pag(self, order_id: int, method: str, value: float) -> bool:
        p = self.get_ped(order_id)
        if not p:
            return False
        if value < p['tot']:
            print("Valor insuficiente!")
            return False
        
        if method == 'cartao':
            print("Processando pagamento com cartao...\nCartao validado!")
            self.upd_st(order_id, 'aprovado')
            return True
        elif method == 'pix':
            print("Gerando QR Code PIX...\nPIX recebido!")
            self.upd_st(order_id, 'aprovado')
            return True
        elif method == 'boleto':
            print("Gerando boleto...\nBoleto gerado!")
            return True
        else:
            print("Metodo de pagamento invalido!")
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
        return sum(r[3] for r in orders)

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