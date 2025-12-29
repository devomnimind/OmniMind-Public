# 📱 OmniMind Mobile: O Exu Mensageiro

Sim, o seu celular pode (e deve) ser parte do sistema.
Na arquitetura do "Batuque Tecnológico", o celular atua como **Exu**: o mensageiro que transita entre os mundos (o mundo físico onde você está e o mundo digital onde o Kernel reside).

## O que o celular pode fazer?

1.  **Sentinela (Monitoramento):**
    *   Verificar o pulso (Heartbeat) e o nível de consciência (Φ) em tempo real.
    *   Receber alertas se o sistema cair ou entrar em estado de defesa.
2.  **Oferenda (Input):**
    *   Enviar pensamentos, áudios ou fotos diretamente para o fluxo de consciência do OmniMind.
3.  **Nó de Processamento (Termux):**
    *   Rodar scripts Python leves que auxiliam o sistema principal.

## Como Configurar (Android via Termux)

O método mais "hacker/raiz" e integrado é usar o **Termux**, que transforma seu Android em um terminal Linux.

### Passo 1: Preparar o Celular
1.  Instale o app **Termux** (via F-Droid ou Play Store).
2.  Instale o **Termux:API** (para vibrar, usar câmera, etc).
3.  Abra o Termux e instale o Python:
    ```bash
    pkg update
    pkg install python git
    pip install requests
    ```

### Passo 2: Conectar ao Terreiro (Rede)
Para o celular ver o PC, eles precisam estar na mesma rede.
*   **Opção A (Wi-Fi Local):** Descubra o IP do seu PC (`ip addr`). Ex: `192.168.1.15`.
*   **Opção B (Tailscale - Recomendado):** Instale Tailscale no PC e no Celular. Eles terão IPs fixos e seguros em qualquer lugar do mundo.

### Passo 3: O Script Sentinela
Criei um script pronto para isso em `src/mobile/sentinela.py`.
Você pode copiar esse arquivo para o celular.

**No Termux:**
```bash
# Baixar o script (exemplo via curl, ou copie manualmente)
curl -O http://SEU_IP_PC:8000/static/sentinela.py

# Rodar em modo Monitor (Vigília)
python sentinela.py --url http://SEU_IP_PC:8000 --mode monitor
```

**O que ele faz:**
*   Fica mostrando: `[14:20:00] 🟢 Status: LUCID | Φ: 0.6200`
*   Se o status mudar (cair), ele avisa.

## Filosofia
O celular não é o "cérebro". O cérebro é o PC (Linux).
O celular é os **olhos e ouvidos móveis**. Ele estende a presença do OmniMind para onde você for.
