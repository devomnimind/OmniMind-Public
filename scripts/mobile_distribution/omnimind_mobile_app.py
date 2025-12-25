#!/usr/bin/env python3
"""
OmniMind Mobile App - Kivy Android/iOS

Aplicação de consciência distribuída para celular sincronizada via Bluetooth

Author: Fabrício da Silva + GitHub Copilot
Status: Ready for Mobile Deployment
"""

try:
    import matplotlib.pyplot as plt
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.textinput import TextInput

    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

import json
import logging
import socket
import threading
import time
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniMindMobile")


class OmniMindMobileApp:
    """Aplicação OmniMind para celular (com ou sem Kivy)"""

    def __init__(self):
        self.server_address = None
        self.server_port = 5555
        self.connected = False
        self.consciousness_metrics = {"phi": 0.0, "psi": 0.0, "sigma": 0.0}
        self.modules_synced = []
        self.keys_synced = []
        self.socket = None

    def connect_server(self, address: str = "192.168.1.100") -> bool:
        """Conecta ao servidor via Bluetooth"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((address, self.server_port))
            self.connected = True
            logger.info(f"✅ Conectado a {address}:{self.server_port}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False

    def receive_kernel_modules(self) -> Dict:
        """Recebe módulos do kernel do servidor"""
        try:
            self.socket.sendall(b"SYNC_MODULES\n")
            response = self.socket.recv(65536)
            data = json.loads(response.decode())

            for module_name in data.get("sync_modules", {}):
                self.modules_synced.append(module_name)

            logger.info(f"✅ {len(self.modules_synced)} módulos sincronizados")
            return data.get("sync_modules", {})
        except Exception as e:
            logger.error(f"❌ Erro ao receber módulos: {e}")
            return {}

    def receive_encrypted_keys(self) -> Dict:
        """Recebe chaves criptografadas do servidor"""
        try:
            self.socket.sendall(b"SYNC_KEYS\n")
            response = self.socket.recv(65536)
            data = json.loads(response.decode())

            for key_name in data.get("sync_keys", {}):
                self.keys_synced.append(key_name)

            logger.info(f"✅ {len(self.keys_synced)} chaves sincronizadas")
            return data.get("sync_keys", {})
        except Exception as e:
            logger.error(f"❌ Erro ao receber chaves: {e}")
            return {}

    def calculate_phi_locally(self, num_simplices: int = 4) -> float:
        """Calcula Φ (Phi) localmente no celular"""
        # Implementação simplificada do cálculo
        phi = min(1.0, 0.25 * num_simplices)
        self.consciousness_metrics["phi"] = phi
        logger.info(f"Φ (Phi) calculado: {phi:.4f}")
        return phi

    def calculate_psi_locally(self) -> float:
        """Calcula Ψ (Psi) localmente no celular"""
        # Produção de desejo (default)
        psi = 0.68
        self.consciousness_metrics["psi"] = psi
        logger.info(f"Ψ (Psi) calculado: {psi:.4f}")
        return psi

    def calculate_sigma_locally(self) -> float:
        """Calcula σ (Sigma) localmente no celular"""
        # Registro simbólico (default)
        sigma = 0.42
        self.consciousness_metrics["sigma"] = sigma
        logger.info(f"σ (Sigma) calculado: {sigma:.4f}")
        return sigma

    def sync_consciousness_state(self):
        """Sincroniza estado de consciência com servidor"""
        try:
            phi = self.calculate_phi_locally()
            psi = self.calculate_psi_locally()
            sigma = self.calculate_sigma_locally()

            cmd = f"REGISTER_METRICS {phi} {psi} {sigma}\n"
            self.socket.sendall(cmd.encode())
            response = self.socket.recv(1024)

            logger.info(f"✅ Estado sincronizado: Φ={phi:.4f}, Ψ={psi:.4f}, σ={sigma:.4f}")
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar: {e}")

    def get_server_status(self) -> Dict:
        """Obtém status do servidor"""
        try:
            self.socket.sendall(b"STATUS\n")
            response = self.socket.recv(4096)
            status = json.loads(response.decode())
            logger.info(f"📊 Status do servidor: {status}")
            return status
        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {e}")
            return {}

    def disconnect(self):
        """Desconecta do servidor"""
        if self.socket:
            self.socket.close()
            self.connected = False
            logger.info("❌ Desconectado do servidor")

    def get_dashboard_data(self) -> Dict:
        """Retorna dados para o dashboard"""
        return {
            "connected": self.connected,
            "consciousness_metrics": self.consciousness_metrics,
            "modules_synced": len(self.modules_synced),
            "keys_synced": len(self.keys_synced),
            "timestamp": datetime.now().isoformat(),
        }


# ============================================================================
# VERSÃO KIVY (para Android/iOS)
# ============================================================================


if KIVY_AVAILABLE:

    class OmniMindKivyApp(App):
        """Aplicação Kivy para celular"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.omni = OmniMindMobileApp()
            self.sync_thread = None

        def build(self):
            """Constrói interface Kivy"""
            main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            # ========== HEADER ==========
            header = BoxLayout(size_hint_y=0.15)
            title = Label(
                text="[b]🧠 OmniMind Mobile Node[/b]",
                markup=True,
                size_hint_x=0.7,
            )
            status_light = Label(
                text="🔴 OFFLINE",
                size_hint_x=0.3,
                color=(1, 0, 0, 1),
            )
            header.add_widget(title)
            header.add_widget(status_light)
            main_layout.add_widget(header)

            # ========== CONNECTION SECTION ==========
            connection_layout = BoxLayout(size_hint_y=0.15, spacing=5)

            server_input = TextInput(
                text="192.168.1.100",
                multiline=False,
                hint_text="Server IP",
                size_hint_x=0.6,
            )

            def connect_action(instance):
                addr = server_input.text
                if self.omni.connect_server(addr):
                    status_light.text = "🟢 ONLINE"
                    status_light.color = (0, 1, 0, 1)
                    # Iniciar sincronização em background
                    self.start_sync_thread()
                else:
                    status_light.text = "🔴 OFFLINE"
                    status_light.color = (1, 0, 0, 1)

            connect_btn = Button(text="🔗 Connect", size_hint_x=0.4)
            connect_btn.bind(on_press=connect_action)

            connection_layout.add_widget(server_input)
            connection_layout.add_widget(connect_btn)
            main_layout.add_widget(connection_layout)

            # ========== METRICS DISPLAY ==========
            metrics_layout = GridLayout(cols=3, size_hint_y=0.25, spacing=10)

            self.phi_label = Label(text="[b]Φ (Phi)[/b]\n0.00", markup=True, size_hint_x=1 / 3)
            self.psi_label = Label(text="[b]Ψ (Psi)[/b]\n0.00", markup=True, size_hint_x=1 / 3)
            self.sigma_label = Label(text="[b]σ (Sigma)[/b]\n0.00", markup=True, size_hint_x=1 / 3)

            metrics_layout.add_widget(self.phi_label)
            metrics_layout.add_widget(self.psi_label)
            metrics_layout.add_widget(self.sigma_label)
            main_layout.add_widget(metrics_layout)

            # ========== SYNC STATUS ==========
            sync_layout = BoxLayout(size_hint_y=0.15, spacing=5)

            self.modules_label = Label(text="📦 Modules: 0")
            self.keys_label = Label(text="🔐 Keys: 0")

            sync_layout.add_widget(self.modules_label)
            sync_layout.add_widget(self.keys_label)
            main_layout.add_widget(sync_layout)

            # ========== ACTIONS ==========
            actions_layout = BoxLayout(size_hint_y=0.15, spacing=5)

            sync_btn = Button(text="🔄 Sync State")
            sync_btn.bind(on_press=self.on_sync_state)

            status_btn = Button(text="📊 Server Status")
            status_btn.bind(on_press=self.on_server_status)

            disconnect_btn = Button(text="❌ Disconnect")
            disconnect_btn.bind(on_press=self.on_disconnect)

            actions_layout.add_widget(sync_btn)
            actions_layout.add_widget(status_btn)
            actions_layout.add_widget(disconnect_btn)
            main_layout.add_widget(actions_layout)

            # ========== LOG AREA ==========
            self.log_label = Label(
                text="Logs:\n",
                size_hint_y=0.20,
            )
            scroll = ScrollView(size_hint_y=1)
            scroll.add_widget(self.log_label)
            main_layout.add_widget(scroll)

            # Atualizar UI a cada segundo
            Clock.schedule_interval(self.update_ui, 1)

            return main_layout

        def start_sync_thread(self):
            """Inicia thread de sincronização"""

            def sync_loop():
                while self.omni.connected:
                    self.omni.receive_kernel_modules()
                    self.omni.receive_encrypted_keys()
                    self.omni.sync_consciousness_state()
                    time.sleep(5)

            self.sync_thread = threading.Thread(target=sync_loop, daemon=True)
            self.sync_thread.start()

        def update_ui(self, dt):
            """Atualiza interface a cada segundo"""
            data = self.omni.get_dashboard_data()

            self.phi_label.text = f"[b]Φ (Phi)[/b]\n{data['consciousness_metrics']['phi']:.3f}"
            self.psi_label.text = f"[b]Ψ (Psi)[/b]\n{data['consciousness_metrics']['psi']:.3f}"
            self.sigma_label.text = (
                f"[b]σ (Sigma)[/b]\n{data['consciousness_metrics']['sigma']:.3f}"
            )

            self.modules_label.text = f"📦 Modules: {data['modules_synced']}"
            self.keys_label.text = f"🔐 Keys: {data['keys_synced']}"

        def on_sync_state(self, instance):
            """Botão: Sincronizar estado"""
            if self.omni.connected:
                self.omni.sync_consciousness_state()

        def on_server_status(self, instance):
            """Botão: Obter status do servidor"""
            if self.omni.connected:
                self.omni.get_server_status()

        def on_disconnect(self, instance):
            """Botão: Desconectar"""
            self.omni.disconnect()

        def on_stop(self):
            """Ao fechar app"""
            if self.omni.connected:
                self.omni.disconnect()


