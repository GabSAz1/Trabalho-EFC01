# Análise Textual Inicial: Violações de Princípios SOLID no Sistema Legado

Este documento apresenta a análise do código legado (`legacy.py`), identificando violações dos 5 princípios SOLID. Para cada princípio, foram mapeadas ao menos duas violações, acompanhadas de trechos de código, justificativas e impactos.

---

# 1. SRP - Single Responsibility Principle (Princípio da Responsabilidade Única)

---
## Violação 1: A classe `Sis` mistura acesso a banco de dados com regras de negócio.

### Trecho do Código:

```python
  def add_ped(self, n, its, t):
      # ... (cálculo de regras de negócio, descontos, totais) ...
      self.c.execute("INSERT INTO ped (cli, itens, tot, st, dt, tp) VALUES (?, ?, ?, ?, ?, ?)", ...)
```
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


# Análise de Padrões de Projeto GoF Aplicados

Para garantir a modularidade, o respeito aos princípios SOLID (especialmente OCP, LSP e DIP) e a manutenibilidade do software, foram aplicados e integrados quatro padrões de projeto clássicos do GoF na refatoração do sistema.

---

# 1. Padrão: Strategy (Comportamental)

## Intenção segundo GoF: Definir uma família de algoritmos, encapsular cada um deles e torná-los intercambiáveis. O Strategy permite que o algoritmo varie independentemente dos clientes que o utilizam.

### Classes e Interfaces Criadas/Modificadas:
* `ItemDiscountStrategy` (Interface/Classe Abstrata)
  * *Implementações:* `NormalDiscount`, `Discount10`, `Discount20`, `VolumeDiscount` (Extensão Obrigatória 3)
* `OrderDiscountStrategy` (Interface/Classe Abstrata)
  * *Implementações:* `VIPOrderDiscount`, `CorpOrderDiscount`, `NormalOrderDiscount`, `SpecialOrderDiscount`
* `PaymentStrategy` (Interface/Classe Abstrata)
  * *Implementações:* `CreditCardPayment`, `PixPayment`, `BoletoPayment`, `CryptoPayment` (Extensão Obrigatória 1)
* `OrderService` (Contexto que armazena e consome as estratégias dinamicamente)

### Justificativa de Aplicação:
O sistema legado calculava taxas de pagamento e descontos através de blocos condicionais aninhados (`if/elif`). Com o *Strategy*, isolamos cada regra de cálculo em sua própria classe. Isso permitiu, por exemplo, implementar o pagamento em *Criptomoeda* (com taxa de 2%) e o *Desconto por Volume* (15% para 3 ou mais itens) de forma puramente aditiva (OCP), registrando as novas estratégias no `OrderService` sem tocar em uma única linha de código existente, mantendo os testes originais intactos.

### Diagrama Parcial (PlantUML):
```plantuml
interface PaymentStrategy {
    + process(value: float): bool
    + requires_manual_approval(): bool
}
class CreditCardPayment implements PaymentStrategy
class CryptoPayment implements PaymentStrategy
class OrderService {
    - payment_methods: Map<String, PaymentStrategy>
    + register_payment_method(name, strategy)
}
OrderService --> PaymentStrategy
```

--- 

# 2. Padrão: Observer (Comportamental)

## Intenção segundo GoF: Definir uma dependência um-para-muitos entre objetos, de modo que, quando um objeto muda de estado, todos os seus dependentes são notificados e atualizados automaticamente.

### Classes e Interfaces Criadas/Modificadas:
  * `OrderObserver` (Interface/Classe Abstrata do Ouvinte)
  * `NormalClientNotifier`, `VIPClientNotifier`, `CorporateClientNotifier`, `SpecialClientNotifier` (Ouvintes Base)
  * `WhatsAppNotifier` (Extensão Obrigatória 2 - Disponível para todos os clientes)
  * `OrderService` (O "Sujeito" ou Subject observável)
  
  
### Justificativa de Aplicação: No código original, o envio de e-mails e a impressão de relatórios de pontos disparavam regras de negócio confusas e acopladas ao fluxo do pedido. Ao transformar o `OrderService` em um Subject (com os métodos `attach` e a chamada aos ouvintes durante transições de status), desacoplamos o canal de comunicação da regra central. O canal WhatsApp foi adicionado criando unicamente a classe `WhatsAppNotifier` e assinando-a no ciclo de vida do sistema, estendendo o comportamento sem violar o OCP.

### Diagrama Parcial (PlantUML):
```plantuml
interface OrderObserver {
    + update(event_type: str, order_data: dict)
}
class NormalClientNotifier implements OrderObserver
class WhatsAppNotifier implements OrderObserver
class OrderService {
    - _observers: List<OrderObserver>
    + attach(observer: OrderObserver)
    + upd_st(id: int, s: str)
}
OrderService "1" *-- "*" OrderObserver
```

---

# 3. Padrão: Repository (Arquitetural / Enterprise Patterns)

## Intenção Comercial/Arquitetural: Isolar a camada de domínio e as regras de negócio dos detalhes de acesso a dados e persistência, fornecendo uma interface herdeira de coleção para o modelo de domínio.

