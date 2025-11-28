#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Tests for multi-tenant isolation module.
Tests database isolation, resource quotas, security boundaries,
and tenant management.
"""

import tempfile
from pathlib import Path

import pytest

from src.audit.immutable_audit import ImmutableAuditSystem
from src.scaling.multi_tenant_isolation import (
    MultiTenantIsolationManager,
    ResourceQuota,
    ResourceType,
    TenantConfig,
    TenantStatus,
)


class TestResourceQuota:
    """Test resource quota functionality."""

    def test_quota_initialization(self):
        """Test quota initialization."""
        quota = ResourceQuota(
            resource_type=ResourceType.CPU,
            limit=4.0,
            current_usage=2.0,
            unit="cores",
        )

        assert quota.resource_type == ResourceType.CPU
        assert quota.limit == 4.0
        assert quota.current_usage == 2.0
        assert quota.unit == "cores"

    def test_quota_exceeded(self):
        """Test quota exceeded detection."""
        quota = ResourceQuota(
            resource_type=ResourceType.MEMORY,
            limit=1024.0,
            current_usage=1024.0,
        )

        assert quota.is_exceeded()

        quota.current_usage = 512.0
        assert not quota.is_exceeded()

    def test_quota_available(self):
        """Test available quota calculation."""
        quota = ResourceQuota(
            resource_type=ResourceType.STORAGE,
            limit=10240.0,
            current_usage=2048.0,
        )

        assert quota.available() == 8192.0

    def test_quota_usage_percentage(self):
        """Test usage percentage calculation."""
        quota = ResourceQuota(
            resource_type=ResourceType.CPU,
            limit=4.0,
            current_usage=2.0,
        )

        assert quota.usage_percentage() == 50.0


class TestTenantConfig:
    """Test tenant configuration."""

    def test_tenant_config_initialization(self):
        """Test tenant config initialization."""
        config = TenantConfig(
            tenant_id="test123",
            tenant_name="Test Tenant",
            status=TenantStatus.ACTIVE,
        )

        assert config.tenant_id == "test123"
        assert config.tenant_name == "Test Tenant"
        assert config.status == TenantStatus.ACTIVE
        assert config.created_at is not None

    def test_tenant_config_to_dict(self):
        """Test converting tenant config to dict."""
        quota = ResourceQuota(
            resource_type=ResourceType.CPU,
            limit=2.0,
            unit="cores",
        )

        config = TenantConfig(
            tenant_id="test123",
            tenant_name="Test Tenant",
            quotas={"cpu": quota},
        )

        data = config.to_dict()

        assert data["tenant_id"] == "test123"
        assert data["tenant_name"] == "Test Tenant"
        assert "cpu" in data["quotas"]
        assert data["quotas"]["cpu"]["limit"] == 2.0


class TestMultiTenantIsolationManager:
    """Test multi-tenant isolation manager."""

    @pytest.fixture
    def temp_manager(self):
        """Create temporary isolation manager for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "tenants"
            audit_dir = Path(tmpdir) / "audit"
            audit = ImmutableAuditSystem(log_dir=str(audit_dir))
            manager = MultiTenantIsolationManager(
                data_dir=data_dir,
                audit_system=audit,
            )
            yield manager

    def test_manager_initialization(self, temp_manager):
        """Test manager initialization."""
        assert temp_manager.data_dir.exists()
        assert temp_manager.audit_system is not None
        assert isinstance(temp_manager.tenants, dict)

    def test_create_tenant(self, temp_manager):
        """Test tenant creation."""
        config = temp_manager.create_tenant(
            tenant_name="Test Company",
            metadata={"industry": "technology"},
        )

        assert config.tenant_id is not None
        assert config.tenant_name == "Test Company"
        assert config.status == TenantStatus.ACTIVE
        assert config.encryption_key_id is not None
        assert len(config.quotas) > 0
        assert config.metadata["industry"] == "technology"

        # Verify tenant directory was created
        tenant_dir = temp_manager.data_dir / config.tenant_id
        assert tenant_dir.exists()
        assert (tenant_dir / "data").exists()
        assert (tenant_dir / "logs").exists()
        assert (tenant_dir / "audit").exists()

    def test_create_tenant_with_custom_quotas(self, temp_manager):
        """Test tenant creation with custom quotas."""
        custom_quotas = {
            ResourceType.CPU: 8.0,
            ResourceType.MEMORY: 16384.0,
        }

        config = temp_manager.create_tenant(
            tenant_name="Enterprise Client",
            default_quotas=custom_quotas,
        )

        cpu_quota = config.quotas.get(ResourceType.CPU.value)
        assert cpu_quota is not None
        assert cpu_quota.limit == 8.0

        memory_quota = config.quotas.get(ResourceType.MEMORY.value)
        assert memory_quota is not None
        assert memory_quota.limit == 16384.0

    def test_get_tenant(self, temp_manager):
        """Test getting tenant by ID."""
        config = temp_manager.create_tenant("Test Tenant")

        retrieved = temp_manager.get_tenant(config.tenant_id)
        assert retrieved is not None
        assert retrieved.tenant_id == config.tenant_id
        assert retrieved.tenant_name == config.tenant_name

        # Test non-existent tenant
        assert temp_manager.get_tenant("nonexistent") is None

    def test_update_tenant_status(self, temp_manager):
        """Test updating tenant status."""
        config = temp_manager.create_tenant("Test Tenant")

        # Update to suspended
        success = temp_manager.update_tenant_status(
            config.tenant_id,
            TenantStatus.SUSPENDED,
        )
        assert success

        # Verify status changed
        updated = temp_manager.get_tenant(config.tenant_id)
        assert updated.status == TenantStatus.SUSPENDED

        # Test non-existent tenant
        assert not temp_manager.update_tenant_status(
            "nonexistent",
            TenantStatus.ACTIVE,
        )

    def test_check_quota(self, temp_manager):
        """Test quota checking."""
        config = temp_manager.create_tenant("Test Tenant")

        # Should have quota available
        assert temp_manager.check_quota(
            config.tenant_id,
            ResourceType.CPU,
            1.0,
        )

        # Should not have excessive quota
        assert not temp_manager.check_quota(
            config.tenant_id,
            ResourceType.CPU,
            1000.0,
        )

    def test_consume_quota(self, temp_manager):
        """Test quota consumption."""
        config = temp_manager.create_tenant("Test Tenant")

        # Consume some CPU quota
        success = temp_manager.consume_quota(
            config.tenant_id,
            ResourceType.CPU,
            1.0,
        )
        assert success

        # Verify usage increased
        tenant = temp_manager.get_tenant(config.tenant_id)
        cpu_quota = tenant.quotas.get(ResourceType.CPU.value)
        assert cpu_quota.current_usage == 1.0

        # Try to consume more than available
        success = temp_manager.consume_quota(
            config.tenant_id,
            ResourceType.CPU,
            100.0,
        )
        assert not success

    def test_release_quota(self, temp_manager):
        """Test quota release."""
        config = temp_manager.create_tenant("Test Tenant")

        # Consume then release quota
        temp_manager.consume_quota(config.tenant_id, ResourceType.CPU, 1.0)

        success = temp_manager.release_quota(
            config.tenant_id,
            ResourceType.CPU,
            1.0,
        )
        assert success

        # Verify usage decreased
        tenant = temp_manager.get_tenant(config.tenant_id)
        cpu_quota = tenant.quotas.get(ResourceType.CPU.value)
        assert cpu_quota.current_usage == 0.0

    def test_get_tenant_encryption_key(self, temp_manager):
        """Test getting tenant encryption key."""
        config = temp_manager.create_tenant("Test Tenant")

        key = temp_manager.get_tenant_encryption_key(config.tenant_id)
        assert key is not None
        assert isinstance(key, bytes)
        assert len(key) == 32  # 256-bit key

        # Test non-existent tenant
        assert temp_manager.get_tenant_encryption_key("nonexistent") is None

    def test_get_tenant_audit_system(self, temp_manager):
        """Test getting tenant-specific audit system."""
        config = temp_manager.create_tenant("Test Tenant")

        audit = temp_manager.get_tenant_audit_system(config.tenant_id)
        assert audit is not None
        assert isinstance(audit, ImmutableAuditSystem)

        # Verify it's using tenant-specific directory
        expected_path = temp_manager.data_dir / config.tenant_id / "audit"
        assert str(expected_path) in str(audit.log_dir)

    def test_list_tenants(self, temp_manager):
        """Test listing tenants."""
        # Create multiple tenants
        temp_manager.create_tenant("Tenant 1")
        tenant2 = temp_manager.create_tenant("Tenant 2")
        temp_manager.create_tenant("Tenant 3")

        # Suspend one tenant
        temp_manager.update_tenant_status(tenant2.tenant_id, TenantStatus.SUSPENDED)

        # List all tenants
        all_tenants = temp_manager.list_tenants()
        assert len(all_tenants) == 3

        # List only active tenants
        active_tenants = temp_manager.list_tenants(status=TenantStatus.ACTIVE)
        assert len(active_tenants) == 2

        # List only suspended tenants
        suspended_tenants = temp_manager.list_tenants(status=TenantStatus.SUSPENDED)
        assert len(suspended_tenants) == 1

    def test_get_quota_summary(self, temp_manager):
        """Test quota summary generation."""
        config = temp_manager.create_tenant("Test Tenant")

        # Consume some resources
        temp_manager.consume_quota(config.tenant_id, ResourceType.CPU, 1.0)
        temp_manager.consume_quota(config.tenant_id, ResourceType.MEMORY, 512.0)

        summary = temp_manager.get_quota_summary(config.tenant_id)

        assert summary["tenant_id"] == config.tenant_id
        assert summary["tenant_name"] == config.tenant_name
        assert "quotas" in summary

        # Check CPU quota
        cpu_summary = summary["quotas"][ResourceType.CPU.value]
        assert cpu_summary["current_usage"] == 1.0
        assert cpu_summary["usage_percentage"] > 0
        assert "available" in cpu_summary

    def test_enforce_tenant_isolation(self, temp_manager):
        """Test tenant isolation enforcement."""
        config = temp_manager.create_tenant("Test Tenant")

        tenant_dir = temp_manager.data_dir / config.tenant_id
        valid_path = tenant_dir / "data" / "test.txt"
        invalid_path = temp_manager.data_dir / "other_tenant" / "data.txt"

        # Valid path should be allowed
        assert temp_manager.enforce_tenant_isolation(config.tenant_id, valid_path)

        # Invalid path should be blocked
        assert not temp_manager.enforce_tenant_isolation(config.tenant_id, invalid_path)

    def test_persistence(self, temp_manager):
        """Test that tenant data persists."""
        # Create tenant
        config = temp_manager.create_tenant("Test Tenant")
        tenant_id = config.tenant_id

        # Create new manager instance with same data directory
        new_manager = MultiTenantIsolationManager(
            data_dir=temp_manager.data_dir,
            audit_system=temp_manager.audit_system,
        )

        # Verify tenant was loaded
        loaded_config = new_manager.get_tenant(tenant_id)
        assert loaded_config is not None
        assert loaded_config.tenant_id == tenant_id
        assert loaded_config.tenant_name == "Test Tenant"


