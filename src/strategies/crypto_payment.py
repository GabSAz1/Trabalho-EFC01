from src.strategies.payment_strategy import PaymentStrategy

class CryptoPayment(PaymentStrategy):
    def process(self, value: float) -> bool:
        fee = value * 0.02
        total = value + fee
        print(f"Processando pagamento em Criptomoeda. Valor com taxa (2%): R${total:.2f}")
        return True
        
    def requires_manual_approval(self) -> bool:
        return False