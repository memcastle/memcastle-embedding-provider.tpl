"""Validate both native sample behavior and the generated component in Core."""

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tomllib


def run(*args: str) -> None:
    subprocess.run(args, check=True)


module = pathlib.Path(sys.argv[1]).resolve()
manifest = str(module / "Cargo.toml")
run("cargo", "generate-lockfile", "--manifest-path", manifest)
run("cargo", "fmt", "--manifest-path", manifest, "--all", "--", "--check")
run("cargo", "test", "--manifest-path", manifest, "--locked", "--lib")
run(
    "cargo",
    "clippy",
    "--manifest-path",
    manifest,
    "--locked",
    "--target",
    "wasm32-wasip3",
    "--",
    "-D",
    "warnings",
)
run(
    "cargo",
    "build",
    "--manifest-path",
    manifest,
    "--locked",
    "--release",
    "--target",
    "wasm32-wasip3",
    "--target-dir",
    str(module / "target"),
)
package = tomllib.loads((module / "Cargo.toml").read_text())["package"]["name"]
component = (
    module / "target/wasm32-wasip3/release" / f"{package.replace('-', '_')}.wasm"
)
wasm_tools = os.environ.get("WASM_TOOLS_BIN", "wasm-tools")
run(
    wasm_tools,
    "validate",
    "--features",
    "cm-async,cm-async-stackful,cm-more-async-builtins",
    str(component),
)
wit = subprocess.check_output(
    [wasm_tools, "component", "wit", str(component)], text=True
)
world = wit.split("world root {", 1)[1].split("\n}", 1)[0]
imports = re.findall(r"^\s*import (wasi:[^;]+);", world, re.MULTILINE)
if not imports or any(not name.endswith("@0.3.0") for name in imports):
    raise ValueError(f"expected WASI 0.3.0 imports, got {imports}")
if "export memcastle:embedding/provider@0.2.0;" not in world:
    raise ValueError("missing embedding 0.2.0 export")
shutil.copyfile(component, module / "embedding.wasm")
run(sys.executable, str(module / "tests/conformance.py"))
