from pathlib import Path
import re

WORKSPACE = Path("workspace")
WORKSPACE.mkdir(exist_ok=True)

def sanitize_filename(filename: str) -> str:
    filename = Path(filename).name

    filename = re.sub(
        r'[<>:"/\\|?*\x00-\x1F]',
        "_",
        filename
    )

    return filename

async def save_attachment(attachment) -> Path:
    filename = sanitize_filename(attachment.filename)

    save_path = WORKSPACE / filename

    if save_path.exists():
        stem = save_path.stem
        suffix = save_path.suffix

        index = 1

        while True:
            new_path = WORKSPACE / f"{stem}_{index}{suffix}"
            if not new_path.exists():
                save_path = new_path
                break

        index += 1

    await attachment.save(save_path)

    return save_path
