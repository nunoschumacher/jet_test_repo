from datetime import timedelta
from typing import List, Protocol
import structlog

from backupmanager.backends import BackupBackend, FakeBackupBackend, GCPBackend
from backupmanager.domain import VM, AsyncSnapshotOperation
from rich.console import Console
from rich.table import Table

logger = structlog.getLogger(__name__)


class BackupManager:
    def __init__(self, backend: BackupBackend):
        self.backend = backend  # Dependency Injection
        self.backup_interval = timedelta(hours=24)

    def print_status(self):
        vms: List[VM] = self.backend.fetch_vms()

        console = Console()
        table = Table(show_header=True, show_lines=True, width=100)
        table.add_column("Instance", width=20)
        table.add_column("Backup enabled", width=20)
        table.add_column("Disks", width=20)
        table.add_column("Last Backup", width=30)

        for vm in vms:
            table.add_row(
                vm.name,
                str(vm.backup_enabled),
                '\n'.join([d.name for d in vm.disks]),
                '\n'.join([
                    d.last_snapshot.created_date.isoformat()
                    if d.last_snapshot is not None
                    else "Never"
                    for d in vm.disks
                ])
            )
        console.print(table)

    def backup(self):
        vms = self.backend.fetch_vms()
        operations: List[AsyncSnapshotOperation] = []
        for vm in vms:
            log = logger.bind(vm=vm.name)
            if not vm.backup_enabled:
                log.info("backup_disabled")
                continue

            log.info("backup_enabled")
            for disk in vm.disks:
                log = log.bind(disk=disk.name)

                if disk.last_snapshot is None or disk.last_snapshot.time_since > self.backup_interval:
                    log.info("starting_backup")
                    operations.append(self.backend.snapshot(disk))
                else:
                    log.info("backup_too_recent")

        for done_operation in self.backend.wait_for(operations):
            logger.info(
                "backup_done",
                disk=done_operation.disk_name,
                status=done_operation.status
            )

    def retention_policy(self):
        ...


if __name__ == "__main__":
    # bm = BackupManager(GCPBackend(project='backups-mahsa', zone='europe-west4-a'))
    bm = BackupManager(FakeBackupBackend())
    bm.print_status()

    # bm.backup()
