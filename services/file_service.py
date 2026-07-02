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
    print(f"save attachment: filename = {filename}")

    save_path = WORKSPACE / filename
    print(f"save attachment: save_path = {save_path}")

    if save_path.exists():
        print(f"save attachment: 이미 존재함")
        stem = save_path.stem
        suffix = save_path.suffix

        index = 1

        while True:
            new_path = WORKSPACE / f"{stem}_{index}{suffix}"
            print(f"save attachment: 새 경로로 재시도 : {new_path}")
            if not new_path.exists():
                save_path = new_path
                print(f"save attachment: 중복되지 않은 경로 : {save_path}")
                break

            index += 1

    print(f"save attachment: {save_path}로 저장 시도")
    await attachment.save(save_path)
    print(f"save attachment: 저장 완료")

    return save_path
