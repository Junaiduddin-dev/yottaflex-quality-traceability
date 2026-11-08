
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIRS = [
    ROOT / "data" / "csv",
    ROOT / "data" / "json",
    ROOT / "data" / "sql",
    ROOT / "data" / "ground_truth",
]

MANIFEST = ROOT / "docs" / "export_checksums.sha256"


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def collect_checksums():
    checksums = {}

    for directory in DATA_DIRS:
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file():
                relative_path = file_path.relative_to(ROOT).as_posix()
                checksums[relative_path] = calculate_sha256(file_path)

    return checksums


def save_baseline(checksums):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    with MANIFEST.open("w", encoding="utf-8") as file:
        for path, checksum in sorted(checksums.items()):
            file.write(f"{checksum}  {path}\n")

    print("Baseline checksum manifest created.")
    print("Manifest:", MANIFEST)


def load_baseline():
    if not MANIFEST.exists():
        raise FileNotFoundError(
            "Baseline manifest not found. Run with baseline first."
        )

    checksums = {}

    with MANIFEST.open("r", encoding="utf-8") as file:
        for line in file:
            checksum, path = line.strip().split("  ", 1)
            checksums[path] = checksum

    return checksums


def compare_checksums(current, baseline):
    all_paths = sorted(set(current) | set(baseline))
    differences = []

    for path in all_paths:
        old = baseline.get(path)
        new = current.get(path)

        if old != new:
            differences.append(path)

    if differences:
        print("\nREPRODUCIBILITY CHECK: FAILED")
        print("Files changed or missing:")

        for path in differences:
            print("[CHANGED]", path)

        return False

    print("\nREPRODUCIBILITY CHECK: PASSED")
    print("Files compared:", len(current))
    print("All SHA-256 checksums match.")

    return True


def main():
    print("\nYOTTAFLEX REPRODUCIBILITY CHECK")
    print("===============================")

    current = collect_checksums()

    if not current:
        print("No exported files found.")
        raise SystemExit(1)

    if len(sys.argv) != 2 or sys.argv[1] not in (
        "--baseline",
        "--compare",
    ):
        print("Usage:")
        print("python -m validation.reproducibility_check --baseline")
        print("python -m validation.reproducibility_check --compare")
        raise SystemExit(1)

    if sys.argv[1] == "--baseline":
        save_baseline(current)
        print("Files fingerprinted:", len(current))

    elif sys.argv[1] == "--compare":
        baseline = load_baseline()

        if not compare_checksums(current, baseline):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
