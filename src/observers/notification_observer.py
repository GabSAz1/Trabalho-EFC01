from abc import ABC, abstractmethod
from typing import Dict, Any
from src.services.notification_service import NotificationService

# Interface do Observer
class OrderObserver(ABC):
    @abstractmethod
    def update(self, event_type: str, order_data: Dict[str, Any]) -> None:
        pass

# Implementações (Os "Ouvintes" concretos)
class NormalClientNotifier(OrderObserver):
    def __init__(self, notifier: NotificationService):
        self.notifier = notifier

    def update(self, event_type: str, order_data: Dict[str, Any]) -> None:
        if order_data['tp'] != 'normal': return
        
        client = order_data['cli']
        if event_type == 'created':
            self.notifier.send_email(client, "Pedido recebido!")
        elif event_type == 'aprovado':
            self.notifier.send_email(client, "Pedido aprovado!")
        elif event_type == 'enviado':
            self.notifier.send_email(client, "Pedido enviado!")
        elif event_type == 'entregue':
            self.notifier.send_email(client, "Pedido entregue!")
            pts = int(order_data['tot'])
            print(f"Cliente ganhou {pts} pontos!")

class VIPClientNotifier(OrderObserver):
    def __init__(self, notifier: NotificationService):
        self.notifier = notifier

    def update(self, event_type: str, order_data: Dict[str, Any]) -> None:
        if order_data['tp'] != 'vip': return
        
        client = order_data['cli']
        if event_type == 'created':
            self.notifier.send_email(client, "Pedido recebido!")
            self.notifier.send_sms(client, "Pedido VIP recebido!")
        elif event_type == 'aprovado':
            self.notifier.send_email(client, "Pedido aprovado!")
            self.notifier.send_sms(client, "Pedido aprovado!")
        elif event_type == 'enviado':
            self.notifier.send_email(client, "Pedido enviado!")
        elif event_type == 'entregue':
            self.notifier.send_email(client, "Pedido entregue!")
            pts = int(order_data['tot'] * 2)
            print(f"Cliente VIP ganhou {pts} pontos!")

class CorporateClientNotifier(OrderObserver):
    def __init__(self, notifier: NotificationService):
        self.notifier = notifier

    def update(self, event_type: str, order_data: Dict[str, Any]) -> None:
        if order_data['tp'] != 'corporativo': return
        
        client = order_data['cli']
        if event_type == 'created':
            self.notifier.send_email(client, "Pedido recebido!")
            self.notifier.notify_manager(client)
        elif event_type == 'aprovado':
            self.notifier.send_email(client, "Pedido aprovado!")
        elif event_type == 'enviado':
            self.notifier.send_email(client, "Pedido enviado!")
        elif event_type == 'entregue':
            self.notifier.send_email(client, "Pedido entregue!")
            pts = int(order_data['tot'] * 1.5)
            print(f"Cliente corporativo ganhou {pts} pontos!")