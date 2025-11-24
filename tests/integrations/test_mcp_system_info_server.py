"""Testes para SystemInfoMCPServer (mcp_system_info_server.py).

Cobertura de:
- Inicialização do servidor
- Informações da GPU (get_gpu_info)
- Informações da CPU (get_cpu_info)
- Informações de memória (get_memory_info)
- Informações de disco (get_disk_info)
- Informações de temperatura (get_temperature)
"""

from __future__ import annotations

from src.integrations.mcp_system_info_server import SystemInfoMCPServer

class TestSystemInfoMCPServer:
    """Testes para o servidor MCP de informações do sistema."""

    def test_initialization(self) -> None:
        """Testa inicialização do SystemInfoMCPServer."""
        server = SystemInfoMCPServer()
        assert server is not None
        expected_methods = [
            "get_gpu_info",
            "get_cpu_info",
            "get_memory_info",
            "get_disk_info",
            "get_temperature",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_get_gpu_info_basic(self) -> None:
        """Testa recuperação de informações da GPU."""
        server = SystemInfoMCPServer()
        result = server.get_gpu_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "name" in result
        assert "vram_gb" in result
        assert result["name"] == "NVIDIA GeForce GTX 1650"
        assert result["vram_gb"] == 4

    def test_get_gpu_info_structure(self) -> None:
        """Testa estrutura dos dados da GPU."""
        server = SystemInfoMCPServer()
        result = server.get_gpu_info()
        assert isinstance(result["name"], str)
        assert isinstance(result["vram_gb"], int)
        assert len(result["name"]) > 0
        assert result["vram_gb"] > 0

    def test_get_cpu_info_basic(self) -> None:
        """Testa recuperação de informações da CPU."""
        server = SystemInfoMCPServer()
        result = server.get_cpu_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "model" in result
        assert "cores" in result
        assert result["model"] == "Intel Core i5"
        assert result["cores"] == 4

    def test_get_cpu_info_structure(self) -> None:
        """Testa estrutura dos dados da CPU."""
        server = SystemInfoMCPServer()
        result = server.get_cpu_info()
        assert isinstance(result["model"], str)
        assert isinstance(result["cores"], int)
        assert len(result["model"]) > 0
        assert result["cores"] > 0

    def test_get_memory_info_basic(self) -> None:
        """Testa recuperação de informações de memória."""
        server = SystemInfoMCPServer()
        result = server.get_memory_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "total_gb" in result
        assert "available_gb" in result
        assert result["total_gb"] == 24
        assert result["available_gb"] == 18

    def test_get_memory_info_structure(self) -> None:
        """Testa estrutura dos dados de memória."""
        server = SystemInfoMCPServer()
        result = server.get_memory_info()
        assert isinstance(result["total_gb"], int)
        assert isinstance(result["available_gb"], int)
        assert result["total_gb"] > 0
        assert result["available_gb"] > 0
        assert result["available_gb"] <= result["total_gb"]

    def test_get_disk_info_basic(self) -> None:
        """Testa recuperação de informações de disco."""
        server = SystemInfoMCPServer()
        result = server.get_disk_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "total_gb" in result
        assert "free_gb" in result
        assert result["total_gb"] == 256
        assert result["free_gb"] == 100

    def test_get_disk_info_structure(self) -> None:
        """Testa estrutura dos dados de disco."""
        server = SystemInfoMCPServer()
        result = server.get_disk_info()
        assert isinstance(result["total_gb"], int)
        assert isinstance(result["free_gb"], int)
        assert result["total_gb"] > 0
        assert result["free_gb"] >= 0
        assert result["free_gb"] <= result["total_gb"]

    def test_get_temperature_basic(self) -> None:
        """Testa recuperação de informações de temperatura."""
        server = SystemInfoMCPServer()
        result = server.get_temperature()
        assert result is not None
        assert isinstance(result, dict)
        assert "cpu_c" in result
        assert "gpu_c" in result
        assert result["cpu_c"] == 45.0
        assert result["gpu_c"] == 42.0

    def test_get_temperature_structure(self) -> None:
        """Testa estrutura dos dados de temperatura."""
        server = SystemInfoMCPServer()
        result = server.get_temperature()
        assert isinstance(result["cpu_c"], float)
        assert isinstance(result["gpu_c"], float)
        # Temperaturas razoáveis entre 0 e 100 graus Celsius
        assert 0 <= result["cpu_c"] <= 100
        assert 0 <= result["gpu_c"] <= 100

    def test_methods_registered(self) -> None:
        """Testa se todos os métodos estão registrados."""
        server = SystemInfoMCPServer()
        expected_methods = [
            "get_gpu_info",
            "get_cpu_info",
            "get_memory_info",
            "get_disk_info",
            "get_temperature",
            # Métodos herdados de MCPServer
            "read_file",
            "write_file",
            "list_dir",
            "stat",
            "get_metrics",
        ]
        for method in expected_methods:
            assert method in server._methods

    def test_all_methods_return_dict(self) -> None:
        """Testa se todos os métodos retornam dicionários."""
        server = SystemInfoMCPServer()
        methods = [
            server.get_gpu_info,
            server.get_cpu_info,
            server.get_memory_info,
            server.get_disk_info,
            server.get_temperature,
        ]
        for method in methods:
            result = method()
            assert isinstance(result, dict)
            assert len(result) > 0

    def test_gpu_info_consistency(self) -> None:
        """Testa consistência das informações da GPU."""
        server = SystemInfoMCPServer()
        result1 = server.get_gpu_info()
        result2 = server.get_gpu_info()
        assert result1 == result2

    def test_cpu_info_consistency(self) -> None:
        """Testa consistência das informações da CPU."""
        server = SystemInfoMCPServer()
        result1 = server.get_cpu_info()
        result2 = server.get_cpu_info()
        assert result1 == result2

    def test_memory_info_consistency(self) -> None:
        """Testa consistência das informações de memória."""
        server = SystemInfoMCPServer()
        result1 = server.get_memory_info()
        result2 = server.get_memory_info()
        assert result1 == result2

    def test_disk_info_consistency(self) -> None:
        """Testa consistência das informações de disco."""
        server = SystemInfoMCPServer()
        result1 = server.get_disk_info()
        result2 = server.get_disk_info()
        assert result1 == result2

    def test_temperature_consistency(self) -> None:
        """Testa consistência das informações de temperatura."""
        server = SystemInfoMCPServer()
        result1 = server.get_temperature()
        result2 = server.get_temperature()
        assert result1 == result2

    def test_all_info_methods_together(self) -> None:
        """Testa execução de todos os métodos de informação juntos."""
        server = SystemInfoMCPServer()
        gpu = server.get_gpu_info()
        cpu = server.get_cpu_info()
        memory = server.get_memory_info()
        disk = server.get_disk_info()
        temp = server.get_temperature()

        assert all([gpu, cpu, memory, disk, temp])
        assert all(isinstance(x, dict) for x in [gpu, cpu, memory, disk, temp])
