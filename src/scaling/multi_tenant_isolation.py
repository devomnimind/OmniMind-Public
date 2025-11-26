#!/usr/bin/env python3
"""
Multi-Tenant Isolation Module for OmniMind
Implements database isolation, resource quotas, security boundaries,
and tenant-specific configurations.

Features:
- Database-level tenant isolation
- Resource quotas (CPU, memory, storage, network)
- Tenant-specific encryption keys
- Separate audit trails per tenant
- Access control enforcement
- Cross-tenant communication controls
"""

import json
import hashlib
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import threading

from ..audit.immutable_audit import ImmutableAuditSystem, get_audit_system


class TenantStatus(Enum):
    """Tenant account status."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DEACTIVATED = "deactivated"


class ResourceType(Enum):
    """Types of resources that can be quota-limited."""

    CPU = "cpu"  # CPU cores
    MEMORY = "memory"  # RAM in MB
    STORAGE = "storage"  # Disk space in MB
    NETWORK = "network"  # Network bandwidth in Mbps
    API_CALLS = "api_calls"  # API calls per hour
    CONCURRENT_TASKS = "concurrent_tasks"  # Max concurrent tasks


@dataclass
class ResourceQuota:
    """Resource quota definition."""

    resource_type: ResourceType
    limit: float
    current_usage: float = 0.0
    unit: str = ""

    def is_exceeded(self) -> bool:
        """Check if quota is exceeded."""
        return self.current_usage >= self.limit

    def available(self) -> float:
        """Get available quota."""
        return max(0, self.limit - self.current_usage)

    def usage_percentage(self) -> float:
        """Get usage as percentage."""
        if self.limit == 0:
            return 0.0
        return (self.current_usage / self.limit) * 100


@dataclass
class TenantConfig:
    """Tenant-specific configuration."""

    tenant_id: str
    tenant_name: str
    status: TenantStatus = TenantStatus.PENDING
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    encryption_key_id: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    quotas: Dict[str, ResourceQuota] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant_name,
            "status": self.status.value,
            "created_at": self.created_at,
            "encryption_key_id": self.encryption_key_id,
            "settings": self.settings,
            "quotas": {
                k: {
                    "resource_type": v.resource_type.value,
                    "limit": v.limit,
                    "current_usage": v.current_usage,
                    "unit": v.unit,
                }
                for k, v in self.quotas.items()
            },
            "metadata": self.metadata,
        }


class MultiTenantIsolationManager:
    """
    Manages multi-tenant isolation, resource quotas, and security boundaries.

    Features:
    - Tenant registration and configuration
    - Resource quota enforcement
    - Database-level isolation
    - Tenant-specific encryption
    - Separate audit trails
    - Access control
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        audit_system: Optional[ImmutableAuditSystem] = None,
    ):
        """
        Initialize multi-tenant isolation manager.

        Args:
            data_dir: Directory for tenant data storage
            audit_system: Optional audit system instance
        """
        self.data_dir = data_dir or Path.home() / ".omnimind" / "tenants"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.audit_system = audit_system or get_audit_system()
        self.tenants: Dict[str, TenantConfig] = {}
        self.encryption_keys: Dict[str, bytes] = {}
        self._lock = threading.Lock()

        # Load existing tenants
        self._load_tenants()

    def _load_tenants(self) -> None:
        """Load tenant configurations from disk."""
        tenants_file = self.data_dir / "tenants.json"
        if tenants_file.exists():
            try:
                with open(tenants_file, "r") as f:
                    data = json.load(f)
                    for tenant_id, config_dict in data.items():
                        # Reconstruct TenantConfig
                        config = TenantConfig(
                            tenant_id=config_dict["tenant_id"],
                            tenant_name=config_dict["tenant_name"],
                            status=TenantStatus(config_dict["status"]),
                            created_at=config_dict["created_at"],
                            encryption_key_id=config_dict.get("encryption_key_id"),
                            settings=config_dict.get("settings", {}),
                            metadata=config_dict.get("metadata", {}),
                        )

                        # Reconstruct quotas
                        quotas_dict = config_dict.get("quotas", {})
                        for quota_key, quota_data in quotas_dict.items():
                            config.quotas[quota_key] = ResourceQuota(
                                resource_type=ResourceType(quota_data["resource_type"]),
                                limit=quota_data["limit"],
                                current_usage=quota_data.get("current_usage", 0.0),
                                unit=quota_data.get("unit", ""),
                            )

                        self.tenants[tenant_id] = config
            except Exception as e:
                self.audit_system.log_action(
                    "tenant_load_failed",
                    {"error": str(e)},
                    category="security",
                )

    def _save_tenants(self) -> None:
        """Save tenant configurations to disk."""
        tenants_file = self.data_dir / "tenants.json"
        with open(tenants_file, "w") as f:
            json.dump(
                {tid: config.to_dict() for tid, config in self.tenants.items()},
                f,
                indent=2,
            )

    def _generate_tenant_id(self, tenant_name: str) -> str:
        """Generate unique tenant ID."""
        # Create hash from tenant name + random salt
        salt = secrets.token_hex(8)
        data = f"{tenant_name}:{salt}:{datetime.now(timezone.utc).isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _generate_encryption_key(self) -> tuple[str, bytes]:
        """Generate encryption key for tenant."""
        key_id = secrets.token_hex(16)
        key = secrets.token_bytes(32)  # 256-bit key
        return key_id, key

    def create_tenant(
        self,
        tenant_name: str,
        default_quotas: Optional[Dict[ResourceType, float]] = None,
        settings: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TenantConfig:
        """
        Create a new tenant with isolation and quotas.

        Args:
            tenant_name: Human-readable tenant name
            default_quotas: Optional default resource quotas
            settings: Optional tenant-specific settings
            metadata: Optional metadata

        Returns:
            Created TenantConfig
        """
        with self._lock:
            # Generate unique tenant ID
            tenant_id = self._generate_tenant_id(tenant_name)

            # Generate encryption key
            key_id, encryption_key = self._generate_encryption_key()
            self.encryption_keys[key_id] = encryption_key

            # Create default quotas if not provided
            if default_quotas is None:
                default_quotas = {
                    ResourceType.CPU: 2.0,  # 2 CPU cores
                    ResourceType.MEMORY: 4096.0,  # 4GB RAM
                    ResourceType.STORAGE: 10240.0,  # 10GB storage
                    ResourceType.NETWORK: 100.0,  # 100 Mbps
                    ResourceType.API_CALLS: 10000.0,  # 10k calls/hour
                    ResourceType.CONCURRENT_TASKS: 10.0,  # 10 concurrent tasks
                }

            # Create quotas
            quotas = {
                rt.value: ResourceQuota(
                    resource_type=rt,
                    limit=limit,
                    unit=self._get_resource_unit(rt),
                )
                for rt, limit in default_quotas.items()
            }

            # Create tenant config
            config = TenantConfig(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                status=TenantStatus.ACTIVE,
                encryption_key_id=key_id,
                settings=settings or {},
                quotas=quotas,
                metadata=metadata or {},
            )

            self.tenants[tenant_id] = config
            self._save_tenants()

            # Create tenant-specific directories
            tenant_dir = self.data_dir / tenant_id
            tenant_dir.mkdir(parents=True, exist_ok=True)
            (tenant_dir / "data").mkdir(exist_ok=True)
            (tenant_dir / "logs").mkdir(exist_ok=True)
            (tenant_dir / "audit").mkdir(exist_ok=True)

            # Log tenant creation
            self.audit_system.log_action(
                "tenant_created",
                {
                    "tenant_id": tenant_id,
                    "tenant_name": tenant_name,
                    "quotas": {k: v.limit for k, v in quotas.items()},
                },
                category="security",
            )

            return config

    def _get_resource_unit(self, resource_type: ResourceType) -> str:
        """Get unit string for resource type."""
        units = {
            ResourceType.CPU: "cores",
            ResourceType.MEMORY: "MB",
            ResourceType.STORAGE: "MB",
            ResourceType.NETWORK: "Mbps",
            ResourceType.API_CALLS: "calls/hour",
            ResourceType.CONCURRENT_TASKS: "tasks",
        }
        return units.get(resource_type, "")

    def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get tenant configuration by ID."""
        return self.tenants.get(tenant_id)

    def update_tenant_status(self, tenant_id: str, status: TenantStatus) -> bool:
        """
        Update tenant status.

        Args:
            tenant_id: Tenant ID
            status: New status

        Returns:
            True if updated, False if tenant not found
        """
        with self._lock:
            if tenant_id not in self.tenants:
                return False

            old_status = self.tenants[tenant_id].status
            self.tenants[tenant_id].status = status
            self._save_tenants()

            # Log status change
            self.audit_system.log_action(
                "tenant_status_changed",
                {
                    "tenant_id": tenant_id,
                    "old_status": old_status.value,
                    "new_status": status.value,
                },
                category="security",
            )

            return True

    def check_quota(
        self, tenant_id: str, resource_type: ResourceType, amount: float = 0
    ) -> bool:
        """
        Check if tenant has available quota for resource.

        Args:
            tenant_id: Tenant ID
            resource_type: Type of resource
            amount: Amount to check (default 0 checks if any quota available)

        Returns:
            True if quota available, False otherwise
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False

        quota = tenant.quotas.get(resource_type.value)
        if not quota:
            return False

        return quota.available() >= amount

    def consume_quota(
        self, tenant_id: str, resource_type: ResourceType, amount: float
    ) -> bool:
        """
        Consume tenant quota.

        Args:
            tenant_id: Tenant ID
            resource_type: Type of resource
            amount: Amount to consume

        Returns:
            True if quota consumed, False if insufficient or tenant not found
        """
        with self._lock:
            tenant = self.get_tenant(tenant_id)
            if not tenant:
                return False

            quota = tenant.quotas.get(resource_type.value)
            if not quota:
                return False

            if not self.check_quota(tenant_id, resource_type, amount):
                # Log quota exceeded
                self.audit_system.log_action(
                    "quota_exceeded",
                    {
                        "tenant_id": tenant_id,
                        "resource_type": resource_type.value,
                        "requested": amount,
                        "available": quota.available(),
                    },
                    category="security",
                )
                return False

            quota.current_usage += amount
            self._save_tenants()

            return True

    def release_quota(
        self, tenant_id: str, resource_type: ResourceType, amount: float
    ) -> bool:
        """
        Release tenant quota.

        Args:
            tenant_id: Tenant ID
            resource_type: Type of resource
            amount: Amount to release

        Returns:
            True if quota released, False if tenant not found
        """
        with self._lock:
            tenant = self.get_tenant(tenant_id)
            if not tenant:
                return False

            quota = tenant.quotas.get(resource_type.value)
            if not quota:
                return False

            quota.current_usage = max(0, quota.current_usage - amount)
            self._save_tenants()

            return True

    def get_tenant_encryption_key(self, tenant_id: str) -> Optional[bytes]:
        """
        Get tenant-specific encryption key.

        Args:
            tenant_id: Tenant ID

        Returns:
            Encryption key bytes or None if not found
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant or not tenant.encryption_key_id:
            return None

        return self.encryption_keys.get(tenant.encryption_key_id)

    def get_tenant_audit_system(self, tenant_id: str) -> Optional[ImmutableAuditSystem]:
        """
        Get tenant-specific audit system instance.

        Args:
            tenant_id: Tenant ID

        Returns:
            Tenant-specific audit system or None
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None

        # Create tenant-specific audit log directory
        audit_dir = self.data_dir / tenant_id / "audit"
        return ImmutableAuditSystem(log_dir=str(audit_dir))

    def list_tenants(self, status: Optional[TenantStatus] = None) -> List[TenantConfig]:
        """
        List all tenants, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of tenant configurations
        """
        tenants = list(self.tenants.values())
        if status:
            tenants = [t for t in tenants if t.status == status]
        return tenants

    def get_quota_summary(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get quota usage summary for tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            Dict containing quota summary
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return {"error": "Tenant not found"}

        summary: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "tenant_name": tenant.tenant_name,
            "quotas": {},
        }

        for quota_key, quota in tenant.quotas.items():
            summary["quotas"][quota_key] = {
                "limit": quota.limit,
                "current_usage": quota.current_usage,
                "available": quota.available(),
                "usage_percentage": quota.usage_percentage(),
                "exceeded": quota.is_exceeded(),
                "unit": quota.unit,
            }

        return summary

    def enforce_tenant_isolation(self, tenant_id: str, resource_path: Path) -> bool:
        """
        Enforce that resource path is within tenant's isolated directory.

        Args:
            tenant_id: Tenant ID
            resource_path: Path to validate

        Returns:
            True if path is within tenant directory, False otherwise
        """
        tenant_dir = self.data_dir / tenant_id
        try:
            # Resolve to absolute path and check if it's within tenant directory
            abs_path = resource_path.resolve()
            abs_tenant_dir = tenant_dir.resolve()
            return abs_path.is_relative_to(abs_tenant_dir)
        except Exception:
            return False


# Global instance
_isolation_manager: Optional[MultiTenantIsolationManager] = None


def get_isolation_manager() -> MultiTenantIsolationManager:
    """Get singleton isolation manager instance."""
    global _isolation_manager
    if _isolation_manager is None:
        _isolation_manager = MultiTenantIsolationManager()
    return _isolation_manager


def create_tenant(
    tenant_name: str,
    quotas: Optional[Dict[ResourceType, float]] = None,
) -> TenantConfig:
    """Create tenant using global isolation manager."""
    return get_isolation_manager().create_tenant(tenant_name, quotas)


def get_tenant(tenant_id: str) -> Optional[TenantConfig]:
    """Get tenant configuration."""
    return get_isolation_manager().get_tenant(tenant_id)
