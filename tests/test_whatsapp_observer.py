from src.observers.whatsapp_observer import WhatsAppNotifier
from src.services.notification_service import NotificationService

def test_whatsapp_notifier_all_clients(capsys): # type: ignore
    notifier_service = NotificationService()
    whatsapp_observer = WhatsAppNotifier(notifier_service)
    
    # Simulando um pedido normal
    order_data = {'cli': 'Joao', 'tp': 'normal', 'id': 1}
    whatsapp_observer.update('created', order_data)
    
    captured = capsys.readouterr()
    assert "WhatsApp enviado para Joao" in captured.out