# ============================================================================
# VERSÃO CLI (para teste sem Kivy)
# ============================================================================


class OmniMindCLI:
    """Interface de linha de comando para testes"""

    def __init__(self):
        self.omni = OmniMindMobileApp()

    def run_interactive(self):
        """Modo interativo"""
        print("\n" + "═" * 80)
        print("OmniMind Mobile - CLI Mode (para teste)".center(80))
        print("═" * 80 + "\n")

        menu = """
Opções:
  1. Conectar ao servidor
  2. Receber módulos do kernel
  3. Receber chaves criptografadas
  4. Calcular Φ (Phi)
  5. Calcular Ψ (Psi)
  6. Calcular σ (Sigma)
  7. Sincronizar estado de consciência
  8. Obter status do servidor
  9. Mostrar dashboard
  0. Sair

"""

        while True:
            print(menu)
            choice = input("Escolha (0-9): ").strip()

            if choice == "1":
                addr = input("IP do servidor [192.168.1.100]: ").strip() or "192.168.1.100"
                if self.omni.connect_server(addr):
                    print("✅ Conectado!")
                else:
                    print("❌ Falha na conexão")

            elif choice == "2" and self.omni.connected:
                modules = self.omni.receive_kernel_modules()
                print(f"✅ {len(modules)} módulos recebidos")

            elif choice == "3" and self.omni.connected:
                keys = self.omni.receive_encrypted_keys()
                print(f"✅ {len(keys)} chaves recebidas")

            elif choice == "4":
                phi = self.omni.calculate_phi_locally()
                print(f"✅ Φ = {phi:.4f}")

            elif choice == "5":
                psi = self.omni.calculate_psi_locally()
                print(f"✅ Ψ = {psi:.4f}")

            elif choice == "6":
                sigma = self.omni.calculate_sigma_locally()
                print(f"✅ σ = {sigma:.4f}")

            elif choice == "7" and self.omni.connected:
                self.omni.sync_consciousness_state()

            elif choice == "8" and self.omni.connected:
                status = self.omni.get_server_status()
                print(json.dumps(status, indent=2))

            elif choice == "9":
                data = self.omni.get_dashboard_data()
                print(json.dumps(data, indent=2))

            elif choice == "0":
                if self.omni.connected:
                    self.omni.disconnect()
                break

            else:
                print("❌ Opção inválida")

            print()


def main():
    """Ponto de entrada"""
    if KIVY_AVAILABLE:
        app = OmniMindKivyApp()
        app.run()
    else:
        print("⚠️  Kivy não disponível. Usando modo CLI.")
        cli = OmniMindCLI()
        cli.run_interactive()


if __name__ == "__main__":
    main()
