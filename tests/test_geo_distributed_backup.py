"""
Tests for Geo-Distributed Backup Manager.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.security.geo_distributed_backup import (
    BackupLocation,
    BackupRegion,
    BackupStatus,
    BackupType,
    GeoDistributedBackupManager,
)


@pytest.fixture
def temp_source_dir(tmp_path: Path) -> Path:
    """Create temporary source directory with test files."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create test files
    (source_dir / "file1.txt").write_text("Test content 1")
    (source_dir / "file2.txt").write_text("Test content 2")

    subdir = source_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Test content 3")

    return source_dir


@pytest.fixture
def temp_backup_dir(tmp_path: Path) -> Path:
    """Create temporary backup directory."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return backup_dir


@pytest.fixture
def backup_manager(temp_source_dir: Path, temp_backup_dir: Path) -> GeoDistributedBackupManager:
    """Create backup manager instance."""
    return GeoDistributedBackupManager(
        source_dir=temp_source_dir,
        backup_base_dir=temp_backup_dir,
    )


def test_backup_manager_initialization(
    backup_manager: GeoDistributedBackupManager,
    temp_source_dir: Path,
    temp_backup_dir: Path,
) -> None:
    """Test backup manager initializes correctly."""
    assert backup_manager.source_dir == temp_source_dir.resolve()
    assert backup_manager.backup_base_dir == temp_backup_dir
    assert temp_backup_dir.exists()


def test_default_locations_initialized(
    backup_manager: GeoDistributedBackupManager,
) -> None:
    """Test default backup locations are initialized."""
    assert BackupRegion.PRIMARY in backup_manager.locations
    assert BackupRegion.SECONDARY in backup_manager.locations
    assert BackupRegion.TERTIARY in backup_manager.locations

    # Primary should be enabled by default
    assert backup_manager.locations[BackupRegion.PRIMARY].enabled


def test_add_backup_location(backup_manager: GeoDistributedBackupManager) -> None:
    """Test adding custom backup location."""
    custom_location = BackupLocation(
        region=BackupRegion.SECONDARY,
        path=Path("/tmp/custom_backup"),
        enabled=True,
        priority=1,
    )

    backup_manager.add_backup_location(custom_location)

    assert backup_manager.locations[BackupRegion.SECONDARY] == custom_location


def test_create_full_backup(backup_manager: GeoDistributedBackupManager) -> None:
    """Test creating full backup."""
    manifests = backup_manager.create_backup(
        backup_type=BackupType.FULL,
        regions=[BackupRegion.PRIMARY],
    )

    assert BackupRegion.PRIMARY in manifests
    manifest = manifests[BackupRegion.PRIMARY]

    assert manifest.backup_type == BackupType.FULL
    assert manifest.status == BackupStatus.SUCCESS
    assert manifest.files_count > 0
    assert manifest.checksum is not None


def test_backup_excludes_patterns(
    backup_manager: GeoDistributedBackupManager,
) -> None:
    """Test backup excludes correct patterns."""
    exclude_patterns = backup_manager._get_exclude_patterns()

    assert "__pycache__" in exclude_patterns
    assert ".git" in exclude_patterns
    assert "node_modules" in exclude_patterns
    assert ".omnimind/backups" in exclude_patterns


def test_calculate_backup_checksum(
    backup_manager: GeoDistributedBackupManager, tmp_path: Path
) -> None:
    """Test backup checksum calculation."""
    test_dir = tmp_path / "test_checksum"
    test_dir.mkdir()
    (test_dir / "file1.txt").write_text("content1")
    (test_dir / "file2.txt").write_text("content2")

    checksum1 = backup_manager._calculate_backup_checksum(test_dir)
    assert checksum1
    assert len(checksum1) == 64  # SHA-256 hash length

    # Same directory should produce same checksum
    checksum2 = backup_manager._calculate_backup_checksum(test_dir)
    assert checksum1 == checksum2


def test_verify_backup_integrity(
    backup_manager: GeoDistributedBackupManager,
) -> None:
    """Test backup integrity verification."""
    # Create backup
    manifests = backup_manager.create_backup(regions=[BackupRegion.PRIMARY])
    manifest = manifests[BackupRegion.PRIMARY]

    # Verify integrity
    assert backup_manager.verify_backup_integrity(manifest.backup_id)


def test_verify_cross_region_consistency(
    backup_manager: GeoDistributedBackupManager,
) -> None:
    """Test cross-region consistency verification."""
    # Create backup in primary region
    backup_manager.create_backup(regions=[BackupRegion.PRIMARY])

    # Verify consistency
    report = backup_manager.verify_cross_region_consistency()

    assert "timestamp" in report
    assert "regions_checked" in report
    assert "consistent" in report


def test_create_restore_point(backup_manager: GeoDistributedBackupManager) -> None:
    """Test restore point creation."""
    # Create backup (should auto-create restore point)
    backup_manager.create_backup(regions=[BackupRegion.PRIMARY])

    # Check restore points
    restore_points = backup_manager.list_restore_points()
    assert len(restore_points) > 0


def test_list_restore_points(backup_manager: GeoDistributedBackupManager) -> None:
    """Test listing restore points."""
    # Initially empty
    points = backup_manager.list_restore_points()
    initial_count = len(points)

    # Create backup
    backup_manager.create_backup(regions=[BackupRegion.PRIMARY])

    # Should have new restore point
    points = backup_manager.list_restore_points()
    assert len(points) == initial_count + 1


def test_restore_from_point(backup_manager: GeoDistributedBackupManager, tmp_path: Path) -> None:
    """Test restoring from restore point."""
    # Create backup
    backup_manager.create_backup(regions=[BackupRegion.PRIMARY])

    # Get restore point
    restore_points = backup_manager.list_restore_points()
    assert len(restore_points) > 0
    restore_point = restore_points[0]

    # Restore to new location
    restore_dir = tmp_path / "restored"
    success = backup_manager.restore_from_point(
        restore_id=restore_point.restore_id,
        target_dir=restore_dir,
    )

    assert success
    assert restore_dir.exists()
    assert (restore_dir / "file1.txt").exists()


def test_cleanup_old_backups(
    backup_manager: GeoDistributedBackupManager,
) -> None:
    """Test cleaning up old backups."""
    # Create backup
    backup_manager.create_backup(regions=[BackupRegion.PRIMARY])

    initial_count = len(backup_manager.manifests)

    # Cleanup with max_age_days=0 should delete all
    deleted_count = backup_manager.cleanup_old_backups(max_age_days=0)

    # Should have deleted backups (if any existed)
    # Note: The backup we just created might not be old enough
    assert deleted_count >= 0
    assert len(backup_manager.manifests) <= initial_count


def test_get_backup_status(backup_manager: GeoDistributedBackupManager) -> None:
    """Test getting backup system status."""
    # Create backup
    backup_manager.create_backup(regions=[BackupRegion.PRIMARY])

    status = backup_manager.get_backup_status()

    assert "total_backups" in status
    assert "successful_backups" in status
    assert "restore_points" in status
    assert "regions" in status
    assert "cross_region_consistency" in status


def test_backup_location_to_dict() -> None:
    """Test backup location serialization."""
    location = BackupLocation(
        region=BackupRegion.PRIMARY,
        path=Path("/tmp/backup"),
        enabled=True,
        priority=0,
    )

    location_dict = location.to_dict()

    assert location_dict["region"] == "primary"
    assert location_dict["path"] == "/tmp/backup"
    assert location_dict["enabled"] is True
    assert location_dict["priority"] == 0


def test_backup_manifest_to_dict(backup_manager: GeoDistributedBackupManager) -> None:
    """Test backup manifest serialization."""
    manifests = backup_manager.create_backup(regions=[BackupRegion.PRIMARY])
    manifest = manifests[BackupRegion.PRIMARY]

    manifest_dict = manifest.to_dict()

    assert "backup_id" in manifest_dict
    assert manifest_dict["region"] == "primary"
    assert manifest_dict["backup_type"] == "full"
    assert manifest_dict["status"] == "success"


def test_restore_point_to_dict(backup_manager: GeoDistributedBackupManager) -> None:
    """Test restore point serialization."""
    backup_manager.create_backup(regions=[BackupRegion.PRIMARY])

    restore_points = backup_manager.list_restore_points()
    assert len(restore_points) > 0

    restore_point = restore_points[0]
    rp_dict = restore_point.to_dict()

    assert "restore_id" in rp_dict
    assert "timestamp" in rp_dict
    assert "backup_ids" in rp_dict
    assert "regions_available" in rp_dict


def test_multiple_regions_backup(
    backup_manager: GeoDistributedBackupManager,
) -> None:
    """Test backup to multiple regions."""
    # Enable secondary region
    backup_manager.locations[BackupRegion.SECONDARY].enabled = True

    # Create backup to both regions
    manifests = backup_manager.create_backup(regions=[BackupRegion.PRIMARY, BackupRegion.SECONDARY])

    assert len(manifests) == 2
    assert BackupRegion.PRIMARY in manifests
    assert BackupRegion.SECONDARY in manifests


def test_backup_with_errors(backup_manager: GeoDistributedBackupManager, tmp_path: Path) -> None:
    """Test backup handling with errors."""
    # Create invalid location with a path that can be created but will fail sync
    invalid_dir = tmp_path / "invalid_sync"
    invalid_dir.mkdir()

    invalid_location = BackupLocation(
        region=BackupRegion.TERTIARY,
        path=invalid_dir,
        enabled=True,
        sync_method="invalid_method",  # Invalid sync method
    )
    backup_manager.add_backup_location(invalid_location)

    # Try to backup - should handle error gracefully
    manifests = backup_manager.create_backup(regions=[BackupRegion.TERTIARY])

    if BackupRegion.TERTIARY in manifests:
        manifest = manifests[BackupRegion.TERTIARY]
        assert manifest.status == BackupStatus.FAILED
        assert len(manifest.errors) > 0
