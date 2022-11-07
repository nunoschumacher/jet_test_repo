import time
from datetime import datetime
from typing import Protocol, List, Generator
from backupmanager.domain import VM, Disk, AsyncSnapshotOperation, Snapshot
from google.cloud.compute_v1 import InstancesClient, SnapshotsClient, DisksClient, ZoneOperationsClient


class BackupBackend(Protocol):
    def fetch_vms(self) -> List[VM]:
        pass

    def snapshot(self, disk: Disk) -> AsyncSnapshotOperation:
        pass

    def wait_for(self, operations: List["AsyncSnapshotOperation"]) -> Generator[AsyncSnapshotOperation, None, None]:
        pass


class GCPBackend:
    def __init__(self, project, zone):
        self.project = project
        self.zone = zone
        self.instances_client = InstancesClient()
        self.snapshots_client = SnapshotsClient()
        self.disks_client = DisksClient()
        self.zone_operations_client = ZoneOperationsClient()

    def fetch_vms(self) -> List[VM]:
        instances = self.instances_client.list(project=self.project, zone=self.zone)
        snapshots = self.snapshots_client.list(project=self.project)

        return [
            VM(
                name=instance.name,
                backup_enabled=instance.labels.get("backup").lower() == "true",
                disks=[
                    Disk(
                        name=disk.source.split('/')[-1],
                        snapshots=[
                            Snapshot(
                                name=snapshot.name, created_date=datetime.fromisoformat(snapshot.creation_timestamp)
                            )
                            for snapshot in snapshots
                            if snapshot.source_disk == disk.source
                        ],
                    )
                    for disk in instance.disks
                ],
            )
            for instance in instances
        ]


class FakeBackupBackend:
    def fetch_vms(self) -> List[VM]:
        return [
            VM(
                "fake vm",
                [
                    Disk("Disk-1", []),
                    Disk("Disk-2", [Snapshot("snapshot-1", datetime.now()), Snapshot("snapshot-2", datetime.now())]),
                ],
                True,
            )
        ]

    def snapshot(self, disk: Disk) -> AsyncSnapshotOperation:
        return AsyncSnapshotOperation(
            id="",
            status="",
            disk_name=disk.name,
        )

    def wait_for(self, operations: List[AsyncSnapshotOperation]) -> Generator[AsyncSnapshotOperation, None, None]:
        for operation in operations:
            time.sleep(1)
            yield operation
