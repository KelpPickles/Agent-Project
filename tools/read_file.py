from pathlib import Path
import json
import csv

WORKSPACE = Path("workspace").resolve()

def read_file(filename: str) -> str:
    print(f"read_file called: {filename}")
    path = (WORKSPACE / filename).resolve()

    if not str(path).startswith(str(WORKSPACE)):
        raise ValueError("허용되지 않은 경로.")
    
    if not path.exists():
        raise FileNotFoundError(f"{filename} 파일이 존재하지 않음.")
    
    extension = path.suffix.lower()

    if extension in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
        
    elif extension == ".json":
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)

        return json.dumps(
            obj,
            ensure_ascii=False,
            indent=2
        )
    
    elif extension == ".csv":
        rows = []

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)

            for row in reader:
                rows.append(", ".join(row))

        return "\n".join(rows)
    
    else:
        raise ValueError(f"지원하지 않는 형식 : {extension}")
    