"""Create additive DBv11; preserve every historical DBv10 table and status."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sqlite3


BASELINE_SHA256 = "ec8004d7b2191ab1e0ee9f1407fedfdd8e320bc89b2e3ad7ff56f7fb23a1188a"
BASELINE_BYTES = 7491584


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_pointer(record, pointer):
    """Resolve RFC 6901 pointers into the hash-bound JSON evidence."""
    if pointer == "":
        return record
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("evidence checks require a JSON pointer")
    value = record
    for part in pointer[1:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def build(baseline, evidence_map, status_file, output, receipt):
    baseline, output, receipt = map(Path, (baseline, output, receipt))
    if output.exists() or receipt.exists() or output.resolve() == receipt.resolve():
        raise ValueError("create-only distinct DB and receipt required")
    if baseline.stat().st_size != BASELINE_BYTES or sha(baseline) != BASELINE_SHA256:
        raise ValueError("DBv10 baseline identity mismatch")
    evidence = json.loads(Path(evidence_map).read_text())
    status = json.loads(Path(status_file).read_text())
    if (status.get("gap_id") != "G02" or status.get("status") != "UNRESOLVED"
            or status.get("production_admission") != "HOLD"
            or status.get("capture") is not False):
        raise ValueError("update must preserve G02 UNRESOLVED, production HOLD, capture false")
    records, bound_json = [], {}
    for item in evidence:
        path = Path(item["path"])
        package_path = PurePosixPath(item["package_path"])
        if package_path.is_absolute() or ".." in package_path.parts:
            raise ValueError("evidence package path is not relative and bounded")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("evidence identity mismatch: " + str(path))
        evidence_id = item["evidence_id"]
        if evidence_id in bound_json:
            raise ValueError("duplicate evidence identity")
        body = data.decode("utf-8")
        bound_json[evidence_id] = json.loads(body)
        records.append((evidence_id, item["kind"], str(package_path),
                        item["sha256"], len(data), body))
    checks = status.get("required_central_checks", [])
    if not isinstance(status.get("closure_label"), str) or not status["closure_label"]:
        raise ValueError("an explicit closure label is required")
    if status.get("central_spatial_status") == "PASSED_LOCAL" and not checks:
        raise ValueError("PASSED_LOCAL central spatial status requires actual evidence checks")
    for check in checks:
        actual = json_pointer(bound_json[check["evidence_id"]], check["json_pointer"])
        expected = check["expected"]
        if not (expected is True or expected == "PASS"):
            raise ValueError("a passing check must expect true or PASS")
        if type(actual) is not type(expected) or actual != expected:
            raise ValueError("required central check did not pass: " + str(check))

    prior = sqlite3.connect("file:" + str(baseline.resolve()) + "?mode=ro", uri=True)
    prior_tables = prior.execute("SELECT name,sql FROM sqlite_master WHERE type='table'").fetchall()
    prior_row_count = sum(prior.execute('SELECT COUNT(*) FROM "' + name.replace('"', '""') + '"').fetchone()[0]
                          for name, _ in prior_tables)
    if len(prior_tables) != 44 or prior_row_count != 3301:
        prior.close()
        raise ValueError("unexpected DBv10 historical table/row counts")
    old_view = prior.execute("SELECT sql FROM sqlite_master WHERE type='view' AND name='current_research_gap_status'").fetchone()[0]
    view_prefix = "CREATE VIEW current_research_gap_status AS"
    if not old_view.startswith(view_prefix):
        prior.close()
        raise ValueError("unexpected baseline effective view definition")
    with output.open("xb") as dst, baseline.open("rb") as src:
        shutil.copyfileobj(src, dst)
    conn = sqlite3.connect(output)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        with conn:
            conn.execute("CREATE TABLE central_quadrature_evidence (evidence_id TEXT PRIMARY KEY, kind TEXT NOT NULL, package_path TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, record_json TEXT NOT NULL)")
            conn.executemany("INSERT INTO central_quadrature_evidence VALUES (?,?,?,?,?,?)", records)
            conn.execute("CREATE TABLE central_quadrature_status (gap_id TEXT PRIMARY KEY REFERENCES research_gap_status(gap_id), status TEXT NOT NULL, closure_label TEXT NOT NULL, record_json TEXT NOT NULL)")
            conn.execute("INSERT INTO central_quadrature_status VALUES (?,?,?,?)", (
                status["gap_id"], status["status"], status["closure_label"],
                json.dumps(status, ensure_ascii=False, sort_keys=True)))
            conn.execute(old_view.replace(view_prefix, "CREATE VIEW current_research_gap_status_v10 AS", 1))
            conn.execute("DROP VIEW current_research_gap_status")
            conn.execute("CREATE VIEW current_research_gap_status AS SELECT old.database_gap_id,old.gap_id,COALESCE(new.status,old.status) AS status,COALESCE(new.closure_label,old.closure_label) AS closure_label,COALESCE(new.record_json,old.record_json) AS record_json,CASE WHEN new.gap_id IS NULL THEN old.status_source ELSE 'R4Y_G02_CENTRAL_QUADRATURE_RESEARCH' END AS status_source FROM current_research_gap_status_v10 old LEFT JOIN central_quadrature_status new USING(gap_id)")
        preserved = []
        for name, schema in prior_tables:
            if conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() != (schema,):
                raise ValueError("historical schema changed: " + name)
            identifier = '"' + name.replace('"', '""') + '"'
            old = list(prior.execute("SELECT * FROM " + identifier))
            if Counter(old) != Counter(conn.execute("SELECT * FROM " + identifier)):
                raise ValueError("historical rows changed: " + name)
            preserved.append({"table": name, "rows": len(old), "schema_equal": True,
                              "row_multiset_equal": True})
        for name, schema in prior.execute("SELECT name,sql FROM sqlite_master WHERE type='view' AND name!='current_research_gap_status'"):
            if conn.execute("SELECT sql FROM sqlite_master WHERE type='view' AND name=?", (name,)).fetchone() != (schema,):
                raise ValueError("historical view changed: " + name)
        historical = prior.execute("SELECT * FROM current_research_gap_status ORDER BY gap_id").fetchall()
        if conn.execute("SELECT * FROM current_research_gap_status_v10 ORDER BY gap_id").fetchall() != historical:
            raise ValueError("v10 effective view was not preserved")
        if conn.execute("SELECT * FROM current_research_gap_status WHERE gap_id!='G02' ORDER BY gap_id").fetchall() != [row for row in historical if row[1] != "G02"]:
            raise ValueError("non-G02 effective status changed")
        if conn.execute("PRAGMA integrity_check").fetchall() != [("ok",)] or conn.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("DB integrity/foreign key failure")
        current = conn.execute("SELECT gap_id,status,closure_label,status_source FROM current_research_gap_status ORDER BY gap_id").fetchall()
    finally:
        prior.close()
        conn.close()
    result = {"schema": "BASS_R4Y_DB11_VALIDATION_V1", "baseline_sha256": sha(baseline),
              "database_sha256": sha(output), "database_bytes": output.stat().st_size,
              "preserved_tables": preserved, "preserved_table_count": len(preserved),
              "preserved_row_count": sum(x["rows"] for x in preserved),
              "new_evidence_rows": len(records), "new_status_rows": 1,
              "central_spatial_status": status.get("central_spatial_status", "UNRESOLVED"),
              "integrity_check": "ok", "foreign_key_violations": 0,
              "previous_effective_view_preserved_as": "current_research_gap_status_v10",
              "non_G02_effective_statuses_unchanged": True,
              "required_central_checks": checks, "effective_status_view": "current_research_gap_status",
              "effective_statuses": current, "production_admission": "HOLD", "capture": False}
    with receipt.open("x") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("baseline", "evidence-map", "status-file", "output", "receipt"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    result = build(args.baseline, args.evidence_map, args.status_file, args.output, args.receipt)
    print(json.dumps({key: result[key] for key in (
        "database_sha256", "database_bytes", "preserved_table_count", "preserved_row_count", "new_evidence_rows")}))
