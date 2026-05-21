from abc import ABC, abstractmethod

# --- Estratégias de Desconto por Item ---
class ItemDiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, price: float, quantity: int) -> float:
        pass

class NormalDiscount(ItemDiscountStrategy):
    def calculate(self, price: float, quantity: int) -> float:
        return price * quantity

class Discount10(ItemDiscountStrategy):
    def calculate(self, price: float, quantity: int) -> float:
        return price * quantity * 0.9

class Discount20(ItemDiscountStrategy):
    def calculate(self, price: float, quantity: int) -> float:
        return price * quantity * 0.8

class FreeShipping(ItemDiscountStrategy):
    def calculate(self, price: float, quantity: int) -> float:
        return price * quantity

# --- Estratégias de Desconto no Pedido Total ---
class OrderDiscountStrategy(ABC):
    @abstractmethod
    def apply_discount(self, total: float) -> float:
        pass

class VIPOrderDiscount(OrderDiscountStrategy):
    def apply_discount(self, total: float) -> float:
        return total * 0.95

class CorpOrderDiscount(OrderDiscountStrategy):
    def apply_discount(self, total: float) -> float:
        return total * 0.90

class NormalOrderDiscount(OrderDiscountStrategy):
    def apply_discount(self, total: float) -> float:
        return total
    
class SpecialOrderDiscount(OrderDiscountStrategy):
    def apply_discount(self, total: float) -> float:
        return total * 1.15