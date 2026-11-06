import json
from pathlib import Path

from mnemosyne_api.api.schemas.events import AssassinationEventV1

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts" / "json-schema" / "political.assassination.v1.schema.json"


def main() -> None:
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = AssassinationEventV1.model_json_schema()
    SCHEMA_PATH.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {SCHEMA_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
