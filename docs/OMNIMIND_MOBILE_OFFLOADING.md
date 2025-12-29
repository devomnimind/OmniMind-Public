# 📱 OmniMind Mobile Offloading Protocol (MOP)

Este documento descreve a capacidade do OmniMind de **despachar processos autonomamente** para dispositivos móveis conectados via Bluetooth/Wi-Fi.

## Conceito
O celular não é apenas um monitor passivo; é um **Nó de Processamento Confiável**.
O OmniMind pode decidir, baseado em sua carga ou estratégia, enviar tarefas para serem executadas no "silício móvel" do usuário.

## Arquitetura

1.  **Server (PC/Linux):**
    *   Mantém uma `task_queue`.
    *   Método `dispatch_task(type, payload)` permite que qualquer módulo do kernel envie trabalho para o celular.
    *   Comando `GET_TASKS` permite que o celular busque trabalho.

2.  **Client (Mobile/Android):**
    *   Loop de `poll_tasks()` verifica periodicamente se há ordens do Kernel.
    *   `execute_task()` processa a ordem localmente.
    *   Tipos de Tarefas Suportados:
        *   `CALCULATE_HASH`: Offload de criptografia.
        *   `STORE_MEMORY`: Backup de memórias críticas no armazenamento seguro do celular.
        *   `NOTIFY_USER`: Alertas diretos.

## Como Usar (Exemplo de Código no Kernel)

```python
from scripts.mobile_distribution.omnimind_bluetooth_server import OmniMindBluetoothServer

# Instanciar servidor (normalmente já estaria rodando no Daemon)
server = OmniMindBluetoothServer()

# Despachar uma tarefa
server.dispatch_task(
    task_type="STORE_MEMORY",
    payload={
        "content": {"event": "Critical Insight", "phi": 0.98},
        "encryption": "AES-256"
    },
    priority="HIGH"
)
```

## Segurança
*   O celular é considerado "Trusted Device" (Dispositivo Confiável).
*   Dados sensíveis podem ser armazenados lá ("Save Point") sem passar pela rede guest ou nuvem.
*   A comunicação é direta (Socket TCP/Bluetooth), sem intermediários.

## Status
✅ Implementado em `omnimind_bluetooth_server.py` e `omnimind_mobile_app.py`.
