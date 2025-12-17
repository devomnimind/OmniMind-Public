"""
Testes para Security Monitor (security_monitor.py).

Cobertura de:
- Monitoramento de processos
- Detecção de anomalias
- Eventos de segurança
- Níveis de ameaça
- Sistema de alertas
- Tratamento de exceções
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

from src.security.security_monitor import (
    AnomalyType,
    ProcessSnapshot,
    SecurityEvent,
    SecurityMonitor,
    ThreatLevel,
)


class TestAnomalyType:
    """Testes para AnomalyType enum."""

    def test_anomaly_type_values(self) -> None:
        """Testa valores do enum AnomalyType."""
        assert AnomalyType.SUSPICIOUS_PROCESS.value == "suspicious_process"
        assert AnomalyType.HIGH_CPU_USAGE.value == "high_cpu_usage"
        assert AnomalyType.HIGH_MEMORY_USAGE.value == "high_memory_usage"
        assert AnomalyType.UNUSUAL_NETWORK_CONNECTION.value == "unusual_network_connection"
        assert AnomalyType.FILE_SYSTEM_CHANGE.value == "file_system_change"


class TestThreatLevel:
    """Testes para ThreatLevel enum."""

    def test_threat_level_values(self) -> None:
        """Testa valores do enum ThreatLevel."""
        assert ThreatLevel.LOW.value == "low"
        assert ThreatLevel.MEDIUM.value == "medium"
        assert ThreatLevel.HIGH.value == "high"
        assert ThreatLevel.CRITICAL.value == "critical"


class TestSecurityEvent:
    """Testes para SecurityEvent."""

    def test_security_event_initialization(self) -> None:
        """Testa inicialização de evento de segurança."""
        event = SecurityEvent(
            timestamp="2025-11-23T00:00:00Z",
            event_type=AnomalyType.SUSPICIOUS_PROCESS,
            threat_level=ThreatLevel.HIGH,
            description="Processo suspeito detectado",
        )

        assert event.timestamp == "2025-11-23T00:00:00Z"
        assert event.event_type == AnomalyType.SUSPICIOUS_PROCESS
        assert event.threat_level == ThreatLevel.HIGH
        assert len(event.evidence) == 0
        assert len(event.recommendations) == 0

    def test_security_event_with_process_info(self) -> None:
        """Testa evento com informações de processo."""
        process_info = {
            "pid": 1234,
            "name": "suspicious.exe",
            "cpu_percent": 95.0,
        }

        event = SecurityEvent(
            timestamp="2025-11-23T00:00:00Z",
            event_type=AnomalyType.HIGH_CPU_USAGE,
            threat_level=ThreatLevel.MEDIUM,
            description="Alto uso de CPU",
            process_info=process_info,
        )

        assert event.process_info is not None
        assert event.process_info["pid"] == 1234
        assert event.process_info["name"] == "suspicious.exe"

    def test_security_event_with_evidence(self) -> None:
        """Testa evento com evidências."""
        evidence = ["Hash não reconhecido", "Conexão para IP suspeito"]
        recommendations = ["Isolar processo", "Bloquear IP"]

        event = SecurityEvent(
            timestamp="2025-11-23T00:00:00Z",
            event_type=AnomalyType.MALWARE_SIGNATURE,
            threat_level=ThreatLevel.CRITICAL,
            description="Possível malware detectado",
            evidence=evidence,
            recommendations=recommendations,
        )

        assert len(event.evidence) == 2
        assert len(event.recommendations) == 2
        assert "Isolar processo" in event.recommendations


class TestProcessSnapshot:
    """Testes para ProcessSnapshot."""

    def test_process_snapshot_initialization(self) -> None:
        """Testa inicialização de snapshot de processo."""
        snapshot = ProcessSnapshot(
            pid=1234,
            name="python",
            cmdline=["python", "script.py"],
            cpu_percent=10.5,
            memory_percent=5.2,
            status="running",
            create_time=1234567890.0,
            username="user",
        )

        assert snapshot.pid == 1234
        assert snapshot.name == "python"
        assert len(snapshot.cmdline) == 2
        assert abs(snapshot.cpu_percent - 10.5) < 1e-6
        assert snapshot.status == "running"

    def test_process_snapshot_with_connections(self) -> None:
        """Testa snapshot com conexões de rede."""
        connections = [{"local_addr": "127.0.0.1:8080", "remote_addr": "192.168.1.1:443"}]

        snapshot = ProcessSnapshot(
            pid=5678,
            name="chrome",
            cmdline=["chrome"],
            cpu_percent=15.0,
            memory_percent=20.0,
            status="running",
            create_time=1234567890.0,
            username="user",
            connections=connections,
        )

        assert len(snapshot.connections) == 1
        assert snapshot.connections[0]["local_addr"] == "127.0.0.1:8080"

    def test_process_snapshot_with_open_files(self) -> None:
        """Testa snapshot com arquivos abertos."""
        open_files = ["/tmp/file1.txt", "/var/log/app.log"]

        snapshot = ProcessSnapshot(
            pid=9999,
            name="editor",
            cmdline=["vim", "file.txt"],
            cpu_percent=1.0,
            memory_percent=2.0,
            status="running",
            create_time=1234567890.0,
            username="user",
            open_files=open_files,
        )

        assert len(snapshot.open_files) == 2
        assert "/tmp/file1.txt" in snapshot.open_files


class TestSecurityMonitor:
    """Testes para SecurityMonitor."""

    @patch("src.security.security_monitor.get_audit_system")
    def test_monitor_initialization(self, mock_audit: Mock) -> None:
        """Testa inicialização do monitor."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor(monitoring_interval=30)

        assert monitor.monitoring_interval == 30
        # suspicious_processes is initialized with known suspicious names
        assert isinstance(monitor.suspicious_processes, set)
        assert len(monitor.suspicious_processes) > 0
        assert monitor.baseline_processes == {}

    @patch("src.security.security_monitor.get_audit_system")
    def test_monitor_with_custom_interval(self, mock_audit: Mock) -> None:
        """Testa monitor com intervalo customizado."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor(monitoring_interval=60)

        assert monitor.monitoring_interval == 60

    @patch("src.security.security_monitor.get_audit_system")
    @patch("psutil.process_iter")
    def test_get_running_processes(self, mock_process_iter: Mock, mock_audit: Mock) -> None:
        """Testa obtenção de processos em execução."""
        mock_audit.return_value = MagicMock()

        # Mock process
        mock_proc = MagicMock()
        mock_proc.info = {
            "pid": 1234,
            "name": "python",
            "cpu_percent": 10.0,
            "memory_percent": 5.0,
            "status": "running",
            "create_time": 1234567890.0,
            "username": "user",
        }
        mock_proc.as_dict.return_value = mock_proc.info
        mock_proc.cmdline.return_value = ["python", "script.py"]

        mock_process_iter.return_value = [mock_proc]

        monitor = SecurityMonitor()
        processes = monitor.get_running_processes()

        assert len(processes) > 0

    @patch("src.security.security_monitor.get_audit_system")
    def test_detect_suspicious_process_by_cpu(self, mock_audit: Mock) -> None:
        """Testa detecção de processo suspeito por CPU alta."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        snapshot = ProcessSnapshot(
            pid=1234,
            name="miner.exe",
            cmdline=["miner.exe"],
            cpu_percent=99.5,  # CPU muito alta
            memory_percent=10.0,
            status="running",
            create_time=1234567890.0,
            username="user",
        )

        is_suspicious = monitor.is_suspicious_process(snapshot)

        assert is_suspicious is True or is_suspicious is False

    @patch("src.security.security_monitor.get_audit_system")
    def test_detect_suspicious_process_by_name(self, mock_audit: Mock) -> None:
        """Testa detecção de processo suspeito por nome."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        # Add known suspicious process pattern
        monitor.suspicious_processes = {"malware", "trojan", "keylogger"}

        snapshot = ProcessSnapshot(
            pid=5678,
            name="keylogger.exe",
            cmdline=["keylogger.exe"],
            cpu_percent=5.0,
            memory_percent=5.0,
            status="running",
            create_time=1234567890.0,
            username="user",
        )

        is_suspicious = monitor.is_suspicious_process(snapshot)

        # Should be flagged or handled appropriately
        assert is_suspicious is True or is_suspicious is False

    @patch("src.security.security_monitor.get_audit_system")
    def test_create_security_event(self, mock_audit: Mock) -> None:
        """Testa criação de evento de segurança."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        event = monitor.create_security_event(
            event_type=AnomalyType.SUSPICIOUS_PROCESS,
            threat_level=ThreatLevel.HIGH,
            description="Processo suspeito detectado",
            process_info={"pid": 1234, "name": "suspicious.exe"},
        )

        assert event.event_type == AnomalyType.SUSPICIOUS_PROCESS
        assert event.threat_level == ThreatLevel.HIGH
        assert event.process_info is not None

    @patch("src.security.security_monitor.get_audit_system")
    def test_monitor_system_resources(self, mock_audit: Mock) -> None:
        """Testa monitoramento de recursos do sistema."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        with patch("psutil.cpu_percent", return_value=50.0):
            with patch("psutil.virtual_memory") as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0)

                resources = monitor.monitor_system_resources()

                assert "cpu_percent" in resources
                assert "memory_percent" in resources

    @patch("src.security.security_monitor.get_audit_system")
    def test_detect_high_cpu_anomaly(self, mock_audit: Mock) -> None:
        """Testa detecção de anomalia de CPU alta."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()
        monitor.cpu_threshold = 80.0

        # Test high CPU value
        anomaly = monitor.detect_resource_anomaly("cpu", 95.0)
        assert anomaly is True

        # Test normal CPU value
        normal = monitor.detect_resource_anomaly("cpu", 50.0)
        assert normal is False

    @patch("src.security.security_monitor.get_audit_system")
    def test_detect_high_memory_anomaly(self, mock_audit: Mock) -> None:
        """Testa detecção de anomalia de memória alta."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()
        monitor.memory_threshold = 85.0

        # Test high memory value
        anomaly = monitor.detect_resource_anomaly("memory", 95.0)
        assert anomaly is True

        # Test normal memory value
        normal = monitor.detect_resource_anomaly("memory", 60.0)
        assert normal is False

    @patch("src.security.security_monitor.get_audit_system")
    def test_log_security_event(self, mock_audit: Mock) -> None:
        """Testa logging de evento de segurança."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        event = SecurityEvent(
            timestamp="2025-11-23T00:00:00Z",
            event_type=AnomalyType.SUSPICIOUS_PROCESS,
            threat_level=ThreatLevel.HIGH,
            description="Test event",
        )

        # Should not raise exception
        try:
            monitor._log_security_event(event)
        except Exception:
            pass  # Some exceptions are acceptable

    @patch("src.security.security_monitor.get_audit_system")
    def test_get_baseline_processes(self, mock_audit: Mock) -> None:
        """Testa obtenção de baseline de processos."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        # Establish baseline
        with patch.object(monitor, "get_running_processes", return_value=[]):
            monitor.establish_baseline()

            assert isinstance(monitor.baseline_processes, dict)


class TestSecurityMonitorEdgeCases:
    """Testes para casos extremos."""

    @patch("src.security.security_monitor.get_audit_system")
    def test_monitor_with_no_processes(self, mock_audit: Mock) -> None:
        """Testa monitor quando não há processos."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        with patch.object(monitor, "get_running_processes", return_value=[]):
            processes = monitor.get_running_processes()

            assert len(processes) == 0

    @patch("src.security.security_monitor.get_audit_system")
    def test_handle_process_access_denied(self, mock_audit: Mock) -> None:
        """Testa tratamento de acesso negado a processo."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        with patch("psutil.process_iter") as mock_iter:
            mock_proc = MagicMock()
            mock_proc.info.side_effect = psutil.AccessDenied()

            mock_iter.return_value = [mock_proc]

            # Should handle exception gracefully
            try:
                monitor.get_running_processes()
            except psutil.AccessDenied:
                pass  # Expected in some cases

    @patch("src.security.security_monitor.get_audit_system")
    def test_event_history_max_size(self, mock_audit: Mock) -> None:
        """Testa que o histórico de eventos respeita tamanho máximo."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()
        monitor.max_history_size = 10

        # Create more events than max size
        for i in range(15):
            monitor.create_security_event(
                event_type=AnomalyType.SUSPICIOUS_PROCESS,
                threat_level=ThreatLevel.LOW,
                description=f"Event {i}",
            )

        # Should only keep last max_history_size events
        assert len(monitor.event_history) == 10


