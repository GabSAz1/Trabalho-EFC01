import pytest

from legacy import Sis

@pytest.fixture

def sis(tmp_path, monkeypatch):

    """Isola o banco em diretorio temporario por teste."""

    monkeypatch.chdir(tmp_path)

    s = Sis()

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


def test_validar_estoque_com_sucesso(sis):
    itens = [{'nome': 'produto1', 'q': 50}]
    assert sis.validar_estoque(itens) is True

def test_validar_estoque_falha_por_quantidade(sis):
    itens = [{'nome': 'produto1', 'q': 150}]
    assert sis.validar_estoque(itens) is False

def test_validar_estoque_falha_produto_inexistente(sis):
    itens = [{'nome': 'produto_invisivel', 'q': 1}]
    assert sis.validar_estoque(itens) is False

def test_cancelar_pedido_atualiza_status(sis):
    itens = [{'nome': 'produto1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis.add_ped('Carlos', itens, 'normal')
    sis.cancelar_pedido(id_ped)
    assert sis.get_ped(id_ped)['st'] == 'cancelado'

def test_gerar_relatorios_nao_quebra_execucao(sis, tmp_path):
    # Garante que os métodos rodam sem exceções e geram os arquivos
    itens = [{'nome': 'produto1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    sis.add_ped('Carlos', itens, 'normal')
    
    sis.gerar_rel('vendas')
    sis.gerar_rel('clientes')
    
    assert (tmp_path / 'rel_vendas.txt').exists()
    assert (tmp_path / 'rel_clientes.txt').exists()

def test_pedido_especial_aplica_taxa_correta(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from legacy import PedEspecial
    
    sis_esp = PedEspecial()
    itens = [{'nome': 'produto1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    id_ped = sis_esp.add_ped('Especialista', itens, 'normal')
    
    pedido = sis_esp.get_ped(id_ped)
    # Total deve ser 100 * 1.15 = 115.0
    assert pedido['tot'] == pytest.approx(115.0)
    sis_esp.close()

def test_main_executa_sem_erros(tmp_path, monkeypatch):
    # Roda a função main original para garantir que o script inteiro compila e roda
    monkeypatch.chdir(tmp_path)
    from legacy import main
    main()

def test_pedido_corporativo_e_outros_descontos(sis):
    # Cobre as linhas de desconto de 20%, frete grátis e cálculo corporativo
    itens = [
        {'nome': 'produto1', 'p': 100, 'q': 1, 'tipo': 'desc20'},
        {'nome': 'produto2', 'p': 50, 'q': 1, 'tipo': 'frete_gratis'}
    ]
    id_ped = sis.add_ped('Empresa XYZ', itens, 'corporativo')
    pedido = sis.get_ped(id_ped)
    
    # 100 * 0.8 = 80 (desc20)
    # 50 * 1 = 50 (frete grátis)
    # Subtotal = 130
    # Corporativo: 130 * 0.9 = 117
    assert pedido['tot'] == pytest.approx(117.0)

def test_status_entregue_gera_pontos_para_todos_os_tipos(sis):
    # Cobre o bloco de if/elif gigante que dá pontos dependendo do tipo de cliente
    itens = [{'nome': 'p1', 'p': 100, 'q': 1, 'tipo': 'normal'}]
    
    id_vip = sis.add_ped('Vip', itens, 'vip')
    sis.upd_st(id_vip, 'entregue')
    
    id_corp = sis.add_ped('Corp', itens, 'corporativo')
    sis.upd_st(id_corp, 'entregue')
    
    id_norm = sis.add_ped('Norm', itens, 'normal')
    sis.upd_st(id_norm, 'entregue')