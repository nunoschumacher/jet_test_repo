# import datetime
# import time
# from collections import defaultdict
# import logging
# import itertools as it
#
# from google.cloud.compute_v1 import InstancesClient, SnapshotsClient, DisksClient, Snapshot, ZoneOperationsClient
# from rich.console import Console
# from rich.table import Table
#
# logger = logging.getLogger(__name__)
#
#
# def fetch_vms(project, zone):
#     c = InstancesClient()
#     instances = c.list(project=project, zone=zone)
#
#     return [(i.name, i.labels.get("backup", "false") == "true", i.name) for i in instances]
#
#
# def fetch_snapshots(project):
#     c = SnapshotsClient()
#     snapshots = c.list(project=project)
#
#     return snapshots
#
#
# def last_backups_for_disks(snapshots):
#     results = defaultdict(lambda: datetime.datetime.min.replace(tzinfo=datetime.timezone.utc))
#
#     for snapshot in snapshots:
#         snapshot_time = datetime.datetime.fromisoformat(snapshot.creation_timestamp)
#         snapshot_disk_name = snapshot.source_disk.split("/")[-1]
#
#         if results[snapshot_disk_name] < snapshot_time:
#             results[snapshot_disk_name] = snapshot_time
#
#     return results
#
#
# def create_snapshot_async(project, zone, disk):
#     disk_client = DisksClient()
#     operation = disk_client.create_snapshot(
#         project=project, zone=zone, disk=disk, snapshot_resource=Snapshot(name=f"disk-auto-backup")
#     )
#     return operation
#
#
# def delete_snapshot(project, snapshot):
#     c = SnapshotsClient()
#     c.delete(project=project, snapshot=snapshot)
#
#
def wait_for_async_operations(project, zone, operations):
    operations = operations.copy()
    operation_client = ZoneOperationsClient()

    while True:
        for operation in operations:
            operation_data = operation_client.get(project=project, zone=zone, operation=operation.name)
            logger.info("Snapshot for disk %s is %s", operation.target_link.split("/")[-1], operation_data.status)
            if operation_data.status.value == 2104194:
                operations.remove(operation)

        if len(operations) == 0:
            logger.info("All snapshots done")
            break
        time.sleep(5)
#
#
# def backup(project, zone, interval=datetime.timedelta(hours=0)):
#     logger.info("Starting backup process")
#     vms = fetch_vms(project, zone)
#     snapshots = fetch_snapshots(project)
#     last_backups = last_backups_for_disks(snapshots)
#
#     logger.info("Found %s instances", len(vms))
#
#     snapshot_operations = []
#     for vm_name, backup_enabled, device_name in vms:
#         logger.info("Instance: %s", vm_name)
#         logger.info("Backup Enabled: %s", backup_enabled)
#         if not backup_enabled:
#             continue
#
#         time_since_last_backup = (
#             datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - last_backups[device_name]
#         )
#         logger.info("Last backup was %s ago", time_since_last_backup)
#         if time_since_last_backup < interval:
#             logger.info("Skipping backup creation since the last backup is too recent")
#             continue
#
#         logger.info("Starting asynchronous backup creation")
#         snapshot_operations.append(create_snapshot_async(project, zone, device_name.split("/")[-1]))
#
#     wait_for_async_operations(project, zone, snapshot_operations)
#
#
# def retention(project):
#     logger.info("Checking backups against retention policy")
#     snapshots = fetch_snapshots(project)
#
#     snapshots_by_disk = {k: list(v) for k, v in it.groupby(snapshots, lambda s: s.source_disk_id)}
#
#     now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
#     for disk, snapshots in snapshots_by_disk.items():
#         logger.info("Checking backups for disk %s", disk)
#         days_since_backup = [
#             (now - datetime.datetime.fromisoformat(snapshot.creation_timestamp)).days
#             for snapshot in snapshots
#         ]
#         backup_groups = [
#             -day if day < 7 else day // 7 for
#             day in days_since_backup
#         ]
#         # Attach the backup groups to the snapshots and sort by group
#         snapshots_with_groups = sorted(zip(snapshots, backup_groups), key=lambda v: v[1])
#
#         # group by backup group so we can know which ones to delete
#         for backup_group, group_snapshots in it.groupby(snapshots_with_groups, lambda v: v[1]):
#             group_snapshots = [s for s, _ in group_snapshots]
#             logger.info("Backup group %s contains snapshots %s", backup_group, [s.id for s in group_snapshots])
#             old_snapshots = list(sorted(group_snapshots, reverse=True, key=lambda v: datetime.datetime.fromisoformat(v.creation_timestamp)))[1:]
#
#             for old_snapshot in old_snapshots:
#                 logger.info("Deleting snapshot %s", old_snapshot.id)
#                 delete_snapshot(project, old_snapshot.name)
#
#
# def print_backup_status(instances, last_backups):
#     console = Console()
#     table = Table(show_header=True, header_style="bold magenta", width=110)
#     table.add_column('Instance', width=15)
#     table.add_column('Backup Enabled', width=12)
#     table.add_column('Disk', width=15)
#     table.add_column('Last Backup', width=30)
#
#     for name, backup_enabled, disk_name in instances:
#         last_backup = str(last_backups.get(disk_name, 'Never'))
#         table.add_row(name, str(backup_enabled), disk_name, last_backup)
#
#     console.print(table)
#
#
# if __name__ == "__main__":
#     fetch_vms()
