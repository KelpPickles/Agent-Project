from pathlib import Path
import re

WORKSPACE = Path("workspace").resolve()

def sanitize_filename(filename: str) -> str:
    filename = filename.replace("\\", "/")

    parts = []

    for part in filename.split("/"):
        if part in ("", ".", ".."):
            continue

        part = re.sub(
            r'[<>:"/\\|?*\x00-\x1F]',
            "_",
            part
        )

        parts.append(part)
    
    return "/".join(parts)

def write_file(filename: str, content: str) -> Path:
    filename = sanitize_filename(filename)

    path = (WORKSPACE / filename).resolve()

    if not str(path).startswith(str(WORKSPACE)):
        raise ValueError("허용되지 않은 경로.")
    
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return {"path": str(path)}