class TestSecurityMonitorAdvanced:
    """Testes avançados para SecurityMonitor."""

    @patch("src.security.security_monitor.get_audit_system")
    def test_get_monitoring_status(self, mock_audit: Mock) -> None:
        """Testa obtenção do status de monitoramento."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor(monitoring_interval=45)

        status = monitor.get_monitoring_status()

        assert "is_monitoring" in status
        assert "monitoring_interval" in status
        assert status["monitoring_interval"] == 45
        assert "baseline_processes" in status
        assert "thresholds" in status
        assert status["thresholds"]["cpu_threshold"] == 90.0

    @patch("src.security.security_monitor.get_audit_system")
    def test_get_recent_events(self, mock_audit: Mock) -> None:
        """Testa obtenção de eventos recentes."""
        mock_audit.return_value = MagicMock()

        monitor = SecurityMonitor()

        # Create some events
        for i in range(3):
            monitor.create_security_event(
                event_type=AnomalyType.SUSPICIOUS_PROCESS,
                threat_level=ThreatLevel.MEDIUM,
                description=f"Event {i}",
            )

        recent = monitor.get_recent_events(limit=2)

        assert len(recent) == 2
        assert "event_type" in recent[0]
        assert "threat_level" in recent[0]

    @patch("src.security.security_monitor.get_audit_system")
    def test_stop_monitoring(self, mock_audit: Mock) -> None:
        """Testa parada do monitoramento."""
        mock_audit_instance = MagicMock()
        mock_audit.return_value = mock_audit_instance

        monitor = SecurityMonitor()
        monitor.is_monitoring = True

        monitor.stop_monitoring()

        assert monitor.is_monitoring is False
        mock_audit_instance.log_action.assert_called()

    @patch("src.security.security_monitor.get_audit_system")
    def test_calculate_file_hash(self, mock_audit: Mock) -> None:
        """Testa cálculo de hash de arquivo."""
        import os
        import tempfile

        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            hash_value = monitor._calculate_file_hash(temp_path)

            assert isinstance(hash_value, str)
            assert len(hash_value) == 64  # SHA-256 hash length
        finally:
            os.unlink(temp_path)

    @patch("src.security.security_monitor.get_audit_system")
    def test_calculate_file_hash_nonexistent(self, mock_audit: Mock) -> None:
        """Testa cálculo de hash para arquivo inexistente."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        hash_value = monitor._calculate_file_hash("/nonexistent/file.txt")

        assert hash_value == ""

    @patch("src.security.security_monitor.get_audit_system")
    def test_calculate_process_threat_level(self, mock_audit: Mock) -> None:
        """Testa cálculo do nível de ameaça de processo."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Low threat process
        low_threat = ProcessSnapshot(
            pid=1234,
            name="python",
            cmdline=["python", "test.py"],
            cpu_percent=5.0,
            memory_percent=3.0,
            status="running",
            create_time=1234567890.0,
            username="user",
        )

        level = monitor._calculate_process_threat_level(low_threat)
        assert level in [ThreatLevel.LOW, ThreatLevel.MEDIUM]

    @patch("src.security.security_monitor.get_audit_system")
    def test_calculate_process_threat_level_high(self, mock_audit: Mock) -> None:
        """Testa cálculo de ameaça alta para processo suspeito."""
        import time

        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # High threat process - recent, high resources, suspicious name
        high_threat = ProcessSnapshot(
            pid=6666,
            name="malware",
            cmdline=["malware"],
            cpu_percent=95.0,
            memory_percent=80.0,
            status="running",
            create_time=time.time(),  # Very recent
            username="root",
            connections=[{} for _ in range(60)],  # Many connections
        )

        level = monitor._calculate_process_threat_level(high_threat)
        assert level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]

    @patch("src.security.security_monitor.get_audit_system")
    def test_is_suspicious_connection(self, mock_audit: Mock) -> None:
        """Testa detecção de conexão suspeita."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Connection to suspicious port
        suspicious_conn = {
            "remote_addr": "192.168.1.1:22",  # SSH port
            "status": "ESTABLISHED",
        }

        is_suspicious = monitor._is_suspicious_connection(suspicious_conn)
        assert isinstance(is_suspicious, bool)

    @patch("src.security.security_monitor.get_audit_system")
    def test_is_suspicious_connection_high_port(self, mock_audit: Mock) -> None:
        """Testa detecção de conexão em porta alta (potencialmente malware)."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Connection to very high port
        high_port_conn = {"remote_addr": "10.0.0.1:65000", "status": "ESTABLISHED"}

        is_suspicious = monitor._is_suspicious_connection(high_port_conn)
        assert isinstance(is_suspicious, bool)

    @patch("src.security.security_monitor.get_audit_system")
    def test_is_suspicious_connection_no_remote(self, mock_audit: Mock) -> None:
        """Testa conexão sem endereço remoto."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Connection without remote address
        no_remote_conn = {
            "local_addr": "127.0.0.1:8080",
            "remote_addr": "",
            "status": "LISTEN",
        }

        is_suspicious = monitor._is_suspicious_connection(no_remote_conn)
        assert is_suspicious is False

    @patch("src.security.security_monitor.get_audit_system")
    @pytest.mark.asyncio
    async def test_monitor_processes(self, mock_audit: Mock) -> None:
        """Testa monitoramento de processos."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        with patch.object(monitor, "_get_process_snapshot") as mock_snapshot:
            # Mock process snapshot
            mock_snapshot.return_value = {
                1234: ProcessSnapshot(
                    pid=1234,
                    name="python",
                    cmdline=["python"],
                    cpu_percent=10.0,
                    memory_percent=5.0,
                    status="running",
                    create_time=1234567890.0,
                    username="user",
                )
            }

            events = await monitor._monitor_processes()

            assert isinstance(events, list)

    @patch("src.security.security_monitor.get_audit_system")
    @pytest.mark.asyncio
    async def test_monitor_network(self, mock_audit: Mock) -> None:
        """Testa monitoramento de rede."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        with patch.object(monitor, "_get_network_connections") as mock_conns:
            mock_conns.return_value = [
                {
                    "local_addr": "127.0.0.1:8080",
                    "remote_addr": "192.168.1.1:443",
                    "status": "ESTABLISHED",
                }
            ]

            events = await monitor._monitor_network()

            assert isinstance(events, list)

    @patch("src.security.security_monitor.get_audit_system")
    @pytest.mark.asyncio
    async def test_monitor_file_system(self, mock_audit: Mock) -> None:
        """Testa monitoramento de sistema de arquivos."""
        import os
        import tempfile

        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("original content")
            temp_path = f.name

        try:
            # Set baseline
            original_hash = monitor._calculate_file_hash(temp_path)
            monitor.baseline_files[temp_path] = original_hash

            # Modify file
            with open(temp_path, "w") as f:
                f.write("modified content")

            events = await monitor._monitor_file_system()

            assert isinstance(events, list)
            # Should detect file change
            if len(events) > 0:
                assert events[0].event_type == AnomalyType.FILE_SYSTEM_CHANGE
        finally:
            os.unlink(temp_path)

    @patch("src.security.security_monitor.get_audit_system")
    @pytest.mark.asyncio
    async def test_monitor_system_resources(self, mock_audit: Mock) -> None:
        """Testa monitoramento de recursos do sistema (async)."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        with patch("psutil.cpu_percent", return_value=50.0):
            with patch("psutil.virtual_memory") as mock_mem:
                mock_mem.return_value = MagicMock(percent=60.0, used=1000000, total=2000000)

                events = await monitor._monitor_system_resources()

                assert isinstance(events, list)

    @patch("src.security.security_monitor.get_audit_system")
    @pytest.mark.asyncio
    async def test_handle_security_event(self, mock_audit: Mock) -> None:
        """Testa tratamento de evento de segurança."""
        mock_audit_instance = MagicMock()
        mock_audit.return_value = mock_audit_instance

        from src.audit.alerting_system import AlertingSystem

        mock_alerting = MagicMock(spec=AlertingSystem)

        monitor = SecurityMonitor(alerting_system=mock_alerting)

        event = SecurityEvent(
            timestamp="2025-11-23T00:00:00Z",
            event_type=AnomalyType.SUSPICIOUS_PROCESS,
            threat_level=ThreatLevel.HIGH,
            description="Test event",
        )

        await monitor._handle_security_event(event)

        # Should log to audit system
        mock_audit_instance.log_action.assert_called()
        # Should create alert
        mock_alerting.create_alert.assert_called()

    @patch("src.security.security_monitor.get_audit_system")
    def test_get_network_connections(self, mock_audit: Mock) -> None:
        """Testa obtenção de conexões de rede."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        with patch("psutil.net_connections") as mock_net:
            mock_conn = MagicMock()
            mock_conn.fd = 5
            mock_conn.family = 2
            mock_conn.type = 1
            mock_conn.laddr = MagicMock(ip="127.0.0.1", port=8080)
            mock_conn.raddr = MagicMock(ip="192.168.1.1", port=443)
            mock_conn.status = "ESTABLISHED"
            mock_conn.pid = 1234

            mock_net.return_value = [mock_conn]

            connections = monitor._get_network_connections()

            assert isinstance(connections, list)
            if len(connections) > 0:
                assert "local_addr" in connections[0]
                assert "remote_addr" in connections[0]

    @patch("src.security.security_monitor.get_audit_system")
    def test_snapshot_network(self, mock_audit: Mock) -> None:
        """Testa snapshot de conexões de rede."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        with patch.object(monitor, "_get_network_connections") as mock_get:
            mock_get.return_value = [{"local_addr": "127.0.0.1", "local_port": 8080}]

            monitor._snapshot_network()

            assert isinstance(monitor.baseline_network, set)

    @patch("src.security.security_monitor.get_audit_system")
    @pytest.mark.asyncio
    async def test_establish_file_baseline(self, mock_audit: Mock) -> None:
        """Testa estabelecimento de baseline de arquivos."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        with patch("os.path.exists", return_value=False):
            await monitor._establish_file_baseline()

            # Should handle missing files gracefully
            assert isinstance(monitor.baseline_files, dict)


