from datetime import datetime

from backupmanager.domain import VM, Disk, Snapshot


def test_vm_backup_default_disabled():
    vm1 = VM('name', [])
    assert not vm1.backup_enabled


def test_disk_last_snapshot_empty():
    disk = Disk('test-disk', [])
    assert disk.last_snapshot is None


def test_disk_last_snapshot_non_empty():
    disk = Disk('test-disk', [
        Snapshot('snapshot-1', datetime(2022, 1, 1)),
        Snapshot('snapshot-2', datetime(2022, 1, 2))
    ])

    assert disk.last_snapshot == Snapshot('snapshot-2', datetime(2022, 1, 2))
