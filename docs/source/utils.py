import json
import os

from urllib.request import urlopen

api_version = "0.3.0"
version = "1.5.0-beta"

capability_table_header = (
    "| Type | Method | Capability | Description |",
    "| ---- | :----: | ---------- | ----------- |",
)
capability_table_row = "\n| {type} | {method} | {capability} | {description} |"
source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps")


def get_api(app):
    api_url = "https://raw.githubusercontent.com/materials-marketplace/standard-app-api/v{}/openapi.json"
    openapi = json.loads(urlopen(api_url.format(api_version)).read())  # nosec B310
    build_capability_table(openapi)
    with open(
        os.path.join(
            source_path,
            "openAPI.json",
        ),
        "w",
    ) as f:
        json.dump(openapi, f, indent=4)


def build_capability_table(openapi):
    capability_table = "\n".join(capability_table_header)
    paths = openapi.get("paths")
    for _, path_obj in paths.items():
        for method, method_obj in path_obj.items():
            capability = method_obj.get("operationId")
            description = method_obj.get("summary").replace("\n", " ")
            tags = ", ".join(method_obj.get("tags"))
            capability_table += capability_table_row.format(
                type=tags, method=method, capability=capability, description=description
            )
    with open(
        os.path.join(
            source_path,
            "capability_table.md",
        ),
        "w",
    ) as f:
        f.write(capability_table)


def source_read_handler(app, docname, source):
    result = source[0]
    result = result.replace("{platform_version}", version)
    result = result.replace("{api_version}", api_version)
    source[0] = result
