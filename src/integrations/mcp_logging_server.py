"""
MCP Logging Server - Servidor MCP para busca e análise de logs.

Este servidor MCP fornece acesso a logs do sistema:
- Busca em logs (audit, security, agents, etc.)
- Logs recentes
- Integração com ImmutableAuditSystem
- Filtros e queries avançadas

Autor: Fabrício da Silva + assistência de IA
Data: 2025-01-XX
"""

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.audit.immutable_audit import get_audit_system
from src.audit.log_analyzer import AuditLogAnalyzer, QueryFilter
from src.integrations.mcp_server import MCPServer

logger = logging.getLogger(__name__)

# Fontes de log padrão
DEFAULT_LOG_SOURCES = [
    "logs/omnimind.log",
    "logs/security.log",
    "logs/audit.log",
    "logs/audit_chain.log",
    "logs/agents.log",
]


class LoggingMCPServer(MCPServer):
    """Servidor MCP para busca e análise de logs."""

    def __init__(self, log_sources: Optional[List[str]] = None) -> None:
        """Inicializa o servidor de logging MCP.

        Args:
            log_sources: Lista de caminhos de arquivos de log (opcional)
        """
        super().__init__()

        self.log_sources = log_sources or DEFAULT_LOG_SOURCES
        self.log_paths = [Path(source) for source in self.log_sources]

        # Sistema de auditoria
        self.audit_system = get_audit_system()
        self.log_analyzer = AuditLogAnalyzer(audit_system=self.audit_system)

        # Registrar métodos MCP (preserva initialize())
        self.register_methods(
            {
                "search_logs": self.search_logs,
                "get_recent_logs": self.get_recent_logs,
                "get_audit_logs": self.get_audit_logs,
                "get_log_statistics": self.get_log_statistics,
                "export_logs": self.export_logs,
            }
        )

        logger.info("LoggingMCPServer inicializado com %d fontes de log", len(self.log_sources))

    def search_logs(
        self,
        query: str,
        limit: int = 100,
        log_source: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Busca em logs usando query.

        Args:
            query: Termo de busca (suporta regex)
            limit: Número máximo de resultados
            log_source: Fonte de log específica (opcional)
            start_date: Data de início (ISO format, opcional)
            end_date: Data de fim (ISO format, opcional)

        Returns:
            Dict com resultados da busca
        """
        try:
            results: List[Dict[str, Any]] = []

            # Parsear datas se fornecidas
            start_dt = None
            end_dt = None
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                except Exception:
                    pass
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                except Exception:
                    pass

            # Buscar em arquivos de log
            log_files = [Path(log_source)] if log_source else self.log_paths

            pattern = re.compile(query, re.IGNORECASE)

            for log_file in log_files:
                if not log_file.exists():
                    continue

                try:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if not line.strip():
                                continue

                            # Filtrar por data se fornecida
                            if start_dt or end_dt:
                                # Tentar extrair timestamp da linha
                                line_dt = self._extract_timestamp(line)
                                if line_dt:
                                    if start_dt and line_dt < start_dt:
                                        continue
                                    if end_dt and line_dt > end_dt:
                                        continue

                            # Buscar padrão
                            if pattern.search(line):
                                results.append(
                                    {
                                        "source": str(log_file),
                                        "line": line_num,
                                        "content": line.strip(),
                                        "timestamp": self._extract_timestamp(line),
                                    }
                                )

                                if len(results) >= limit:
                                    break

                except Exception as e:
                    logger.debug("Erro ao ler arquivo de log %s: %s", log_file, e)
                    continue

                if len(results) >= limit:
                    break

            # Ordenar por timestamp (mais recente primeiro)
            results.sort(
                key=lambda x: x.get("timestamp") or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )

            logger.debug("Busca em logs: query='%s', results=%d", query, len(results))

            return {
                "query": query,
                "results": results[:limit],
                "count": len(results),
                "sources_searched": [str(f) for f in log_files],
            }

        except Exception as e:
            logger.error("Erro ao buscar logs: %s", e)
            return {
                "query": query,
                "results": [],
                "count": 0,
                "error": str(e),
            }

    def get_recent_logs(
        self,
        limit: int = 100,
        log_source: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Obtém logs recentes.

        Args:
            limit: Número máximo de logs
            log_source: Fonte de log específica (opcional)
            level: Nível de log (DEBUG, INFO, WARNING, ERROR, opcional)

        Returns:
            Dict com logs recentes
        """
        try:
            logs: List[Dict[str, Any]] = []

            log_files = [Path(log_source)] if log_source else self.log_paths

            for log_file in log_files:
                if not log_file.exists():
                    continue

                try:
                    # Ler últimas linhas do arquivo
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        # Pegar últimas N linhas
                        recent_lines = lines[-limit:] if len(lines) > limit else lines

                        for line_num, line in enumerate(
                            recent_lines, len(lines) - len(recent_lines) + 1
                        ):
                            if not line.strip():
                                continue

                            # Filtrar por nível se fornecido
                            if level and level.upper() not in line.upper():
                                continue

                            logs.append(
                                {
                                    "source": str(log_file),
                                    "line": line_num,
                                    "content": line.strip(),
                                    "timestamp": self._extract_timestamp(line),
                                    "level": self._extract_log_level(line),
                                }
                            )

                except Exception as e:
                    logger.debug("Erro ao ler arquivo de log %s: %s", log_file, e)
                    continue

            # Ordenar por timestamp (mais recente primeiro)
            logs.sort(
                key=lambda x: x.get("timestamp") or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )

            return {
                "logs": logs[:limit],
                "count": len(logs),
                "sources": [str(f) for f in log_files],
            }

        except Exception as e:
            logger.error("Erro ao obter logs recentes: %s", e)
            return {
                "logs": [],
                "count": 0,
                "error": str(e),
            }

    def get_audit_logs(
        self,
        category: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Obtém logs do sistema de auditoria imutável.

        Args:
            category: Categoria de auditoria (opcional)
            action: Ação específica (opcional)
            limit: Número máximo de resultados
            start_date: Data de início (ISO format, opcional)
            end_date: Data de fim (ISO format, opcional)

        Returns:
            Dict com logs de auditoria
        """
        try:
            # Criar filtro
            start_dt = None
            end_dt = None
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                except Exception:
                    pass
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                except Exception:
                    pass

            filter_obj = QueryFilter(
                start_date=start_dt,
                end_date=end_dt,
                categories=[category] if category else None,
            )

            # Buscar logs
            events = self.log_analyzer.query(filter=filter_obj, limit=limit)

            # Filtrar por ação se fornecido
            if action:
                events = [e for e in events if e.get("action") == action]

            return {
                "events": events[:limit],
                "count": len(events),
                "category": category,
                "action": action,
            }

        except Exception as e:
            logger.error("Erro ao obter logs de auditoria: %s", e)
            return {
                "events": [],
                "count": 0,
                "error": str(e),
            }

    def get_log_statistics(
        self,
        log_source: Optional[str] = None,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """Obtém estatísticas dos logs.

        Args:
            log_source: Fonte de log específica (opcional)
            hours: Número de horas para análise

        Returns:
            Dict com estatísticas
        """
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(hours=hours)

            # Usar log analyzer para estatísticas
            stats = self.log_analyzer.generate_statistics(start_date=start_date, end_date=end_date)

            return {
                "period_hours": hours,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "statistics": stats,
            }

        except Exception as e:
            logger.error("Erro ao obter estatísticas: %s", e)
            return {
                "statistics": {},
                "error": str(e),
            }

    def export_logs(
        self,
        output_path: str,
        query: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = "jsonl",
    ) -> Dict[str, Any]:
        """Exporta logs para arquivo.

        Args:
            output_path: Caminho do arquivo de saída
            query: Query opcional para filtrar
            start_date: Data de início (opcional)
            end_date: Data de fim (opcional)
            format: Formato de exportação (jsonl, json, txt)

        Returns:
            Dict com status da exportação
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Buscar logs
            if query:
                results = self.search_logs(
                    query=query,
                    limit=10000,
                    start_date=start_date,
                    end_date=end_date,
                )
                logs = results.get("results", [])
            else:
                results = self.get_recent_logs(limit=10000)
                logs = results.get("logs", [])

            # Exportar no formato solicitado
            if format == "jsonl":
                with open(output_file, "w") as f:
                    for log in logs:
                        f.write(json.dumps(log) + "\n")
            elif format == "json":
                with open(output_file, "w") as f:
                    json.dump({"logs": logs}, f, indent=2)
            else:  # txt
                with open(output_file, "w") as f:
                    for log in logs:
                        f.write(log.get("content", "") + "\n")

            logger.info("Logs exportados: %s (%d entradas)", output_path, len(logs))

            return {
                "status": "success",
                "output_path": str(output_file),
                "entries_exported": len(logs),
                "format": format,
            }

        except Exception as e:
            logger.error("Erro ao exportar logs: %s", e)
            return {
                "status": "error",
                "error": str(e),
            }

    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """Extrai timestamp de uma linha de log.

        Args:
            line: Linha de log

        Returns:
            Datetime ou None
        """
        # Padrões comuns de timestamp
        patterns = [
            r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})",
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
            r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[.,]\d+)\]",
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    ts_str = match.group(1).replace("T", " ").replace(",", ".")
                    # Tentar parsear
                    if "." in ts_str:
                        dt = datetime.strptime(ts_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
                    else:
                        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    return dt.replace(tzinfo=timezone.utc)
                except Exception:
                    continue

        return None

    def _extract_log_level(self, line: str) -> Optional[str]:
        """Extrai nível de log de uma linha.

        Args:
            line: Linha de log

        Returns:
            Nível de log ou None
        """
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            if level in line.upper():
                return level
        return None


if __name__ == "__main__":
    server = LoggingMCPServer()
    try:
        server.start()
        logger.info("Logging MCPServer running...")
        if server._thread:
            server._thread.join()
    except KeyboardInterrupt:
        server.stop()
