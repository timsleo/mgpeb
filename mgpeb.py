"""
=============================================================
 MGPEB — Módulo de Gerenciamento de Pouso e Estabilização
         de Base | Missão Aurora Siger
=============================================================
Protótipo em Python que simula o sistema de fila de módulos,
autorização de pouso, busca, ordenação e modelagem matemática
da descida.

Bibliotecas utilizadas: numpy (geração aleatória), collections
(deque para fila), math (cálculos de descida).
"""

import numpy as np
import math
from collections import deque

np.random.seed()   # seed aleatória a cada execução

# ─────────────────────────────────────────────────────────────
# 1. DEFINIÇÃO DOS MÓDULOS
# ─────────────────────────────────────────────────────────────
# Prioridade fixa por tipo (1 = mais urgente):
#   1 - Suporte Médico   (vida humana)
#   2 - Habitação        (sobrevivência imediata)
#   3 - Energia          (infraestrutura crítica)
#   4 - Laboratório      (operação científica)
#   5 - Logística        (suporte operacional)

MODULOS_BASE = [
    {"nome": "Aurora-Med-01",  "tipo": "Suporte Médico",  "prioridade": 1},
    {"nome": "Aurora-Hab-01",  "tipo": "Habitação",       "prioridade": 2},
    {"nome": "Aurora-Ene-01",  "tipo": "Energia",         "prioridade": 3},
    {"nome": "Aurora-Lab-01",  "tipo": "Laboratório",     "prioridade": 4},
    {"nome": "Aurora-Log-01",  "tipo": "Logística",       "prioridade": 5},
]

def gerar_atributos_aleatorios():
    """
    Gera atributos numéricos aleatórios via np.random para
    cada módulo. Executado a cada inicialização do sistema,
    tornando cada simulação única.
    """
    return {
        # Combustível restante: 10% a 100%
        "combustivel_pct":        round(np.random.uniform(10.0, 100.0), 1),
        # Massa total do módulo: 2.000 a 12.000 kg
        "massa_kg":               int(np.random.randint(2000, 12001)),
        # Integridade dos sensores: 0.0 (falha total) a 1.0 (perfeita)
        "integridade_sensores":   round(np.random.uniform(0.0, 1.0), 2),
        # Horário estimado de chegada à órbita: 0h a 23h59
        "hora_chegada_orbita":    f"{np.random.randint(0,24):02d}:{np.random.randint(0,60):02d}",
        # Criticidade da carga: 1 (baixa) a 5 (extrema)
        "criticidade_carga":      int(np.random.randint(1, 6)),
        # Condição atmosférica simulada: 0 (tempestade) a 1 (limpa)
        "cond_atmosferica":       round(np.random.uniform(0.0, 1.0), 2),
        # Disponibilidade da área de pouso (booleano simulado)
        "area_pouso_disponivel":  bool(np.random.choice([True, False], p=[0.8, 0.2])),
    }

def criar_modulos():
    """Instancia os 5 módulos com atributos aleatórios."""
    modulos = []
    for base in MODULOS_BASE:
        modulo = base.copy()
        modulo.update(gerar_atributos_aleatorios())
        modulos.append(modulo)
    return modulos

# ─────────────────────────────────────────────────────────────
# 2. ESTRUTURAS DE DADOS LINEARES
# ─────────────────────────────────────────────────────────────

def inicializar_estruturas(modulos):
    """
    Organiza os módulos nas estruturas lineares:
      - fila_pouso  : deque — módulos aguardando autorização (FIFO)
      - pousados    : lista — módulos que concluíram o pouso
      - em_espera   : lista — módulos adiados (condição não atendida)
      - alertas     : lista (pilha) — módulos em situação crítica (LIFO)
    """
    fila_pouso = deque()
    pousados   = []
    em_espera  = []
    alertas    = []   # usado como pilha: append/pop

    # Ordena por prioridade antes de enfileirar
    for m in sorted(modulos, key=lambda x: x["prioridade"]):
        fila_pouso.append(m)

    return fila_pouso, pousados, em_espera, alertas

