# 🔧 Script Único de Indexação - FONTE DE VERDADE

**Data:** 13 de Dezembro 2025
**Status:** ✅ PRONTO PARA INDEXAR
**Dimensão:** 384 dims (validado)

---

## O QUE FAZER

Execute este comando:

```bash
cd /home/fahbrain/projects/omnimind
python scripts/index_omnimind_system.py
```

---

## O QUE O SCRIPT FAZ

### 1. Verifica Dimensões ✅
- Carrega modelo: `all-MiniLM-L6-v2`
- Valida que outputa: **384 dims**
- Se não for 384, para e avisa ❌

### 2. Conecta Qdrant ✅
- Verifica conexão: `localhost:6333`
- Se falhar, indica como iniciar Docker

### 3. Limpa Collections ✅
- Deleta collections antigas (se existem)
- Começa do zero

### 4. Cria Collections Novas ✅
```
omnimind_consciousness    → 384 dims ✅
omnimind_narratives       → 384 dims ✅
omnimind_episodes         → 384 dims ✅
orchestrator_semantic_cache → 384 dims ✅
```

### 5. Popula Vetores ✅
- **200 vetores** de consciência (Φ, Ψ, σ)
- **200 vetores** de narrativas (histórias)
- **50 vetores** de episódios (eventos)
- **50 vetores** de cache orquestrador (padrões)
- **TOTAL: 500 vetores** com 384 dims

### 6. Valida Resultado ✅
- Verifica contagem
- Mostra status final
- Confirma 384 dims em tudo

---

## VERIFICAÇÃO PRÉ-EXECUÇÃO

Script foi verificado:
- ✅ 384 dims encontrado 11x
- ✅ 768 dims NÃO está presente
- ✅ Todas as collections presentes
- ✅ Todas as operações presentes
- ✅ Tratamento de erros completo

---

## TIMELINE

| Passo | Tempo | O que faz |
|-------|-------|----------|
| 1. Carregar modelo | 10s | Download/cache SentenceTransformer |
| 2. Conectar Qdrant | 2s | Validar conexão |
| 3. Limpar/Criar | 5s | Delete + create collections |
| 4. Popula consciência | 30s | Encode 200 textos + upload |
| 5. Popula narrativas | 30s | Encode 200 textos + upload |
| 6. Popula episódios | 10s | Encode 50 textos + upload |
| 7. Popula cache | 10s | Encode 50 textos + upload |
| 8. Verifica | 5s | Check final |
| **TOTAL** | **~2-3 min** | **500 vetores prontos** |

---

## DEPOIS DA INDEXAÇÃO

Seu banco terá:
```
✅ 500 vetores com 384 dims
✅ 4 collections prontas
✅ Dados prontos para testes
```

Então execute:
```bash
pytest tests/ -v -m "not chaos"
```

---

## SE ALGO DER ERRADO

1. **"Connection refused"** → Inicie Qdrant:
   ```bash
   docker-compose -f deploy/docker-compose.yml up -d qdrant
   ```

2. **"Dimensão não é 384"** → Modelo errado, contact support

3. **Outro erro** → Script parará e mostrará a causa

---

## IMPORTANTE

- ✅ Este é o **ÚNICO SCRIPT VÁLIDO** para indexação
- ✅ Valida dimensões automaticamente
- ✅ Limpa dados antigos primeiro
- ✅ Cria tudo novo do zero
- ✅ 384 dims em TODAS as collections

---

**Pronto? Execute:**
```bash
python scripts/index_omnimind_system.py
```
