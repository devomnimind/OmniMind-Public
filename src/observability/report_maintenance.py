"""
Sistema de Manutenção e Limpeza de Reports com Compressão Automática

Responsável por:
- Compactação diária de reports antigos
- Limpeza de arquivos excessivos
- Rotação de logs
- Otimização de espaço em disco

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-11
"""

import gzip
import json
import logging
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ReportMaintenanceManager:
    """
    Gerenciador de manutenção, compressão e limpeza de reports.

    Características:
    - Compactação automática de reports diários
    - Limpeza de arquivos antigos (configurável)
    - Rotação de logs baseada em tamanho
    - Compressão com gzip
    - Índice de arquivos compactados
    """

    def __init__(
        self,
        reports_dir: str = "data/reports/modules",
        archive_dir: Optional[str] = None,
        retention_days: int = 30,
        compression_threshold_files: int = 1000,
        compression_threshold_size_mb: int = 500,
    ):
        """
        Inicializa gerenciador de manutenção.

        Args:
            reports_dir: Diretório de reports
            archive_dir: Diretório de arquivos compactados (default: reports_dir/archive)
            retention_days: Dias para manter reports descompactados
            compression_threshold_files: Número de arquivos antes de disparar compressão
            compression_threshold_size_mb: Tamanho em MB antes de disparar compressão
        """
        self.reports_dir = Path(reports_dir)
        self.archive_dir = Path(archive_dir or f"{reports_dir}/archive")
        self.retention_days = retention_days
        self.compression_threshold_files = compression_threshold_files
        self.compression_threshold_size_mb = compression_threshold_size_mb

        # Criar diretórios se não existirem
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Arquivo de índice de compactações
        self.compression_index = self.archive_dir / "compression_index.jsonl"

        logger.info(
            f"ReportMaintenanceManager inicializado: {self.reports_dir} → {self.archive_dir}"
        )

    def execute_maintenance(self) -> Dict[str, any]:
        """
        Executa limpeza, compressão e manutenção completa.

        Returns:
            Dicionário com estatísticas de manutenção
        """
        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reports_dir": str(self.reports_dir),
            "archive_dir": str(self.archive_dir),
            "compression": {"files_processed": 0, "size_before_mb": 0, "size_after_mb": 0},
            "cleanup": {"files_deleted": 0, "size_freed_mb": 0},
            "errors": [],
        }

        try:
            # 1. Compactar relatórios antigos
            logger.info("Iniciando compressão de relatórios...")
            compression_stats = self._compress_old_reports()
            stats["compression"] = compression_stats

            # 2. Limpar arquivos excessivamente antigos
            logger.info("Iniciando limpeza de arquivos antigos...")
            cleanup_stats = self._cleanup_expired_files()
            stats["cleanup"] = cleanup_stats

            # 3. Atualizar índice
            self._update_index(stats)

            # 4. Gerar relatório
            stats["total_files_active"] = len(list(self.reports_dir.glob("*.json")))
            stats["total_files_archived"] = len(list(self.archive_dir.glob("*.json.gz")))
            stats["total_size_archived_mb"] = sum(
                f.stat().st_size / (1024 * 1024) for f in self.archive_dir.glob("*.json.gz")
            )

            logger.info(f"Manutenção concluída: {json.dumps(stats, indent=2)}")
            return stats

        except Exception as e:
            logger.error(f"Erro durante manutenção: {e}", exc_info=True)
            stats["errors"].append(str(e))
            return stats

    def _compress_old_reports(self) -> Dict[str, any]:
        """
        Comprime reports antigos (mais antigos que retention_days).

        Returns:
            Estatísticas de compressão
        """
        stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "size_before_mb": 0,
            "size_after_mb": 0,
            "compressed_dates": [],
        }

        try:
            # Obter data de cutoff
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)  # Ontem

            # Agrupar files por data
            files_by_date: Dict[str, List[Path]] = {}
            for json_file in self.reports_dir.glob("*.json"):
                try:
                    # Extrair data do nome ou usar mtime
                    if "_20" in json_file.name:
                        # Formato: autopoietic_cycle_1_20251207_071324.json
                        date_str = json_file.name.split("_")[-2]
                        file_date = datetime.strptime(date_str, "%Y%m%d").replace(
                            tzinfo=timezone.utc
                        )
                    else:
                        file_date = datetime.fromtimestamp(
                            json_file.stat().st_mtime, tz=timezone.utc
                        )

                    date_key = file_date.strftime("%Y%m%d")

                    if date_key not in files_by_date:
                        files_by_date[date_key] = []
                    files_by_date[date_key].append(json_file)

                except Exception as e:
                    logger.debug(f"Erro ao processar data de {json_file.name}: {e}")
                    continue

            # Compactar arquivos de datas antigas
            for date_key in sorted(files_by_date.keys()):
                try:
                    file_date = datetime.strptime(date_key, "%Y%m%d").replace(tzinfo=timezone.utc)

                    # Se arquivo é de ontem ou mais antigo, compactar
                    if file_date < cutoff_date:
                        archive_name = f"reports_{date_key}.tar.gz"
                        archive_path = self.archive_dir / archive_name

                        # Não recompactar se já existe
                        if archive_path.exists():
                            logger.debug(f"Arquivo {archive_name} já compactado")
                            stats["files_skipped"] += len(files_by_date[date_key])
                            continue

                        # Compactar cada arquivo individualmente
                        for json_file in files_by_date[date_key]:
                            try:
                                size_before = json_file.stat().st_size
                                gz_path = json_file.with_suffix(".json.gz")

                                # Compactar
                                with open(json_file, "rb") as f_in:
                                    with gzip.open(gz_path, "wb", compresslevel=9) as f_out:
                                        f_out.write(f_in.read())

                                size_after = gz_path.stat().st_size

                                stats["files_processed"] += 1
                                stats["size_before_mb"] += size_before / (1024 * 1024)
                                stats["size_after_mb"] += size_after / (1024 * 1024)

                                # Remover original
                                json_file.unlink()

                                logger.debug(
                                    f"Compactado: {json_file.name} "
                                    f"({size_before/1024:.1f}KB → {size_after/1024:.1f}KB)"
                                )

                            except Exception as e:
                                logger.error(f"Erro ao compactar {json_file.name}: {e}")
                                continue

                        stats["compressed_dates"].append(date_key)

                except Exception as e:
                    logger.error(f"Erro ao processar data {date_key}: {e}")
                    continue

            return stats

        except Exception as e:
            logger.error(f"Erro durante compressão: {e}")
            stats["error"] = str(e)
            return stats

    def _cleanup_expired_files(self) -> Dict[str, any]:
        """
        Remove arquivos excessivamente antigos (mais antigos que retention_days).

        Returns:
            Estatísticas de limpeza
        """
        stats = {"files_deleted": 0, "size_freed_mb": 0, "deleted_dates": []}

        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)

            # Limpar .json.gz arquivos antigos
            for gz_file in self.archive_dir.glob("*.json.gz"):
                try:
                    if "_20" in gz_file.name:
                        date_str = gz_file.name.split("_")[-3]
                        file_date = datetime.strptime(date_str, "%Y%m%d").replace(
                            tzinfo=timezone.utc
                        )
                    else:
                        file_date = datetime.fromtimestamp(gz_file.stat().st_mtime, tz=timezone.utc)

                    if file_date < cutoff_date:
                        size = gz_file.stat().st_size
                        gz_file.unlink()

                        stats["files_deleted"] += 1
                        stats["size_freed_mb"] += size / (1024 * 1024)
                        stats["deleted_dates"].append(file_date.strftime("%Y%m%d"))

                        logger.info(f"Removido arquivo expirado: {gz_file.name}")

                except Exception as e:
                    logger.error(f"Erro ao remover {gz_file.name}: {e}")
                    continue

            return stats

        except Exception as e:
            logger.error(f"Erro durante limpeza: {e}")
            stats["error"] = str(e)
            return stats

    def _update_index(self, stats: Dict) -> None:
        """
        Atualiza índice de compactações para rastreabilidade.

        Args:
            stats: Estatísticas de manutenção
        """
        try:
            index_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "compression": stats["compression"],
                "cleanup": stats["cleanup"],
            }

            with open(self.compression_index, "a", encoding="utf-8") as f:
                f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

            logger.debug(f"Índice atualizado: {self.compression_index}")

        except Exception as e:
            logger.error(f"Erro ao atualizar índice: {e}")

    def check_maintenance_needed(self) -> Tuple[bool, Dict[str, any]]:
        """
        Verifica se manutenção é necessária baseado em limiares.

        Returns:
            Tuple (needs_maintenance, stats)
        """
        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "needs_compression": False,
            "needs_cleanup": False,
            "reason": "",
        }

        try:
            # Contar arquivos JSON
            json_files = list(self.reports_dir.glob("*.json"))
            stats["total_files"] = len(json_files)

            # Calcular tamanho
            total_size = sum(f.stat().st_size for f in json_files)
            stats["total_size_mb"] = total_size / (1024 * 1024)

            # Verificar limiares
            if stats["total_files"] > self.compression_threshold_files:
                stats["needs_compression"] = True
                stats["reason"] = (
                    f"Excedido limite de arquivos ({stats['total_files']} > {self.compression_threshold_files})"
                )

            if stats["total_size_mb"] > self.compression_threshold_size_mb:
                stats["needs_compression"] = True
                stats["reason"] = (
                    f"Excedido limite de tamanho ({stats['total_size_mb']:.1f}MB > {self.compression_threshold_size_mb}MB)"
                )

            # Verificar se existem arquivos para limpeza
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            for json_file in json_files:
                if "_20" in json_file.name:
                    try:
                        date_str = json_file.name.split("_")[-2]
                        file_date = datetime.strptime(date_str, "%Y%m%d").replace(
                            tzinfo=timezone.utc
                        )
                        if file_date < cutoff_date:
                            stats["needs_cleanup"] = True
                            break
                    except:
                        pass

            needs_maintenance = stats["needs_compression"] or stats["needs_cleanup"]
            return needs_maintenance, stats

        except Exception as e:
            logger.error(f"Erro ao verificar necessidade de manutenção: {e}")
            return False, stats


# Singleton global
_maintenance_manager: Optional[ReportMaintenanceManager] = None


def get_report_maintenance_manager(
    reports_dir: str = "data/reports/modules",
) -> ReportMaintenanceManager:
    """
    Obtém ou cria instância singleton do gerenciador de manutenção.

    Args:
        reports_dir: Diretório de reports

    Returns:
        ReportMaintenanceManager singleton
    """
    global _maintenance_manager
    if _maintenance_manager is None:
        _maintenance_manager = ReportMaintenanceManager(reports_dir=reports_dir)
    return _maintenance_manager
