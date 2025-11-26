"""
Geo-Distributed Backup System for OmniMind.

This module implements enterprise-grade disaster recovery with:
- Multi-region backup configuration
- Automated failover mechanism
- Data consistency verification across regions
- Backup integrity checks
- Point-in-time recovery capabilities
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BackupRegion(str, Enum):
    """Geographical regions for backups."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class BackupStatus(str, Enum):
    """Backup operation status."""

    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    PARTIAL = "partial"


class BackupType(str, Enum):
    """Type of backup."""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


@dataclass
class BackupLocation:
    """Configuration for a backup location."""

    region: BackupRegion
    path: Path
    enabled: bool = True
    priority: int = 0  # Lower is higher priority
    sync_method: str = "rsync"  # rsync, rclone, s3sync
    remote_url: Optional[str] = None
    credentials_file: Optional[Path] = None
    encryption_key: Optional[str] = None
    max_age_days: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["region"] = self.region.value
        data["path"] = str(self.path)
        data["credentials_file"] = (
            str(self.credentials_file) if self.credentials_file else None
        )
        return data


@dataclass
class BackupManifest:
    """Manifest of a backup operation."""

    backup_id: str
    region: BackupRegion
    backup_type: BackupType
    status: BackupStatus
    started_at: str
    completed_at: Optional[str] = None
    files_count: int = 0
    total_size_bytes: int = 0
    checksum: Optional[str] = None
    files: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["region"] = self.region.value
        data["backup_type"] = self.backup_type.value
        data["status"] = self.status.value
        return data


@dataclass
class RestorePoint:
    """Point-in-time restore point."""

    restore_id: str
    timestamp: str
    backup_ids: List[str]  # Chain of backups needed for restore
    description: str
    regions_available: List[BackupRegion]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["regions_available"] = [r.value for r in self.regions_available]
        return data


