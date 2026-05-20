# Análise Textual Inicial: Violações de Princípios SOLID no Sistema Legado

Este documento apresenta a análise do código legado (`legacy.py`), identificando violações dos 5 princípios SOLID. Para cada princípio, foram mapeadas ao menos duas violações, acompanhadas de trechos de código, justificativas e impactos.

---

## 1. SRP - Single Responsibility Principle (Princípio da Responsabilidade Única)

**Violação 1: A classe `Sis` mistura acesso a banco de dados com regras de negócio.**
* **Trecho do Código:**
  ```python
  def add_ped(self, n, its, t):
      # ... (cálculo de regras de negócio, descontos, totais) ...
      self.c.execute("INSERT INTO ped (cli, itens, tot, st, dt, tp) VALUES (?, ?, ?, ?, ?, ?)", ...)

### Justificativa

A função add_ped calcula os totais (regra de negócio) e realiza operações diretas em SQL (persistência).

### Impacto

Mudanças no banco de dados (ex: migrar do SQLite para PostgreSQL) ou mudanças na regra de cálculo forçarão a alteração da mesma classe, aumentando o risco de quebrar o sistema.

---

## Violação 2: A classe `Sis` é responsável pelo envio de notificações

### Trecho do código

```python
if s == 'entregue': 
    print(f"Email enviado para {p['cli']}: Pedido entregue!")
```

### Justificativa

Regras de comunicação (Email, SMS) estão acopladas à lógica de atualização de status do pedido.

### Impacto

Se o sistema precisar integrar com uma API real de SMS (como Twilio) ou um servidor SMTP, a classe central de pedidos precisará ser alterada e inflada com lógicas de rede.

---

# 2. OCP - Open/Closed Principle (Princípio do Aberto/Fechado)

---

## Violação 1: Cálculo de descontos engessado por condicinais

### Trecho do código

```python
if i['tipo'] == 'normal': tot += i['p'] * i['q']
elif i['tipo'] == 'desc10': tot += i['p'] * i['q'] * 0.9
elif i['tipo'] == 'desc20': tot += i['p'] * i['q'] * 0.8
```

### Justificativa

A classe não está fechada para modificação. Para adicionar um novo tipo de desconto (ex: desc50 ou black_friday), é obrigatório modificar o método add_ped.

### Impacto

O código cresce infinitamente em blocos if/elif, tornando a manutenção perigosa e complexa.

---

## Violação 2: Processamento de pagamentos centralizado via `if/elif`

### Trecho do código

```python
if m == 'cartao': ...
elif m == 'pix': ...
elif m == 'boleto': ...
```

### Justificativa

Novamente, adicionar um método "PayPal" ou "Cripto" exigiria alterar o método proc_pag.

### Impacto

Fere o OCP, pois o sistema deveria permitir a adição de novas estratégias de pagamento por extensão (polimorfismo/injeção), não por modificação direta do código central.

---

# 3. LSP - Liskov Substitution Principle (Princípio da Substituição de Liskov)

---

## Violação 1: `PedEspecial` altera a regra de cálculo de descontos da superclasse silenciosamente.

### Trecho do código Em `PedEspecial.add_ped`:

```python
tot = tot * 1.15
```

### Justificativa

A subclasse PedEspecial sobrescreve a adição de pedidos, mas ignora o tipo frete_gratis que existe na base, além de injetar uma taxa oculta de 15%.

### Impacto

Se o cliente do código (a função main) usar PedEspecial achando que é um objeto Sis comum, receberá resultados matemáticos totalmente inesperados.

---

## Violação 2: `PedEspecial` quebra as transições de estado e comportamentos pós-condicionais.

### Trecho do código Em `PedEspecial.upd_st`:

```python
# PedEspecial atualiza estado sem seguir regras do pai
```

### Justificativa

A classe base Sis dispara notificações e distribui pontos de fidelidade no upd_st. A classe filha PedEspecial sobrescreve o método sem implementar esses comportamentos (apenas faz o UPDATE no banco e um print simples).

### Impacto

O comportamento da classe derivada não é um subtipo válido da classe base. Partes do sistema que esperam que clientes ganhem pontos ao usar o upd_st falharão ao operar com PedEspecial.

---

# 4. ISP - Interface Segregation Principle (Princípio da Segregação de Interfaces)

---

## Violação 1: Interface "Faz Tudo" (God Class).

### Trecho do código

A classe Sis contém métodos como add_ped, upd_st, proc_pag, gerar_rel, validar_estoque.

### Justificativa

Embora Python não possua o conceito estrito de interface nativa, a assinatura da classe Sis expõe métodos que atendem a domínios completamente diferentes.

### Impacto

Um módulo do sistema que apenas necessita gerar relatórios de clientes (gerar_rel) é forçado a depender de métodos de banco, estoque e pagamento, aumentando o acoplamento.

---

## Violação 2: Validação de estoque amarrada a operações de pedido.

### Trecho do código

```python
def validar_estoque(self, its):
```

### Justificativa

Uma classe de serviço que lida com inventário seria forçada a instanciar ou conhecer a classe de gestão financeira/pedidos (Sis), pois a interface não está segregada.

### Impacto

Dificulta a separação de times e microsserviços. A lógica de estoque está presa à interface de pedidos.

---

# 5. DIP - Dependency Inversion Principle (Princípio da Inversão de Dependência)

---

## Violação 1: Dependência direta da implementação de Banco de Dados de baixo nível.

### Trecho do código

```python
def __init__(self):
    self.db = sqlite3.connect('loja.db')
```

### Justificativa

A classe de alto nível (regras de negócio da loja) depende diretamente de um módulo de baixo nível (sqlite3), em vez de depender de uma abstração (como uma interface IRepository).

### Impacto

Impossibilita testar a lógica de negócios sem acionar o disco, e torna a troca de banco de dados no futuro uma tarefa extremamente custosa.

---

## Violação 2: Dependência direta de dados engessados de integrações externas

### Trecho do código

```python
def validar_estoque(self, its):
    # TODO: integrar com sistema de estoque externo 
    est = {'produto1': 100, 'produto2': 50, 'produto3': 75}
```

### Justificativa

A classe depende de uma estrutura de dados concreta local no lugar de depender de um contrato (Interface de Integração de Estoque).

### Impacto

Não é possível plugar um sistema real (via API REST ou gRPC) sem abrir a classe central do sistema e substituir o código fonte.

---

