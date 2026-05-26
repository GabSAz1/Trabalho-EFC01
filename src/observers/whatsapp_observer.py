from typing import Dict, Any
from src.observers.notification_observer import OrderObserver
from src.services.notification_service import NotificationService

class WhatsAppNotifier(OrderObserver):
    def __init__(self, notifier: NotificationService) -> None:
        self.notifier = notifier

    def update(self, event_type: str, order_data: Dict[str, Any]) -> None:
        # A regra de"disponível para todos" é aplicada aqui, então não há necessidade de verificar o tipo de evento
        client = order_data['cli']
        print(f"WhatsApp enviado para {client}: Notificacao de evento '{event_type}'")