# ─────────────────────────────────────────────────────────────
# 3. REGRAS LÓGICAS DE AUTORIZAÇÃO DE POUSO
# ─────────────────────────────────────────────────────────────
# Expressão booleana completa:
#
# AUTORIZADO = (combustivel >= 20%)
#          AND (integridade_sensores >= 0.6)
#          AND (cond_atmosferica >= 0.4)
#          AND (area_pouso_disponivel == True)
#
# ALERTA     = (combustivel < 20%) OR (integridade_sensores < 0.3)
#
# Portas lógicas aplicadas:
#   AND  → todas as condições críticas devem ser verdadeiras
#   OR   → qualquer condição de alerta envia para pilha de alertas
#   NOT  → inversão da disponibilidade da área bloqueia o pouso

def avaliar_pouso(modulo):
    """
    Aplica as regras booleanas e retorna:
      'AUTORIZADO', 'ADIADO' ou 'ALERTA'
    """
    comb_ok     = modulo["combustivel_pct"]      >= 20.0   # AND
    sensor_ok   = modulo["integridade_sensores"] >= 0.6    # AND
    atmo_ok     = modulo["cond_atmosferica"]     >= 0.4    # AND
    area_ok     = modulo["area_pouso_disponivel"]          # AND / NOT (se False)

    # Condições de alerta (OR entre situações críticas)
    alerta_comb   = modulo["combustivel_pct"]      < 20.0
    alerta_sensor = modulo["integridade_sensores"] < 0.3

    em_alerta = alerta_comb or alerta_sensor   # porta OR

    if em_alerta:
        return "ALERTA"
    elif comb_ok and sensor_ok and atmo_ok and area_ok:  # porta AND
        return "AUTORIZADO"
    else:
        return "ADIADO"

# ─────────────────────────────────────────────────────────────
# 4. ALGORITMOS DE BUSCA
# ─────────────────────────────────────────────────────────────

def buscar_menor_combustivel(modulos):
    """Busca linear — retorna o módulo com menor combustível."""
    if not modulos:
        return None
    return min(modulos, key=lambda m: m["combustivel_pct"])

def buscar_maior_prioridade(modulos):
    """Busca linear — retorna o módulo de maior prioridade (menor número)."""
    if not modulos:
        return None
    return min(modulos, key=lambda m: m["prioridade"])

def buscar_por_tipo(modulos, tipo):
    """Busca linear — retorna todos os módulos de um determinado tipo."""
    return [m for m in modulos if m["tipo"].lower() == tipo.lower()]

# ─────────────────────────────────────────────────────────────
# 5. ALGORITMOS DE ORDENAÇÃO
# ─────────────────────────────────────────────────────────────

def ordenar_por_prioridade(modulos):
    """Ordenação por seleção (selection sort) — prioridade crescente."""
    lista = list(modulos)
    n = len(lista)
    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            if lista[j]["prioridade"] < lista[idx_min]["prioridade"]:
                idx_min = j
        lista[i], lista[idx_min] = lista[idx_min], lista[i]
    return lista

def ordenar_por_combustivel(modulos):
    """Ordenação por inserção (insertion sort) — combustível crescente."""
    lista = list(modulos)
    for i in range(1, len(lista)):
        chave = lista[i]
        j = i - 1
        while j >= 0 and lista[j]["combustivel_pct"] > chave["combustivel_pct"]:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = chave
    return lista

# ─────────────────────────────────────────────────────────────
# 6. MODELAGEM MATEMÁTICA — ALTURA EM FUNÇÃO DO TEMPO
# ─────────────────────────────────────────────────────────────
# Função quadrática de descida:
#   h(t) = h0 - v0*t - (1/2)*a*t^2
#
# Onde:
#   h0 = altitude inicial (m)
#   v0 = velocidade inicial de descida (m/s)
#   a  = desaceleração dos retrofoguetes (m/s²)
#   t  = tempo decorrido (s)
#
# O pouso ocorre quando h(t) <= 0.