class TestIntegration:
    """Integration tests for multi-tenant isolation."""

    @pytest.fixture
    def temp_manager(self):
        """Create temporary isolation manager for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "tenants"
            audit_dir = Path(tmpdir) / "audit"
            audit = ImmutableAuditSystem(log_dir=str(audit_dir))
            manager = MultiTenantIsolationManager(
                data_dir=data_dir,
                audit_system=audit,
            )
            yield manager

    def test_multi_tenant_workflow(self, temp_manager):
        """Test complete multi-tenant workflow."""
        # 1. Create multiple tenants
        tenant1 = temp_manager.create_tenant("Company A")
        tenant2 = temp_manager.create_tenant("Company B")

        # 2. Verify isolation
        assert tenant1.tenant_id != tenant2.tenant_id
        assert tenant1.encryption_key_id != tenant2.encryption_key_id

        # 3. Consume resources for tenant 1
        temp_manager.consume_quota(tenant1.tenant_id, ResourceType.CPU, 1.0)

        # 4. Verify tenant 2 unaffected
        tenant2_config = temp_manager.get_tenant(tenant2.tenant_id)
        cpu_quota = tenant2_config.quotas[ResourceType.CPU.value]
        assert cpu_quota.current_usage == 0.0

        # 5. Get separate audit systems
        audit1 = temp_manager.get_tenant_audit_system(tenant1.tenant_id)
        audit2 = temp_manager.get_tenant_audit_system(tenant2.tenant_id)

        # Log actions in separate audit systems
        audit1.log_action("tenant1_action", {"data": "test"}, "general")
        audit2.log_action("tenant2_action", {"data": "test"}, "general")

        # Verify separate audit trails
        assert audit1.log_dir != audit2.log_dir

    def test_quota_enforcement_across_resources(self, temp_manager):
        """Test quota enforcement across different resource types."""
        tenant = temp_manager.create_tenant("Test Company")

        # Consume different resources
        resources = [
            (ResourceType.CPU, 1.0),
            (ResourceType.MEMORY, 1024.0),
            (ResourceType.STORAGE, 2048.0),
        ]

        for resource_type, amount in resources:
            success = temp_manager.consume_quota(
                tenant.tenant_id,
                resource_type,
                amount,
            )
            assert success

        # Verify all quotas were consumed
        summary = temp_manager.get_quota_summary(tenant.tenant_id)
        for resource_type, amount in resources:
            quota = summary["quotas"][resource_type.value]
            assert quota["current_usage"] == amount


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
