#!/usr/bin/env python3
"""
Timezone Adapter for OmniMind
==============================

Adapta assinaturas de data/hora e relatórios para o timezone local.
O sistema detecta o timezone e produz timestamps verdadeiros em relatórios.

Uso:
    from src.utils.timezone_adapter import TimezoneAdapter

    tz = TimezoneAdapter()
    print(tz.now())  # Data/hora correta do sistema
    print(tz.get_report_timestamp())  # Para relatórios
    print(tz.get_log_prefix())  # Para logs
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytz

logger = logging.getLogger(__name__)


class TimezoneAdapter:
    """Gerencia timezones e produz assinaturas de data/hora verdadeiras."""

    def __init__(self, tz_str: Optional[str] = None):
        """Inicializa adapter com timezone.

        Args:
            tz_str: Timezone string (ex: 'America/Sao_Paulo').
                    Se None, detecta do sistema.
        """
        self.tz_str = tz_str or self._detect_timezone()
        try:
            self.tz = pytz.timezone(self.tz_str)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Timezone inválido: {self.tz_str}, usando UTC")
            self.tz = pytz.UTC
            self.tz_str = "UTC"

    @staticmethod
    def _detect_timezone() -> str:
        """Detecta timezone do sistema.

        Returns:
            String de timezone (ex: 'America/Sao_Paulo')
        """
        # Tenta via TZ env var
        if "TZ" in os.environ:
            return os.environ["TZ"]

        # Tenta via /etc/timezone
        try:
            if Path("/etc/timezone").exists():
                with open("/etc/timezone") as f:
                    return f.read().strip()
        except Exception as e:
            logger.debug(f"Não conseguiu ler /etc/timezone: {e}")

        # Tenta via systemd timedatectl (Linux)
        try:
            import subprocess

            result = subprocess.run(
                ["timedatectl", "show", "-p", "Timezone", "--value"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Não conseguiu usar timedatectl: {e}")

        # Default
        logger.warning("Não foi possível detectar timezone, usando UTC")
        return "UTC"

    def now(self) -> datetime:
        """Retorna data/hora atual no timezone do sistema.

        Returns:
            datetime com timezone correto
        """
        return datetime.now(self.tz)

    def now_utc(self) -> datetime:
        """Retorna data/hora atual em UTC.

        Returns:
            datetime em UTC
        """
        return datetime.now(pytz.UTC)

    def get_report_timestamp(self) -> str:
        """Gera timestamp para relatórios no formato local.

        Returns:
            String formatada: "2025-12-12T15:47:47-03:00 (São Paulo)"
        """
        now = self.now()
        tz_name = self._get_friendly_tz_name()
        offset = now.strftime("%z")
        # Formata offset como -03:00
        if offset:
            offset = f"{offset[:-2]}:{offset[-2:]}"
        return f"{now.isoformat()} ({tz_name})"

    def get_log_prefix(self) -> str:
        """Gera prefixo para logs com data/hora correta.

        Returns:
            String formatada: "2025-12-12 15:47:47 -03"
        """
        now = self.now()
        offset = now.strftime("%z")
        # Formata offset como -03
        if offset:
            offset = f"{offset[:-2]}"
        return now.strftime(f"%Y-%m-%d %H:%M:%S {offset}").strip()

    def get_iso_timestamp(self) -> str:
        """Gera timestamp ISO 8601 completo.

        Returns:
            String formatada: "2025-12-12T15:47:47-03:00"
        """
        return self.now().isoformat()

    def get_filename_timestamp(self) -> str:
        """Gera timestamp seguro para nomes de arquivo.

        Returns:
            String formatada: "20251212_154747"
        """
        return self.now().strftime("%Y%m%d_%H%M%S")

    def get_report_header(self) -> str:
        """Gera header completo para relatórios.

        Returns:
            String com data/hora/timezone
        """
        now = self.now()
        tz_name = self._get_friendly_tz_name()
        return (
            f"Gerado em: {now.strftime('%d de %B de %Y às %H:%M:%S')} "
            f"({tz_name} UTC{now.strftime('%z')[:-2]})"
        )

    def _get_friendly_tz_name(self) -> str:
        """Retorna nome amigável do timezone.

        Returns:
            String com nome localizado
        """
        # Mapa de timezones para nomes amigáveis
        friendly_names = {
            "America/Sao_Paulo": "São Paulo",
            "America/Brasilia": "Brasília",
            "America/Manaus": "Manaus",
            "America/Recife": "Recife",
            "Europe/Lisbon": "Lisboa",
            "Europe/London": "Londres",
            "Europe/Berlin": "Berlim",
            "America/New_York": "Nova York",
            "America/Los_Angeles": "Los Angeles",
            "Asia/Tokyo": "Tóquio",
            "Australia/Sydney": "Sydney",
            "UTC": "UTC",
        }
        return friendly_names.get(self.tz_str, self.tz_str)

    def to_local(self, dt: datetime) -> datetime:
        """Converte datetime para timezone local.

        Args:
            dt: datetime em qualquer timezone

        Returns:
            datetime no timezone local
        """
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        return dt.astimezone(self.tz)

    def to_utc(self, dt: datetime) -> datetime:
        """Converte datetime para UTC.

        Args:
            dt: datetime em qualquer timezone

        Returns:
            datetime em UTC
        """
        if dt.tzinfo is None:
            dt = self.tz.localize(dt)
        return dt.astimezone(pytz.UTC)


# Instância global padrão
_global_adapter: Optional[TimezoneAdapter] = None


def get_global_timezone_adapter() -> TimezoneAdapter:
    """Retorna instância global de TimezoneAdapter.

    Returns:
        TimezoneAdapter singleton
    """
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = TimezoneAdapter()
    return _global_adapter


def set_global_timezone(tz_str: str) -> None:
    """Define timezone global.

    Args:
        tz_str: String de timezone (ex: 'America/Sao_Paulo')
    """
    global _global_adapter
    _global_adapter = TimezoneAdapter(tz_str)


if __name__ == "__main__":
    # Demo
    tz = TimezoneAdapter()
    print(f"Timezone detectado: {tz.tz_str}")
    print(f"Agora: {tz.now()}")
    print(f"Timestamp relatório: {tz.get_report_timestamp()}")
    print(f"Prefixo log: {tz.get_log_prefix()}")
    print(f"Header relatório:\n{tz.get_report_header()}")
