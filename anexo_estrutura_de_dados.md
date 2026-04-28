# Anexo: Estruturas de Dados Aplicadas no MGPEB

Este documento detalha as estruturas de dados lineares implementadas no protótipo do **Módulo de Gerenciamento de Pouso e Estabilização de Base (MGPEB)**. A escolha de cada estrutura foi fundamentada na eficiência algorítmica, no determinismo e na segurança operacional da Missão Aurora Siger, conforme os requisitos de sistemas embarcados de alta confiabilidade.

---

## 1. Fila (Queue) - Gerenciamento de Tráfego Orbital

A fila é a estrutura central para a organização dos módulos que aguardam autorização de pouso. Ela segue o princípio **FIFO (First-In, First-Out)**, garantindo que a ordem de chegada e a prioridade estabelecida sejam respeitadas.

- **Implementação:** Utiliza-se a classe `collections.deque` do Python.  
- **Justificativa Técnica:** O `deque` (double-ended queue) permite remoções à esquerda (`popleft()`) com complexidade constante **O(1)**. Em sistemas de missão crítica, evitar o deslocamento de elementos em memória (comum em listas padrão ao remover o primeiro item) é essencial para manter a previsibilidade do tempo de execução.

### 💻 Exemplo no Código:

```python
from collections import deque

# Inicialização da fila de pouso (FIFO)
fila_pouso = deque()

# Adicionando módulos à fila após ordenação por prioridade
for m in modulos_ordenados:
    fila_pouso.append(m)

# Retirando o próximo módulo para avaliação de autorização
proximo_modulo = fila_pouso.popleft()
```
---

# 2. Pilha (Stack) - Gestão de Emergências e Alertas

A pilha opera sob o princípio **LIFO (Last-In, First-Out)**. No MGPEB, ela funciona como uma estrutura para gerenciamento de situações críticas, garantindo que o evento mais recente seja tratado primeiro.

- **Implementação:** Utiliza-se uma lista dinâmica com operações `append()` e acesso ao topo.  
- **Justificativa Técnica:** Em cenários de falhas múltiplas, o evento mais recente tende a ser o mais urgente. A pilha permite priorizar rapidamente esses casos.

### 💻 Exemplo no Código:

```python
alertas = []  # Lista operando como pilha

# Se houver falha crítica, o módulo é adicionado à pilha
if status == "ALERTA":
    alertas.append(modulo)

# Processamento das emergências (LIFO)
while alertas:
    m = alertas.pop()
    print(f"TRATANDO EMERGÊNCIA: {m['nome']}")
```
---

## 3. Listas (Lists) - Armazenamento de Estados e Histórico

As listas são utilizadas para armazenar módulos que já foram processados pelo sistema, permitindo manter um histórico organizado e facilitar análises posteriores.

No MGPEB, as listas representam diferentes estados dos módulos ao longo da operação.

---

### 📌 Uso no Projeto

As listas são utilizadas para:

- Armazenar módulos que já pousaram (`pousados`);
- Armazenar módulos que tiveram o pouso adiado (`em_espera`);
- Apoiar auditorias e análises após a simulação.

---
### 💻 Exemplo no Código

```python
pousados = []
em_espera = []

# Registro de estados
pousados.append(modulo_pousado)
em_espera.append(modulo_adiado)

# Busca pelo módulo com menor combustível
menor_comb = min(pousados, key=lambda m: m["combustivel_pct"])

print(f"Módulo com menor combustível: {menor_comb['nome']}")
