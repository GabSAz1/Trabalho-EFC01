from typing import List, Dict, Any, Optional
from src.observers.notification_observer import (
    NormalClientNotifier, 
    VIPClientNotifier, 
    CorporateClientNotifier,
    SpecialClientNotifier # <-- Adicionamos o ouvinte especial aqui
)
from src.repositories.order_repository import SQLiteOrderRepository
from src.services.notification_service import NotificationService
from src.services.order_service import OrderService
from src.strategies.crypto_payment import CryptoPayment
from src.observers.whatsapp_observer import WhatsAppNotifier
from src.strategies.volume_discount import VolumeDiscount

class Sis:
    def __init__(self) -> None:
        self.repo = SQLiteOrderRepository('loja.db')
        self.notifier = NotificationService()
        self.service = OrderService(self.repo, self.notifier)
        
        # Conectando TODOS os Observers
        self.service.attach(NormalClientNotifier(self.notifier))
        self.service.attach(VIPClientNotifier(self.notifier))
        self.service.attach(CorporateClientNotifier(self.notifier))
        self.service.attach(SpecialClientNotifier(self.notifier))
        self.service.register_payment_method('cripto', CryptoPayment())
        self.service.attach(WhatsAppNotifier(self.notifier))
        self.service.register_item_discount('volume', VolumeDiscount())

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

# A classe filha agora usa as regras da classe pai (respeitando o LSP),
# apenas forçando o tipo do pedido para 'especial'.
class PedEspecial(Sis):
    """
    Agora respeita 100% o LSP. 
    Não altera fluxos de controle, apenas força o client_type para 'especial'.
    """
    def add_ped(self, n: str, its: List[Dict[str, Any]], t: str) -> int:
        return super().add_ped(n, its, 'especial')

def main() -> None:
    pass

if __name__ == '__main__':
    main()