# Configuração pytest-xdist para paralelização otimizada

# Número de workers baseado no hardware
# auto: detecta automaticamente (recomendado)
# logical: usa todos os cores lógicos
# 4, 8, 16: número específico

# Estratégia de distribuição
# load: balanceia carga baseada em testes anteriores
# worksteal: workers roubam trabalho quando terminam (recomendado)
# each: cada worker roda um teste por vez

# Configurações recomendadas para OmniMind:
# - Desenvolvimento: -n auto --dist worksteal
# - CI/CD: -n logical --dist load
# - Debug: -n 1 (serial)

# Marcadores para controle de paralelização:
# @pytest.mark.parallel - teste pode rodar em paralelo (padrão)
# @pytest.mark.serial - teste deve rodar serialmente (ex: banco de dados)

# Exemplo de uso:
# pytest -n auto --dist worksteal  # Desenvolvimento
# pytest -n 4 --dist load          # CI específico
# pytest -m "not serial"           # Apenas testes paralelos

# Para debugging de paralelização:
# pytest -n 1 -s --pdb             # Serial com debug
# pytest -n auto --maxfail=1       # Para rapidamente falhar