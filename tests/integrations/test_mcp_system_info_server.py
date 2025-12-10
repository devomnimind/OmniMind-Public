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

from typing import Any, Dict

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
        """Testa recuperação de informações da GPU.

        NOTA: Retorna valores reais do sistema via nvidia-smi ou PyTorch.
        Não compara valores específicos, apenas estrutura.
        """
        server = SystemInfoMCPServer()
        result = server.get_gpu_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "name" in result
        assert "vram_gb" in result
        assert "available" in result
        # Verificar tipos e valores razoáveis (não valores hardcoded)
        assert isinstance(result["name"], str)
        assert isinstance(result["vram_gb"], (int, float))
        assert isinstance(result["available"], bool)

    def test_get_gpu_info_structure(self) -> None:
        """Testa estrutura dos dados da GPU."""
        server = SystemInfoMCPServer()
        result = server.get_gpu_info()
        assert isinstance(result["name"], str)
        assert isinstance(result["vram_gb"], int)
        assert len(result["name"]) > 0
        assert result["vram_gb"] > 0

    def test_get_cpu_info_basic(self) -> None:
        """Testa recuperação de informações da CPU.

        NOTA: Retorna valores reais do sistema via platform.processor() e psutil.
        Não compara valores específicos, apenas estrutura e tipos.
        """
        server = SystemInfoMCPServer()
        result = server.get_cpu_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "model" in result
        assert "cores_physical" in result  # Campo correto da implementação
        assert "cores_logical" in result
        # Verificar tipos e valores razoáveis (não valores hardcoded)
        assert isinstance(result["model"], str)
        assert isinstance(result["cores_physical"], int)
        assert isinstance(result["cores_logical"], int)
        assert result["cores_physical"] > 0
        assert result["cores_logical"] > 0

    def test_get_cpu_info_structure(self) -> None:
        """Testa estrutura dos dados da CPU."""
        server = SystemInfoMCPServer()
        result = server.get_cpu_info()
        assert isinstance(result["model"], str)
        assert isinstance(result["cores_physical"], int)  # Campo correto
        assert isinstance(result["cores_logical"], int)
        assert len(result["model"]) > 0
        assert result["cores_physical"] > 0
        assert result["cores_logical"] > 0

    def test_get_memory_info_basic(self) -> None:
        """Testa recuperação de informações de memória.

        NOTA: Retorna valores reais do sistema via psutil.virtual_memory().
        Não compara valores específicos, apenas estrutura e consistência.
        """
        server = SystemInfoMCPServer()
        result = server.get_memory_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "total_gb" in result
        assert "available_gb" in result
        # Verificar tipos e valores razoáveis (não valores hardcoded)
        assert isinstance(result["total_gb"], (int, float))
        assert isinstance(result["available_gb"], (int, float))
        assert result["total_gb"] > 0
        assert result["available_gb"] >= 0
        assert result["available_gb"] <= result["total_gb"]

    def test_get_memory_info_structure(self) -> None:
        """Testa estrutura dos dados de memória."""
        server = SystemInfoMCPServer()
        result = server.get_memory_info()
        assert isinstance(result["total_gb"], (int, float))  # Pode ser float
        assert isinstance(result["available_gb"], (int, float))
        assert result["total_gb"] > 0
        assert result["available_gb"] >= 0  # Pode ser 0 em sistemas com pouca memória
        assert result["available_gb"] <= result["total_gb"]

    def test_get_disk_info_basic(self) -> None:
        """Testa recuperação de informações de disco.

        NOTA: Retorna valores reais do sistema via psutil.disk_usage().
        Não compara valores específicos, apenas estrutura e consistência.
        """
        server = SystemInfoMCPServer()
        result = server.get_disk_info()
        assert result is not None
        assert isinstance(result, dict)
        assert "total_gb" in result
        assert "free_gb" in result
        # Verificar tipos e valores razoáveis (não valores hardcoded)
        assert isinstance(result["total_gb"], (int, float))
        assert isinstance(result["free_gb"], (int, float))
        assert result["total_gb"] > 0
        assert result["free_gb"] >= 0
        assert result["free_gb"] <= result["total_gb"]

    def test_get_disk_info_structure(self) -> None:
        """Testa estrutura dos dados de disco."""
        server = SystemInfoMCPServer()
        result = server.get_disk_info()
        assert isinstance(result["total_gb"], (int, float))  # Pode ser float
        assert isinstance(result["free_gb"], (int, float))
        assert result["total_gb"] > 0
        assert result["free_gb"] >= 0
        assert result["free_gb"] <= result["total_gb"]

    def test_get_temperature_basic(self) -> None:
        """Testa recuperação de informações de temperatura.

        NOTA: Retorna valores reais do sistema via psutil.sensors_temperatures()
        ou None se não disponível. Temperaturas variam constantemente.
        Não compara valores específicos, apenas estrutura.
        """
        server = SystemInfoMCPServer()
        result = server.get_temperature()
        assert result is not None
        assert isinstance(result, dict)
        assert "cpu_c" in result
        assert "gpu_c" in result
        assert "available" in result
        # Valores podem ser None se sensores não disponíveis
        assert result["cpu_c"] is None or isinstance(result["cpu_c"], (int, float))
        assert result["gpu_c"] is None or isinstance(result["gpu_c"], (int, float))
        assert isinstance(result["available"], bool)

    def test_get_temperature_structure(self) -> None:
        """Testa estrutura dos dados de temperatura."""
        server = SystemInfoMCPServer()
        result = server.get_temperature()
        # Valores podem ser None se sensores não disponíveis
        if result["cpu_c"] is not None:
            assert isinstance(result["cpu_c"], (int, float))
            # Temperaturas razoáveis entre 0 e 100 graus Celsius
            assert 0 <= result["cpu_c"] <= 100
        if result["gpu_c"] is not None:
            assert isinstance(result["gpu_c"], (int, float))
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
            result: Dict[str, Any] = method()  # type: ignore[operator]
            assert isinstance(result, dict)
            assert len(result) > 0

    def test_gpu_info_consistency(self) -> None:
        """Testa consistência das informações da GPU."""
        server = SystemInfoMCPServer()
        result1 = server.get_gpu_info()
        result2 = server.get_gpu_info()
        assert result1 == result2

    def test_cpu_info_consistency(self) -> None:
        """Testa consistência das informações da CPU.

        NOTA: Campos dinâmicos (usage_percent, frequency_mhz) podem variar
        entre chamadas. Verificamos apenas campos estáticos.
        """
        server = SystemInfoMCPServer()
        result1 = server.get_cpu_info()
        result2 = server.get_cpu_info()
        # Campos estáticos devem ser iguais
        assert result1["model"] == result2["model"]
        assert result1["cores_physical"] == result2["cores_physical"]
        assert result1["cores_logical"] == result2["cores_logical"]
        assert result1["architecture"] == result2["architecture"]
        # Campos dinâmicos podem variar, mas devem existir
        assert "usage_percent" in result1
        assert "usage_percent" in result2

    def test_memory_info_consistency(self) -> None:
        """Testa consistência das informações de memória.

        NOTA: Campos dinâmicos (available_gb, used_gb, percent) podem variar
        entre chamadas. Verificamos apenas campos estáticos (total_gb).
        """
        server = SystemInfoMCPServer()
        result1 = server.get_memory_info()
        result2 = server.get_memory_info()
        # Campos estáticos devem ser iguais
        assert result1["total_gb"] == result2["total_gb"]
        # Campos dinâmicos podem variar, mas devem manter consistência
        assert result1["available_gb"] >= 0
        assert result2["available_gb"] >= 0
        assert result1["available_gb"] <= result1["total_gb"]
        assert result2["available_gb"] <= result2["total_gb"]

    def test_disk_info_consistency(self) -> None:
        """Testa consistência das informações de disco."""
        server = SystemInfoMCPServer()
        result1 = server.get_disk_info()
        result2 = server.get_disk_info()
        assert result1 == result2

    def test_temperature_consistency(self) -> None:
        """Testa consistência das informações de temperatura.

        NOTA: Temperaturas variam constantemente e podem não estar disponíveis.
        Verificamos apenas estrutura e disponibilidade.
        """
        server = SystemInfoMCPServer()
        result1 = server.get_temperature()
        result2 = server.get_temperature()
        # Estrutura deve ser consistente
        assert result1["available"] == result2["available"]
        # Se disponível, valores podem variar mas devem estar em range razoável
        if result1["available"]:
            if result1["cpu_c"] is not None and result2["cpu_c"] is not None:
                assert 0 <= result1["cpu_c"] <= 100
                assert 0 <= result2["cpu_c"] <= 100
            if result1["gpu_c"] is not None and result2["gpu_c"] is not None:
                assert 0 <= result1["gpu_c"] <= 100
                assert 0 <= result2["gpu_c"] <= 100

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
