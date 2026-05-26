from src.strategies.crypto_payment import CryptoPayment

def test_crypto_payment_process(capsys): # type: ignore
    payment = CryptoPayment()
    # 100 + 2% de taxa = 102.0
    result = payment.process(100.0)
    captured = capsys.readouterr()
    
    assert result is True
    assert not payment.requires_manual_approval()
    assert "102.00" in captured.out