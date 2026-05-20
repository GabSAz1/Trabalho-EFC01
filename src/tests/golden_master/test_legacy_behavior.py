import pytest

from legacy import Sis

@pytest.fixture

def sis(tmp_path, monkeypatch):

    """Isola o banco em diretorio temporario por teste."""

    monkeypatch.chdir(tmp_path)

    S = Sis()

    yield s

    s.close()

def test_pedido_normal_calcula_total_corretamente (sis):

    itens = [
        {'nome': 'produto1', 'p': 100, 'q': 2, 'tipo': 'normal'}, 
        {'nome': 'produto2', 'p': 50, 'q': 1, 'tipo': 'desc10'},
    ]

    id_ped = sis.add_ped ('Joao Silva', itens, 'normal')

    pedido = sis.get_ped(id_ped)

    assert pedido ['tot'] == pytest.approx (245.0)
    assert pedido ['st'] == 'pendente'


def test_pedido_vip_aplica_desconto_de_5_por_cento (sis):

    itens = [{'nome': '1', 'p': 100, 'q': 1, 'tipo': 'normal'}]

    id_ped = sis.add_ped('Maria', itens, 'vip')

    pedido = sis.get_ped(id_ped)

    assert pedido ['tot'] == pytest.approx (95.0)


def test_pagamento_insuficiente_falha(sis):

    itens = [{'nome': '1', 'p': 100, 'q': 1, 'tipo': 'normal'}]

    id_ped = sis.add_ped ('Joao', itens, 'normal')

    assert sis.proc_pag(id_ped, 'cartao', 50) is False

def test_pix_aprova_pedido_automaticamente (sis):

    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]

    id_ped = sis.add_ped ('Joao', itens, 'normal')

    sis.proc_pag(id_ped, 'pix', 100)

    assert sis.get_ped(id_ped) ['st'] == 'aprovado'


def test_boleto_nao_aprova_automaticamente (sis):

    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]

    id_ped = sis.add_ped ('Joao', itens, 'normal')
    sis.proc_pag(id_ped, 'boleto', 100)

    assert sis.get_ped(id_ped) ['st'] == 'pendente'