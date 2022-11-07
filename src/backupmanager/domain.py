import datetime
from typing import List, Optional
from dataclasses import dataclass

# class VM:
#     def __init__(self, name: str, disks: List['Disk'], backup_enabled: bool = False):
#         self.name = name
#         self.disks = disks
#         self.backup_enabled = backup_enabled
#
#     def __str__(self):
#         return f"VM({self.name}, {str(self.disks)}, {self.backup_enabled})"
#
#     def __eq__(self, other):
#         if not isinstance(other, VM):
#             return NotImplemented
#
#         return self.name == other.name and self.disks == other.disks and self.backup_enabled == other.backup_enabled


@dataclass
class VM:
    name: str
    disks: List['Disk']
    backup_enabled: bool = False


@dataclass
class Disk:
    name: str
    snapshots: List['Snapshot']

    @property
    def last_snapshot(self) -> Optional['Snapshot']:
        if len(self.snapshots) == 0:
            return None

        return max(self.snapshots, key=lambda s: s.created_date)


@dataclass
class Snapshot:
    name: str
    created_date: datetime.datetime

    @property
    def time_since(self) -> datetime.timedelta:
        return datetime.datetime.now() - self.created_date


@dataclass
class AsyncSnapshotOperation:
    id: str
    status: str
    disk_name: str


if __name__ == "__main__":
    vm1 = VM(name='backup-vm', disks=[], backup_enabled=True)
    vm2 = VM(name='backup-vm', disks=[], backup_enabled=True)

    print(str(vm1))
    assert vm1 == vm2
    assert vm1 is not vm2
