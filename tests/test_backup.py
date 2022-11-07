import pytest

from backupmanager.backup import BackupManager
from unittest.mock import Mock

from backupmanager.domain import Disk, VM, AsyncSnapshotOperation


@pytest.fixture
def mock_backend():
    mock_backend = Mock()

    def wait_for(ops):
        for op in ops:
            yield op
    mock_backend.wait_for = wait_for
    return mock_backend


def test_backup_if_not_enabled(mock_backend):
    # mock-based testing
    mock_backend.fetch_vms.return_value = [
        VM('test', backup_enabled=False, disks=[
            Disk(name='test-disk', snapshots=[])
        ])
    ]

    bm = BackupManager(mock_backend)
    bm.backup()

    mock_backend.fetch_vms.assert_called_with()
    mock_backend.snapshot.assert_not_called()


def test_backup_if_no_existing_snapshots(mock_backend):
    # mock-based testing
    mock_backend.fetch_vms.return_value = [
        VM('test', backup_enabled=True, disks=[
            Disk(name='test-disk', snapshots=[])
        ])
    ]
    bm = BackupManager(mock_backend)
    bm.backup()

    mock_backend.fetch_vms.assert_called_with()
    mock_backend.snapshot.assert_called_with(
        Disk(name='test-disk', snapshots=[])
    )