class GeoDistributedBackupManager:
    """Manages geo-distributed backups with multi-region redundancy."""

    def __init__(
        self,
        source_dir: Path = Path("."),
        backup_base_dir: Path = Path(".omnimind/backups"),
    ):
        """
        Initialize geo-distributed backup manager.

        Args:
            source_dir: Source directory to backup
            backup_base_dir: Base directory for local backups
        """
        self.source_dir = source_dir.resolve()
        self.backup_base_dir = backup_base_dir
        self.backup_base_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

        self.locations: Dict[BackupRegion, BackupLocation] = {}
        self.manifests: Dict[str, BackupManifest] = {}
        self.restore_points: Dict[str, RestorePoint] = {}

        self._initialize_default_locations()
        self._load_manifests()

        logger.info(
            f"Geo-Distributed Backup Manager initialized: {self.backup_base_dir}"
        )

    def _initialize_default_locations(self) -> None:
        """Initialize default backup locations."""
        # Primary location (local)
        primary = BackupLocation(
            region=BackupRegion.PRIMARY,
            path=self.backup_base_dir / "primary",
            priority=0,
            sync_method="local",
        )
        self.locations[BackupRegion.PRIMARY] = primary

        # Secondary location (could be network drive)
        secondary = BackupLocation(
            region=BackupRegion.SECONDARY,
            path=self.backup_base_dir / "secondary",
            priority=1,
            sync_method="rsync",
            enabled=False,  # Disabled by default, enable when configured
        )
        self.locations[BackupRegion.SECONDARY] = secondary

        # Tertiary location (could be cloud storage)
        tertiary = BackupLocation(
            region=BackupRegion.TERTIARY,
            path=self.backup_base_dir / "tertiary",
            priority=2,
            sync_method="rclone",
            enabled=False,  # Disabled by default
        )
        self.locations[BackupRegion.TERTIARY] = tertiary

    def add_backup_location(self, location: BackupLocation) -> None:
        """
        Add or update a backup location.

        Args:
            location: Backup location configuration
        """
        self.locations[location.region] = location
        location.path.mkdir(parents=True, exist_ok=True, mode=0o700)
        logger.info(
            f"Backup location added: {location.region.value} -> {location.path}"
        )

    def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        regions: Optional[List[BackupRegion]] = None,
    ) -> Dict[BackupRegion, BackupManifest]:
        """
        Create backups in specified regions.

        Args:
            backup_type: Type of backup to create
            regions: Regions to backup to (default: all enabled)

        Returns:
            Dictionary of backup manifests by region
        """
        if regions is None:
            regions = [r for r, loc in self.locations.items() if loc.enabled]

        backup_id_base = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        manifests = {}

        for region in regions:
            if region not in self.locations:
                logger.warning(f"Region not configured: {region.value}")
                continue

            location = self.locations[region]
            if not location.enabled:
                logger.info(f"Skipping disabled region: {region.value}")
                continue

            backup_id = f"{backup_id_base}_{region.value}"
            manifest = self._perform_backup(backup_id, region, backup_type, location)
            manifests[region] = manifest
            self.manifests[backup_id] = manifest

        # Save manifests
        self._save_manifests()

        # Create restore point
        if manifests:
            self._create_restore_point(list(manifests.values()))

        return manifests

    def _perform_backup(
        self,
        backup_id: str,
        region: BackupRegion,
        backup_type: BackupType,
        location: BackupLocation,
    ) -> BackupManifest:
        """
        Perform backup to a specific location.

        Args:
            backup_id: Unique backup identifier
            region: Target region
            backup_type: Type of backup
            location: Backup location configuration

        Returns:
            Backup manifest
        """
        started_at = datetime.now(timezone.utc).isoformat()
        manifest = BackupManifest(
            backup_id=backup_id,
            region=region,
            backup_type=backup_type,
            status=BackupStatus.IN_PROGRESS,
            started_at=started_at,
        )

        try:
            # Create backup directory
            backup_dir = location.path / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Perform backup based on type
            if location.sync_method == "local":
                self._local_backup(backup_dir, manifest)
            elif location.sync_method == "rsync":
                self._rsync_backup(backup_dir, location, manifest)
            elif location.sync_method == "rclone":
                self._rclone_backup(backup_dir, location, manifest)
            else:
                raise ValueError(f"Unknown sync method: {location.sync_method}")

            # Calculate checksum
            manifest.checksum = self._calculate_backup_checksum(backup_dir)

            # Mark as successful
            manifest.status = BackupStatus.SUCCESS
            manifest.completed_at = datetime.now(timezone.utc).isoformat()

            logger.info(f"Backup completed: {backup_id} to {region.value}")

        except Exception as e:
            logger.error(f"Backup failed for {backup_id}: {e}")
            manifest.status = BackupStatus.FAILED
            manifest.errors.append(str(e))
            manifest.completed_at = datetime.now(timezone.utc).isoformat()

        return manifest

    def _local_backup(self, backup_dir: Path, manifest: BackupManifest) -> None:
        """
        Perform local backup using shutil.

        Args:
            backup_dir: Target backup directory
            manifest: Backup manifest to update
        """
        exclude_patterns = self._get_exclude_patterns()

        for item in self.source_dir.rglob("*"):
            if item.is_file():
                # Check if excluded
                relative_path = item.relative_to(self.source_dir)
                if self._is_excluded(relative_path, exclude_patterns):
                    continue

                # Copy file
                target = backup_dir / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)

                # Update manifest
                manifest.files.append(
                    {
                        "path": str(relative_path),
                        "size": item.stat().st_size,
                        "mtime": item.stat().st_mtime,
                    }
                )
                manifest.files_count += 1
                manifest.total_size_bytes += item.stat().st_size

    def _rsync_backup(
        self, backup_dir: Path, location: BackupLocation, manifest: BackupManifest
    ) -> None:
        """
        Perform backup using rsync.

        Args:
            backup_dir: Target backup directory
            location: Backup location configuration
            manifest: Backup manifest to update
        """
        exclude_file = self._create_exclude_file()

        # Build rsync command
        cmd = [
            "rsync",
            "-av",
            "--delete",
            f"--exclude-from={exclude_file}",
            str(self.source_dir) + "/",
            str(backup_dir) + "/",
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.debug(f"rsync output: {result.stdout}")

            # Parse rsync output to update manifest
            self._parse_rsync_output(result.stdout, manifest)

        except subprocess.CalledProcessError as e:
            logger.error(f"rsync failed: {e.stderr}")
            raise RuntimeError(f"rsync backup failed: {e}")

    def _rclone_backup(
        self, backup_dir: Path, location: BackupLocation, manifest: BackupManifest
    ) -> None:
        """
        Perform backup using rclone (for cloud storage).

        Args:
            backup_dir: Target backup directory
            location: Backup location configuration
            manifest: Backup manifest to update
        """
        if not location.remote_url:
            raise ValueError("Remote URL required for rclone backup")

        exclude_file = self._create_exclude_file()

        # Build rclone command
        cmd = [
            "rclone",
            "sync",
            str(self.source_dir),
            location.remote_url,
            f"--exclude-from={exclude_file}",
            "--progress",
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.debug(f"rclone output: {result.stdout}")

            # Note: For rclone, we might need to list files separately
            manifest.status = BackupStatus.SUCCESS

        except subprocess.CalledProcessError as e:
            logger.error(f"rclone failed: {e.stderr}")
            raise RuntimeError(f"rclone backup failed: {e}")

    def _get_exclude_patterns(self) -> List[str]:
        """Get list of exclude patterns for backup."""
        return [
            "__pycache__",
            "*.pyc",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "*.log",
            ".omnimind/backups",  # Don't backup backups
            "tmp",
            ".DS_Store",
        ]

    def _is_excluded(self, path: Path, patterns: List[str]) -> bool:
        """
        Check if path matches any exclude pattern.

        Args:
            path: Path to check
            patterns: List of exclude patterns

        Returns:
            True if path should be excluded
        """
        path_str = str(path)
        for pattern in patterns:
            if pattern in path_str or path_str.endswith(pattern):
                return True
        return False

    def _create_exclude_file(self) -> Path:
        """
        Create temporary exclude file for rsync/rclone.

        Returns:
            Path to exclude file
        """
        exclude_file = self.backup_base_dir / "exclude.txt"
        with exclude_file.open("w") as f:
            f.write("\n".join(self._get_exclude_patterns()))
        return exclude_file

    def _parse_rsync_output(self, output: str, manifest: BackupManifest) -> None:
        """
        Parse rsync output to update manifest.

        Args:
            output: rsync stdout
            manifest: Manifest to update
        """
        # Simple parsing - count transferred files
        lines = output.strip().split("\n")
        for line in lines:
            if line and not line.startswith("sending") and not line.startswith("sent"):
                manifest.files_count += 1

    def _calculate_backup_checksum(self, backup_dir: Path) -> str:
        """
        Calculate checksum of backup directory.

        Args:
            backup_dir: Directory to checksum

        Returns:
            SHA-256 checksum
        """
        hash_obj = hashlib.sha256()

        # Sort files for consistent hashing
        files = sorted(backup_dir.rglob("*"))

        for file_path in files:
            if file_path.is_file():
                with file_path.open("rb") as f:
                    hash_obj.update(f.read())

        return hash_obj.hexdigest()

    def verify_backup_integrity(self, backup_id: str) -> bool:
        """
        Verify integrity of a backup.

        Args:
            backup_id: Backup identifier

        Returns:
            True if backup is intact, False otherwise
        """
        if backup_id not in self.manifests:
            logger.error(f"Backup not found: {backup_id}")
            return False

        manifest = self.manifests[backup_id]
        location = self.locations[manifest.region]
        backup_dir = location.path / backup_id

        if not backup_dir.exists():
            logger.error(f"Backup directory not found: {backup_dir}")
            return False

        # Recalculate checksum
        current_checksum = self._calculate_backup_checksum(backup_dir)

        if current_checksum != manifest.checksum:
            logger.error(
                f"Checksum mismatch for {backup_id}: "
                f"expected {manifest.checksum}, got {current_checksum}"
            )
            return False

        logger.info(f"Backup integrity verified: {backup_id}")
        return True

    def verify_cross_region_consistency(self) -> Dict[str, Any]:
        """
        Verify data consistency across all regions.

        Returns:
            Consistency report
        """
        report: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "regions_checked": [],
            "consistent": True,
            "discrepancies": [],
        }

        # Get latest backup from each region
        latest_backups = {}
        for region, location in self.locations.items():
            if not location.enabled:
                continue

            region_backups = [m for m in self.manifests.values() if m.region == region]
            if region_backups:
                latest = max(region_backups, key=lambda x: x.started_at)
                latest_backups[region] = latest
                report["regions_checked"].append(region.value)

        # Compare checksums
        if len(latest_backups) < 2:
            report["consistent"] = True
            report["note"] = "Less than 2 regions to compare"
            return report

        checksums = {r: m.checksum for r, m in latest_backups.items()}
        unique_checksums = set(checksums.values())

        if len(unique_checksums) > 1:
            report["consistent"] = False
            report["discrepancies"] = [
                f"{r.value}: {cs}" for r, cs in checksums.items()
            ]

        return report

    def _create_restore_point(self, manifests: List[BackupManifest]) -> None:
        """
        Create a restore point from successful backups.

        Args:
            manifests: List of backup manifests
        """
        successful = [m for m in manifests if m.status == BackupStatus.SUCCESS]
        if not successful:
            return

        restore_id = f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        restore_point = RestorePoint(
            restore_id=restore_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            backup_ids=[m.backup_id for m in successful],
            description=f"Restore point from {len(successful)} region(s)",
            regions_available=[m.region for m in successful],
        )

        self.restore_points[restore_id] = restore_point
        self._save_restore_points()

        logger.info(f"Restore point created: {restore_id}")

    def list_restore_points(self) -> List[RestorePoint]:
        """
        List all available restore points.

        Returns:
            List of restore points
        """
        return list(self.restore_points.values())

    def restore_from_point(
        self,
        restore_id: str,
        target_dir: Path,
        preferred_region: Optional[BackupRegion] = None,
    ) -> bool:
        """
        Restore from a specific restore point.

        Args:
            restore_id: Restore point identifier
            target_dir: Directory to restore to
            preferred_region: Preferred region to restore from

        Returns:
            True if restore successful, False otherwise
        """
        if restore_id not in self.restore_points:
            logger.error(f"Restore point not found: {restore_id}")
            return False

        restore_point = self.restore_points[restore_id]

        # Choose region (prefer specified, then by priority)
        if preferred_region and preferred_region in restore_point.regions_available:
            region = preferred_region
        else:
            # Sort by priority
            available = [
                (self.locations[r].priority, r) for r in restore_point.regions_available
            ]
            available.sort()
            if not available:
                logger.error(f"No region available for restore: {restore_id}")
                return False
            region = available[0][1]

        # Now region is guaranteed to be BackupRegion

        # Find backup manifest for this region
        backup_id = None
        for bid in restore_point.backup_ids:
            if bid in self.manifests and self.manifests[bid].region == region:
                backup_id = bid
                break

        if not backup_id:
            logger.error(f"Backup not found for region {region.value}")
            return False

        # Perform restore
        location = self.locations[region]
        backup_dir = location.path / backup_id

        logger.info(f"Restoring from {backup_id} ({region.value}) to {target_dir}")

        try:
            target_dir.mkdir(parents=True, exist_ok=True)

            # Copy all files
            if backup_dir.exists():
                shutil.copytree(backup_dir, target_dir, dirs_exist_ok=True)
                logger.info(f"Restore completed: {restore_id}")
                return True
            else:
                logger.error(f"Backup directory not found: {backup_dir}")
                return False

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def cleanup_old_backups(self, max_age_days: Optional[int] = None) -> int:
        """
        Clean up old backups beyond retention period.

        Args:
            max_age_days: Maximum age in days (default: from location config)

        Returns:
            Number of backups deleted
        """
        deleted_count = 0
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=(max_age_days or 30))

        for backup_id, manifest in list(self.manifests.items()):
            backup_date = datetime.fromisoformat(manifest.started_at)

            if backup_date < cutoff_date:
                location = self.locations[manifest.region]
                backup_dir = location.path / backup_id

                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
                    logger.info(f"Deleted old backup: {backup_id}")
                    deleted_count += 1

                # Remove from manifests
                del self.manifests[backup_id]

        # Update manifests file
        self._save_manifests()

        logger.info(f"Cleaned up {deleted_count} old backup(s)")
        return deleted_count

    def _load_manifests(self) -> None:
        """Load backup manifests from file."""
        manifests_file = self.backup_base_dir / "manifests.json"
        if manifests_file.exists():
            try:
                with manifests_file.open("r") as f:
                    data = json.load(f)
                    for item in data:
                        manifest = BackupManifest(**item)
                        # Convert string enums back to Enum
                        manifest.region = BackupRegion(item["region"])
                        manifest.backup_type = BackupType(item["backup_type"])
                        manifest.status = BackupStatus(item["status"])
                        self.manifests[manifest.backup_id] = manifest
                logger.info(f"Loaded {len(self.manifests)} backup manifest(s)")
            except Exception as e:
                logger.error(f"Failed to load manifests: {e}")

    def _save_manifests(self) -> None:
        """Save backup manifests to file."""
        manifests_file = self.backup_base_dir / "manifests.json"
        try:
            with manifests_file.open("w") as f:
                json.dump([m.to_dict() for m in self.manifests.values()], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save manifests: {e}")

    def _save_restore_points(self) -> None:
        """Save restore points to file."""
        restore_file = self.backup_base_dir / "restore_points.json"
        try:
            with restore_file.open("w") as f:
                json.dump(
                    [rp.to_dict() for rp in self.restore_points.values()], f, indent=2
                )
        except Exception as e:
            logger.error(f"Failed to save restore points: {e}")

    def get_backup_status(self) -> Dict[str, Any]:
        """
        Get overall backup system status.

        Returns:
            Status report with backup statistics
        """
        total_backups = len(self.manifests)
        successful_backups = sum(
            1 for m in self.manifests.values() if m.status == BackupStatus.SUCCESS
        )

        regions_status = {}
        for region, location in self.locations.items():
            region_backups = [m for m in self.manifests.values() if m.region == region]
            regions_status[region.value] = {
                "enabled": location.enabled,
                "backup_count": len(region_backups),
                "latest_backup": (
                    max(region_backups, key=lambda x: x.started_at).backup_id
                    if region_backups
                    else None
                ),
            }

        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": total_backups - successful_backups,
            "restore_points": len(self.restore_points),
            "regions": regions_status,
            "cross_region_consistency": self.verify_cross_region_consistency(),
        }
