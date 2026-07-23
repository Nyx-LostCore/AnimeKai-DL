from pathlib import Path


def resolve_collision_path(dest: Path) -> Path:
    if not dest.exists():
        return dest

    stem = dest.stem
    suffix = dest.suffix
    counter = 1

    while True:
        candidate = dest.with_name(f"{stem} ({counter}){suffix}")

        if not candidate.exists():
            return candidate

        counter += 1