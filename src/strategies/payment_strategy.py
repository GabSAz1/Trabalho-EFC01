from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def process(self, value: float) -> bool:
        pass
    
    @abstractmethod
    def requires_manual_approval(self) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def process(self, value: float) -> bool:
        print("Processando pagamento com cartao...\nCartao validado!")
        return True
        
    def requires_manual_approval(self) -> bool:
        return False

class PixPayment(PaymentStrategy):
    def process(self, value: float) -> bool:
        print("Gerando QR Code PIX...\nPIX recebido!")
        return True
        
    def requires_manual_approval(self) -> bool:
        return False

class BoletoPayment(PaymentStrategy):
    def process(self, value: float) -> bool:
        print("Gerando boleto...\nBoleto gerado!")
        return True
        
    def requires_manual_approval(self) -> bool:
        return True