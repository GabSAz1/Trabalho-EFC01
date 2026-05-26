from src.strategies.discount_strategy import ItemDiscountStrategy

class VolumeDiscount(ItemDiscountStrategy):
    def calculate(self, price: float, quantity: int) -> float:
        base_total = price * quantity
        if quantity >= 3:
            return base_total * 0.85 # 15% de desconto
        return base_total