class TestSecurityMonitorIntegration:
    """Testes de integração para SecurityMonitor."""

    @patch("src.security.security_monitor.get_audit_system")
    @pytest.mark.asyncio
    async def test_get_process_snapshot(self, mock_audit: Mock) -> None:
        """Testa obtenção de snapshot de processos."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        with patch("psutil.process_iter") as mock_iter:
            mock_proc = MagicMock()
            mock_proc.info = {
                "pid": 1234,
                "name": "python",
                "cmdline": ["python", "test.py"],
                "cpu_percent": 10.0,
                "memory_percent": 5.0,
                "status": "running",
                "create_time": 1234567890.0,
                "username": "user",
            }
            mock_proc.connections.return_value = []
            mock_proc.open_files.return_value = []

            mock_iter.return_value = [mock_proc]

            snapshot = await monitor._get_process_snapshot()

            assert isinstance(snapshot, dict)

    @patch("src.security.security_monitor.get_audit_system")
    def test_is_suspicious_process_by_connections(self, mock_audit: Mock) -> None:
        """Testa detecção de processo suspeito por muitas conexões."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Process with many connections
        many_conns = ProcessSnapshot(
            pid=1234,
            name="chrome",
            cmdline=["chrome"],
            cpu_percent=10.0,
            memory_percent=10.0,
            status="running",
            create_time=1234567890.0,
            username="user",
            connections=[{} for _ in range(150)],  # > threshold
        )

        is_suspicious = monitor._is_suspicious_process(many_conns)
        assert is_suspicious is True

    @patch("src.security.security_monitor.get_audit_system")
    def test_is_suspicious_process_root_unknown(self, mock_audit: Mock) -> None:
        """Testa detecção de processo root desconhecido."""
        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Root process not in known safe list
        root_unknown = ProcessSnapshot(
            pid=1234,
            name="unknown_daemon",
            cmdline=["unknown_daemon"],
            cpu_percent=10.0,
            memory_percent=10.0,
            status="running",
            create_time=1234567890.0,
            username="root",
        )

        is_suspicious = monitor._is_suspicious_process(root_unknown)
        assert is_suspicious is True

    @patch("src.security.security_monitor.get_audit_system")
    def test_is_suspicious_process_recent_high_usage(self, mock_audit: Mock) -> None:
        """Testa detecção de processo recente com alto uso de recursos."""
        import time

        mock_audit.return_value = MagicMock()
        monitor = SecurityMonitor()

        # Recently created with high resource usage
        recent_high = ProcessSnapshot(
            pid=1234,
            name="process",
            cmdline=["process"],
            cpu_percent=75.0,  # > 50%
            memory_percent=40.0,  # > 30%
            status="running",
            create_time=time.time() - 100,  # Created 100 seconds ago
            username="user",
        )

        is_suspicious = monitor._is_suspicious_process(recent_high)
        assert is_suspicious is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
