"""Record exact record-level additions/removals/field changes between latest two captures."""
from common import ARCHIVE, read_json, rows_and_meta, write_json
from normalize import occurrence_key


def snapshot_rows(path):
    index = read_json(path)
    rows = {}
    for page in index["pages"]:
        if page["http_status"] == 200:
            batch, _, _ = rows_and_meta(read_json(ARCHIVE / page["path"]))
            rows.update({occurrence_key(row): row for row in batch})
    return rows


def main():
    snapshots = sorted((ARCHIVE / "raw/snapshots").glob("*/extraction.json"))
    if len(snapshots) < 2:
        print("No earlier snapshot to compare")
        return
    old, new = snapshots[-2:]
    before, after = snapshot_rows(old), snapshot_rows(new)
    changes = [{"key": key, "fields": [field for field in sorted(set(before[key]) | set(after[key])) if before[key].get(field) != after[key].get(field)]} for key in sorted(before.keys() & after.keys()) if before[key] != after[key]]
    result = {"before_snapshot": old.parent.name, "after_snapshot": new.parent.name, "before_rows": len(before), "after_rows": len(after), "added_occurrences": sorted(after.keys() - before.keys()), "no_longer_returned_occurrences": sorted(before.keys() - after.keys()), "changed_rows": changes, "preservation_policy": "All earlier raw snapshots and observations retained even if no longer publicly returned"}
    write_json(ARCHIVE / "reports/snapshot-changes.json", result)
    print(result)


if __name__ == "__main__":
    main()
