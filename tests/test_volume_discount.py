from src.strategies.volume_discount import VolumeDiscount

def test_volume_discount_less_than_three():
    discount = VolumeDiscount()
    # 2 unidades de 10 reais = 20 reais (sem desconto)
    assert discount.calculate(10.0, 2) == 20.0

def test_volume_discount_three_or_more():
    discount = VolumeDiscount()
    # 3 unidades de 10 reais = 30 reais - 15% = 25.5
    assert discount.calculate(10.0, 3) == 25.5