def gerar_parametros_descida():
    """
    Gera aleatoriamente os parâmetros físicos da descida via np.random.

    Faixas realistas para um módulo interplanetário em Marte:
      h0 : 8.000 a 15.000 m  — altitude de início da descida controlada
      v0 : 150 a 300 m/s     — velocidade de entrada na fase final
      a  : 4.0 a 9.0 m/s²   — desaceleração dos retrofoguetes
    """
    h0 = round(np.random.uniform(8000, 15000), 0)
    v0 = round(np.random.uniform(150, 300), 1)
    a  = round(np.random.uniform(4.0, 9.0), 2)
    return h0, v0, a

def altura_em_funcao_do_tempo(t, h0, v0, a):
    """
    Calcula a altura do módulo em função do tempo de descida.

    Parâmetros:
      t  : tempo decorrido desde o início da descida (s)
      h0 : altitude inicial (m)      — gerado aleatoriamente
      v0 : velocidade inicial (m/s)  — gerada aleatoriamente
      a  : desaceleração (m/s²)      — gerada aleatoriamente

    Retorna:
      altura em metros (mínimo 0)
    """
    h = h0 - v0 * t - 0.5 * a * (t ** 2)
    return max(h, 0.0)

def simular_descida(h0, v0, a, intervalo=10):
    """
    Simula a descida e retorna os instantes de tempo e alturas.
    Determina também o instante de toque no solo.
    """
    # Tempo de toque: resolver h0 - v0*t - 0.5*a*t² = 0
    # Usando fórmula de Bhaskara: 0.5*a*t² + v0*t - h0 = 0
    delta = v0**2 + 4 * (0.5 * a) * h0
    t_pouso = (-v0 + math.sqrt(delta)) / (2 * 0.5 * a)

    tempos  = list(range(0, int(t_pouso) + intervalo, intervalo))
    alturas = [altura_em_funcao_do_tempo(t, h0, v0, a) for t in tempos]

    return tempos, alturas, round(t_pouso, 1)

# ─────────────────────────────────────────────────────────────
# 7. SIMULAÇÃO PRINCIPAL DO MGPEB
# ─────────────────────────────────────────────────────────────

def imprimir_separador(char="=", n=62):
    print(char * n)

def imprimir_modulo(m, idx=None):
    prefixo = f"[{idx}] " if idx is not None else "    "
    print(f"{prefixo}{m['nome']} | Tipo: {m['tipo']}")
    print(f"      Prioridade: {m['prioridade']} | Combustível: {m['combustivel_pct']}%"
          f" | Massa: {m['massa_kg']} kg")
    print(f"      Sensores: {m['integridade_sensores']} | Atmosfera: {m['cond_atmosferica']}"
          f" | Área OK: {m['area_pouso_disponivel']}")
    print(f"      Chegada à órbita: {m['hora_chegada_orbita']}"
          f" | Criticidade carga: {m['criticidade_carga']}/5")