### Classes e Interfaces Criadas/Modificadas:
  * `IOrderRepository` (Interface que define o contrato de persistência)
  * `SQLiteOrderRepository` (Implementação concreta utilizando SQLite)
  * `OrderService` (Cliente de alto nível que depende apenas da interface)
  
  
### Justificativa de Aplicação: O sistema misturava a execução de queries SQL literais (`INSERT`, `SELECT`, `UPDATE`) diretamente no meio dos fluxos lógicos. Aplicando o Repository em conjunto com o DIP (Dependency Inversion Principle), o `OrderService` passou a conversar apenas com a abstração `IOrderRepository`. Isso isolou os testes unitários da escrita em disco e garante que, caso o banco de dados mude no futuro, o núcleo do negócio permaneça intacto.

### Diagrama Parcial (PlantUML):
```plantuml
interface IOrderRepository {
    + save(payload: dict): int
    + get_by_id(id: int): dict
    + update_status(id: int, status: str)
}
class SQLiteOrderRepository implements IOrderRepository
class OrderService {
    - repo: IOrderRepository
}
OrderService --> IOrderRepository
```

---

# 4. Padrão: Factory Method (Criacional)

## Intenção segundo GoF: Definir uma interface para criar um objeto, mas deixar as subclasses decidirem que classe instanciar. O Factory Method permite adiar a instanciação para subclasses.

### Classes e Interfaces Criadas/Modificadas:
  * Dataclass `Order` (Modelo de Domínio)
  * Método `@staticmethod create_payload` (O método fábrica de payloads)
  * Método `@classmethod from_tuple` (Fábrica secundária para desserialização do banco)
  
  
### Justificativa de Aplicação: Os pedidos possuem diferentes layouts de dicionários e metadados dependendo do tipo do cliente (chaves como `cli`, `itens`, `tot`, `st`, `dt`, `tp`). Em vez de espalhar a fabricação manual dessa estrutura complexa por todo o código, centralizamos a responsabilidade no modelo `Order`. Qualquer alteração estrutural no contrato do pedido é modificada centralizadamente no método fábrica, blindando o `OrderService`.

### Diagrama Parcial (PlantUML):
```plantuml
class Order {
    + id: int
    + client: str
    + total: float
    {static} + create_payload(client, items, total, client_type): dict
    {static} + from_tuple(data: tuple): Order
}
class OrderService {
    + add_ped()
}
OrderService ..> Order : usa métodos de fabricação
```


---

# Justificativa da Estrutura de Arquitetura Adotada

## A estrutura final do projeto divergiu levemente da sugestão inicial garantindo a aprovação contínua dos testes Golden Master.

### As principais adaptações foram:

Ausência de customer.py e order_item.py (Models): O sistema legado operava perfeitamente recebendo dicionários simples para itens e strings para clientes. Para manter a compatibilidade retroativa e evitar overhead de conversão (Data Transfer Objects), optou-se por manter a tipagem forte (List[Dict[str, Any]]) no OrderService, dispensando a criação de classes de domínio anêmicas que não teriam comportamento adicional.

Ausência de payment_service.py: Com a implementação do padrão Strategy (PaymentStrategy), a lógica de processamento e taxas foi totalmente encapsulada nas próprias estratégias (CreditCardPayment, CryptoPayment, etc.). O OrderService atua como o contexto da estratégia, tornando a criação de um "Service" intermediário para pagamentos uma abstração redundante.

Inclusão de Novos Arquivos de Extensão: Foram adicionados arquivos granulares e independentes (crypto_payment.py, whatsapp_observer.py, volume_discount.py) e suas respectivas suítes de testes isoladas. Isso prova de forma empírica o respeito ao OCP (Open/Closed Principle), onde novas funcionalidades ganharam seus próprios módulos sem inchar os diretórios base.

---

# Uso Transparente de Inteligência Artificial e Reflexão Metacognitiva

## Em conformidade com as diretrizes acadêmicas da disciplina, declara-se o uso transparente de Inteligência Artificial Conversacional (LLM) como copiloto de desenvolvimento durante a Sprint 2.

### Escopo de Atuação da IA:

1. Suporte de Refatoração: Auxílio no mapeamento inicial das violações do SOLID no código legado e isolamento da camada SQL para o padrão Repository.

2. Revisão Estatística de Tipagem: Apoio na depuração de erros apontados pelo `mypy --strict` relacionados a tipos genéricos (`Any` e `Dict[str, Any]`) vindos do banco de dados SQLite.

3. Validação OCP: Orientação no design do mecanismo de injeção de dependências em dicionários dinâmicos dentro do `OrderService`, garantindo que as três extensões obrigatórias pudessem ser integradas de forma 100% aditiva.

### Reflexão Metacognitiva do Grupo:

O processo de refatoração trouxe um entendimento prático sobre o custo de um código altamente acoplado. No início do projeto, alterar uma query SQL quebrava o cálculo de descontos. A aplicação de padrões arquiteturais como o Strategy e o Observer demonstrou que o esforço inicial de abstração se paga rapidamente: a implementação das três extensões obrigatórias (cripto, WhatsApp e desconto progressivo), que poderia ser complexa e gerar regressões no modelo antigo, foi realizada de forma trivial através de novas classes, comprovando o real valor do Open/Closed Principle (OCP).

---