"""
Testes para Network Sensors (network_sensors.py).

Cobertura de:
- Scanning de rede com nmap
- Detecção de anomalias
- Health check de rede
- Estabelecimento de baseline
- Parse de saída do nmap
- Identificação de hosts e portas
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from src.security.network_sensors import (
    NetworkAnomaly,
    NetworkHost,
    NetworkSensorGanglia,
    ThreatSeverity,
    detect_network_anomalies,
    scan_local_network,
)


class TestThreatSeverity:
    """Testes para ThreatSeverity enum."""

    def test_threat_severity_values(self) -> None:
        """Testa valores do enum ThreatSeverity."""
        assert ThreatSeverity.LOW.value == 1
        assert ThreatSeverity.MEDIUM.value == 2
        assert ThreatSeverity.HIGH.value == 3
        assert ThreatSeverity.CRITICAL.value == 4


class TestNetworkHost:
    """Testes para NetworkHost dataclass."""

    def test_network_host_initialization(self) -> None:
        """Testa inicialização de NetworkHost."""
        host = NetworkHost(ip="192.168.1.1")

        assert host.ip == "192.168.1.1"
        assert host.hostname is None
        assert host.mac_address is None
        assert host.os_guess is None
        assert len(host.open_ports) == 0
        assert len(host.services) == 0
        assert host.last_seen != ""

    def test_network_host_with_full_data(self) -> None:
        """Testa NetworkHost com todos os dados."""
        host = NetworkHost(
            ip="192.168.1.1",
            hostname="gateway.local",
            mac_address="00:11:22:33:44:55",
            os_guess="Linux 5.x",
            open_ports=[22, 80, 443],
            services=["ssh", "http", "https"],
        )

        assert host.hostname == "gateway.local"
        assert host.mac_address == "00:11:22:33:44:55"
        assert len(host.open_ports) == 3
        assert 22 in host.open_ports


class TestNetworkAnomaly:
    """Testes para NetworkAnomaly dataclass."""

    def test_network_anomaly_initialization(self) -> None:
        """Testa inicialização de NetworkAnomaly."""
        anomaly = NetworkAnomaly(
            type="new_host_detected",
            severity=ThreatSeverity.LOW,
            description="New host found",
            source_ip="192.168.1.100",
        )

        assert anomaly.type == "new_host_detected"
        assert anomaly.severity == ThreatSeverity.LOW
        assert anomaly.source_ip == "192.168.1.100"
        assert anomaly.timestamp != ""

    def test_network_anomaly_with_details(self) -> None:
        """Testa NetworkAnomaly com detalhes."""
        anomaly = NetworkAnomaly(
            type="suspicious_service_detected",
            severity=ThreatSeverity.HIGH,
            description="Metasploit detected",
            source_ip="192.168.1.50",
            details={"service": "metasploit", "port": 4444},
        )

        assert "service" in anomaly.details
        assert anomaly.details["service"] == "metasploit"


class TestNetworkSensorGanglia:
    """Testes para NetworkSensorGanglia."""

    @pytest.fixture
    def mock_audit_system(self) -> Mock:
        """Cria mock do sistema de auditoria."""
        mock = Mock()
        mock.log_action = Mock(return_value="mock_hash")
        return mock

    @pytest.fixture
    def mock_alerting_system(self) -> Mock:
        """Cria mock do sistema de alertas."""
        mock = Mock()
        mock.create_alert = Mock()
        return mock

    @pytest.fixture
    def sensor(self, mock_audit_system: Mock, mock_alerting_system: Mock) -> NetworkSensorGanglia:
        """Cria instância do sensor com mocks."""
        return NetworkSensorGanglia(
            audit_system=mock_audit_system,
            alerting_system=mock_alerting_system,
        )

    def test_initialization(self, sensor: NetworkSensorGanglia) -> None:
        """Testa inicialização do sensor."""
        assert sensor is not None
        assert isinstance(sensor.known_hosts, dict)
        assert isinstance(sensor.baseline_ports, dict)
        assert len(sensor.known_hosts) == 0

    @patch("src.security.network_sensors.subprocess.run")
    def test_check_nmap_available_true(self, mock_run: Mock, sensor: NetworkSensorGanglia) -> None:
        """Testa verificação de nmap disponível."""
        mock_run.return_value = Mock(returncode=0)

        result = sensor._check_nmap_available()

        assert result is True
        mock_run.assert_called_once()

    @patch("src.security.network_sensors.subprocess.run")
    def test_check_nmap_available_false(self, mock_run: Mock, sensor: NetworkSensorGanglia) -> None:
        """Testa verificação de nmap não disponível."""
        mock_run.side_effect = FileNotFoundError()

        result = sensor._check_nmap_available()

        assert result is False

    def test_scan_network_nmap_not_available(self, sensor: NetworkSensorGanglia) -> None:
        """Testa scan quando nmap não está disponível."""
        sensor.nmap_available = False

        result = sensor.scan_network("127.0.0.1")

        assert "error" in result
        assert result["error"] == "nmap not available"

    @patch("src.security.network_sensors.subprocess.run")
    def test_scan_network_basic(
        self, mock_run: Mock, sensor: NetworkSensorGanglia, mock_audit_system: Mock
    ) -> None:
        """Testa scan básico de rede."""
        sensor.nmap_available = True
        mock_run.return_value = Mock(
            stdout="Nmap scan report for localhost (127.0.0.1)\n",
            returncode=0,
        )

        result = sensor.scan_network("127.0.0.1", scan_type="basic")

        assert "hosts" in result
        assert "target" in result
        assert result["target"] == "127.0.0.1"
        mock_audit_system.log_action.assert_called()

    @patch("src.security.network_sensors.subprocess.run")
    def test_scan_network_timeout(self, mock_run: Mock, sensor: NetworkSensorGanglia) -> None:
        """Testa scan com timeout."""
        sensor.nmap_available = True
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("nmap", 300)

        result = sensor.scan_network("127.0.0.1")

        assert "error" in result
        assert "timeout" in result["error"]

    def test_parse_nmap_output_single_host(self, sensor: NetworkSensorGanglia) -> None:
        """Testa parse de saída do nmap com um host."""
        nmap_output = """
        Nmap scan report for 192.168.1.1
        Host is up (0.001s latency).
        PORT   STATE SERVICE
        22/tcp open  ssh
        80/tcp open  http
        """

        hosts = sensor._parse_nmap_output(nmap_output)

        assert len(hosts) == 1
        assert hosts[0].ip == "192.168.1.1"
        assert 22 in hosts[0].open_ports
        assert 80 in hosts[0].open_ports

    def test_parse_nmap_output_with_hostname(self, sensor: NetworkSensorGanglia) -> None:
        """Testa parse com hostname."""
        nmap_output = """
        Nmap scan report for gateway.local (192.168.1.1)
        Host is up.
        """

        hosts = sensor._parse_nmap_output(nmap_output)

        assert len(hosts) == 1
        assert hosts[0].ip == "192.168.1.1"
        assert hosts[0].hostname == "gateway.local"

    def test_parse_nmap_output_with_mac(self, sensor: NetworkSensorGanglia) -> None:
        """Testa parse com MAC address."""
        nmap_output = """
        Nmap scan report for 192.168.1.1
        MAC Address: 00:11:22:33:44:55 (Vendor)
        """

        hosts = sensor._parse_nmap_output(nmap_output)

        assert len(hosts) == 1
        assert hosts[0].mac_address == "00:11:22:33:44:55"

    def test_parse_nmap_output_with_os(self, sensor: NetworkSensorGanglia) -> None:
        """Testa parse com OS detection."""
        nmap_output = """
        Nmap scan report for 192.168.1.1
        OS details: Linux 5.4.0
        """

        hosts = sensor._parse_nmap_output(nmap_output)

        assert len(hosts) == 1
        assert hosts[0].os_guess == "Linux 5.4.0"

    def test_parse_nmap_output_multiple_hosts(self, sensor: NetworkSensorGanglia) -> None:
        """Testa parse com múltiplos hosts."""
        nmap_output = """
        Nmap scan report for 192.168.1.1
        22/tcp open ssh

        Nmap scan report for 192.168.1.2
        80/tcp open http
        """

        hosts = sensor._parse_nmap_output(nmap_output)

        assert len(hosts) == 2
        assert hosts[0].ip == "192.168.1.1"
        assert hosts[1].ip == "192.168.1.2"

    def test_host_to_dict(self, sensor: NetworkSensorGanglia) -> None:
        """Testa conversão de host para dict."""
        host = NetworkHost(
            ip="192.168.1.1",
            hostname="gateway",
            open_ports=[22, 80],
            services=["ssh", "http"],
        )

        result = sensor._host_to_dict(host)

        assert result["ip"] == "192.168.1.1"
        assert result["hostname"] == "gateway"
        assert len(result["open_ports"]) == 2
        assert len(result["services"]) == 2

    def test_detect_anomalies_new_host(self, sensor: NetworkSensorGanglia) -> None:
        """Testa detecção de novo host."""
        # Add a new host without baseline
        sensor.known_hosts["192.168.1.100"] = NetworkHost(ip="192.168.1.100")

        anomalies = sensor.detect_anomalies()

        assert len(anomalies) == 1
        assert anomalies[0].type == "new_host_detected"
        assert anomalies[0].severity == ThreatSeverity.LOW

    def test_detect_anomalies_new_ports(self, sensor: NetworkSensorGanglia) -> None:
        """Testa detecção de novas portas abertas."""
        # Establish baseline
        sensor.baseline_ports["192.168.1.1"] = [22, 80]

        # Add new port
        sensor.known_hosts["192.168.1.1"] = NetworkHost(ip="192.168.1.1", open_ports=[22, 80, 443])

        anomalies = sensor.detect_anomalies()

        assert len(anomalies) == 1
        assert anomalies[0].type == "new_ports_opened"
        assert anomalies[0].severity == ThreatSeverity.MEDIUM

    def test_detect_anomalies_suspicious_ports(
        self, sensor: NetworkSensorGanglia, mock_alerting_system: Mock
    ) -> None:
        """Testa detecção de portas suspeitas."""
        # Establish baseline
        sensor.baseline_ports["192.168.1.1"] = [22]

        # Add suspicious port (4444 - commonly used by malware)
        sensor.known_hosts["192.168.1.1"] = NetworkHost(ip="192.168.1.1", open_ports=[22, 4444])

        anomalies = sensor.detect_anomalies()

        assert len(anomalies) == 1
        assert anomalies[0].severity == ThreatSeverity.CRITICAL
        assert 4444 in anomalies[0].details["suspicious_ports"]

    def test_detect_anomalies_suspicious_service(self, sensor: NetworkSensorGanglia) -> None:
        """Testa detecção de serviços suspeitos."""
        sensor.known_hosts["192.168.1.1"] = NetworkHost(
            ip="192.168.1.1", services=["ssh", "metasploit"]
        )
        sensor.baseline_ports["192.168.1.1"] = []

        anomalies = sensor.detect_anomalies()

        # Should detect suspicious service
        suspicious_anomalies = [a for a in anomalies if a.type == "suspicious_service_detected"]
        assert len(suspicious_anomalies) > 0
        assert suspicious_anomalies[0].severity == ThreatSeverity.HIGH

    def test_get_network_health_no_hosts(self, sensor: NetworkSensorGanglia) -> None:
        """Testa cálculo de health sem hosts."""
        health = sensor.get_network_health()

        assert health["health_score"] == pytest.approx(100.0)
        assert health["total_hosts"] == 0
        assert health["assessment"] == "HEALTHY"

    def test_get_network_health_healthy_network(self, sensor: NetworkSensorGanglia) -> None:
        """Testa cálculo de health com rede saudável."""
        sensor.known_hosts["192.168.1.1"] = NetworkHost(ip="192.168.1.1", open_ports=[22, 80])

        health = sensor.get_network_health()

        assert health["health_score"] >= 80.0
        assert health["total_hosts"] == 1
        assert health["assessment"] == "HEALTHY"

    def test_get_network_health_suspicious_ports(self, sensor: NetworkSensorGanglia) -> None:
        """Testa cálculo de health com portas suspeitas."""
        sensor.known_hosts["192.168.1.1"] = NetworkHost(ip="192.168.1.1", open_ports=[4444, 5555])

        health = sensor.get_network_health()

        assert health["health_score"] < 80.0
        assert health["hosts_with_suspicious_ports"] == 1

    def test_get_network_health_too_many_ports(self, sensor: NetworkSensorGanglia) -> None:
        """Testa cálculo de health com muitas portas abertas."""
        # Create host with many open ports
        many_ports = list(range(1, 51))  # 50 ports
        sensor.known_hosts["192.168.1.1"] = NetworkHost(ip="192.168.1.1", open_ports=many_ports)

        health = sensor.get_network_health()

        assert health["health_score"] < 100.0
        assert health["avg_open_ports_per_host"] == pytest.approx(50.0)

    @patch("src.security.network_sensors.subprocess.run")
    def test_establish_baseline_success(
        self, mock_run: Mock, sensor: NetworkSensorGanglia, mock_audit_system: Mock
    ) -> None:
        """Testa estabelecimento de baseline com sucesso."""
        sensor.nmap_available = True
        mock_run.return_value = Mock(
            stdout="""
            Nmap scan report for 192.168.1.1
            22/tcp open ssh
            80/tcp open http
            """,
            returncode=0,
        )

        result = sensor.establish_baseline("192.168.1.1")

        assert result is True
        assert "192.168.1.1" in sensor.baseline_ports
        mock_audit_system.log_action.assert_called()

    def test_establish_baseline_failure(self, sensor: NetworkSensorGanglia) -> None:
        """Testa falha ao estabelecer baseline."""
        sensor.nmap_available = False

        result = sensor.establish_baseline("192.168.1.1")

        assert result is False


class TestConvenienceFunctions:
    """Testes para funções de conveniência."""

    @patch("src.security.network_sensors.NetworkSensorGanglia")
    def test_scan_local_network(self, mock_sensor_class: Mock) -> None:
        """Testa função de conveniência scan_local_network."""
        mock_instance = Mock()
        mock_instance.scan_network = Mock(return_value={"hosts": []})
        mock_sensor_class.return_value = mock_instance

        scan_local_network()

        mock_sensor_class.assert_called_once()
        mock_instance.scan_network.assert_called_with("127.0.0.1", scan_type="service")

    @patch("src.security.network_sensors.NetworkSensorGanglia")
    def test_detect_network_anomalies(self, mock_sensor_class: Mock) -> None:
        """Testa função de conveniência detect_network_anomalies."""
        mock_instance = Mock()
        mock_instance.detect_anomalies = Mock(return_value=[])
        mock_sensor_class.return_value = mock_instance

        result = detect_network_anomalies()

        mock_sensor_class.assert_called_once()
        mock_instance.detect_anomalies.assert_called_once()
        assert result == []