def executar_simulacao():
    imprimir_separador()
    print("   MGPEB — Missão Aurora Siger")
    print("   Módulo de Gerenciamento de Pouso e Estabilização de Base")
    imprimir_separador()

    # ── Geração dos módulos ──────────────────────────────────
    print("\n[1] GERANDO MODULOS COM ATRIBUTOS ALEATORIOS...\n")
    modulos = criar_modulos()
    for i, m in enumerate(modulos, 1):
        imprimir_modulo(m, i)
        print()

    # ── Estruturas de dados ──────────────────────────────────
    fila_pouso, pousados, em_espera, alertas = inicializar_estruturas(modulos)

    imprimir_separador("-", 62)
    print(f"[2] FILA DE POUSO INICIAL ({len(fila_pouso)} módulos — ordem por prioridade):")
    for m in fila_pouso:
        print(f"    → {m['nome']} (Prioridade {m['prioridade']})")

    # ── Simulação da fila ────────────────────────────────────
    print("\n" + "-" * 62)
    print("[3] SIMULANDO AUTORIZAÇÕES DE POUSO...\n")

    while fila_pouso:
        modulo = fila_pouso.popleft()   # FIFO
        decisao = avaliar_pouso(modulo)

        print(f"  Módulo: {modulo['nome']}")
        print(f"  Combustível: {modulo['combustivel_pct']}% | "
              f"Sensores: {modulo['integridade_sensores']} | "
              f"Atmosfera: {modulo['cond_atmosferica']} | "
              f"Área: {modulo['area_pouso_disponivel']}")
        print(f"  >>> Decisão: {decisao}")

        if decisao == "AUTORIZADO":
            pousados.append(modulo)
            print(f"  ✔ {modulo['nome']} POUSOU com sucesso.\n")
        elif decisao == "ADIADO":
            em_espera.append(modulo)
            print(f"  ⏸ {modulo['nome']} ADIADO — condições não atendidas.\n")
        else:  # ALERTA
            alertas.append(modulo)   # empilha
            print(f"  ⚠ {modulo['nome']} EM ALERTA — enviado à pilha de emergência.\n")

    # ── Resultados das estruturas ────────────────────────────
    imprimir_separador("-", 62)
    print("[4] ESTADO DAS ESTRUTURAS AO FINAL DA SIMULAÇÃO:\n")
    print(f"  Pousados    ({len(pousados)} módulos): "
          + ", ".join(m["nome"] for m in pousados) if pousados else "  Pousados: nenhum")
    print(f"  Em espera   ({len(em_espera)} módulos): "
          + ", ".join(m["nome"] for m in em_espera) if em_espera else "  Em espera: nenhum")
    print(f"  Alertas     ({len(alertas)} módulos — topo da pilha primeiro):")
    for m in reversed(alertas):   # leitura da pilha: último empilhado = mais urgente
        print(f"    [ALERTA] {m['nome']} — Combustível: {m['combustivel_pct']}%"
              f" | Sensores: {m['integridade_sensores']}")

    # ── Buscas ───────────────────────────────────────────────
    todos = modulos
    imprimir_separador("-", 62)
    print("[5] RESULTADOS DE BUSCA:\n")

    menor_comb = buscar_menor_combustivel(todos)
    if menor_comb:
        print(f"  Menor combustível : {menor_comb['nome']} → {menor_comb['combustivel_pct']}%")

    maior_prior = buscar_maior_prioridade(todos)
    if maior_prior:
        print(f"  Maior prioridade  : {maior_prior['nome']} (Prioridade {maior_prior['prioridade']})")

    tipo_busca = "Energia"
    resultado_tipo = buscar_por_tipo(todos, tipo_busca)
    nomes_encontrados = [m["nome"] for m in resultado_tipo]
    print(f"  Busca por tipo '{tipo_busca}': {nomes_encontrados if nomes_encontrados else 'nenhum encontrado'}")

    # ── Ordenações ───────────────────────────────────────────
    imprimir_separador("-", 62)
    print("[6] REORDENAÇÃO DA FILA:\n")

    ord_prior = ordenar_por_prioridade(todos)
    print("  Por prioridade (selection sort):")
    for m in ord_prior:
        print(f"    Prioridade {m['prioridade']} → {m['nome']}")

    ord_comb = ordenar_por_combustivel(todos)
    print("\n  Por combustível crescente (insertion sort):")
    for m in ord_comb:
        print(f"    {m['combustivel_pct']}% → {m['nome']}")

    # ── Modelagem matemática ─────────────────────────────────
    imprimir_separador("-", 62)
    print("[7] MODELAGEM MATEMATICA — DESCIDA DO MÓDULO:\n")

    h0, v0, a = gerar_parametros_descida()
    print(f"  Função: h(t) = h0 - v0*t - (1/2)*a*t²")
    print(f"  Parâmetros gerados aleatoriamente:")
    print(f"    h0 = {h0:.0f} m  | v0 = {v0} m/s  | a = {a} m/s²\n")

    tempos, alturas, t_pouso = simular_descida(h0, v0, a)

    print(f"  {'Tempo (s)':<12} {'Altitude (m)':<15}")
    print(f"  {'-'*12} {'-'*15}")
    for t, h in zip(tempos, alturas):
        print(f"  {t:<12} {h:<15.1f}")

    print(f"\n  Toque no solo estimado: t = {t_pouso} s ({t_pouso/60:.1f} min)")
    print(f"  Acionamento recomendado dos retrofoguetes: t = {t_pouso*0.6:.0f} s")

    imprimir_separador()
    print("  Simulação MGPEB concluída.")
    imprimir_separador()

# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    executar_simulacao()