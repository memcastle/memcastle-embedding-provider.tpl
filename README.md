# MemCastle embedding-provider template

Render a standalone embedding module, or compose it into a provider plugin with `memcastle-plugin.tpl`.
It implements the `memcastle:embedding@0.2.0` component contract with a deterministic sample model; replace the
sample vectors and model declaration with your actual embedding implementation before publication.

Requires GitTPL 0.14+, Rust 1.100+ with `wasm32-wasip3`, wasm-tools 1.263.0, Python 3.11+, and migrated development Core.
Use Core commit `828f0f6` or a descendant, with its Wasmtime 50.0.3 runtime.
Stable 0.5.2 predates the migration even though development currently reports the same version.
The parent's transitional `>=0.5, <0.6` range cannot distinguish those binaries;
tighten it when the first compatible stable release exists.

```sh
git tpl init https://github.com/memcastle/memcastle-embedding-provider.tpl example --init \
  --answer module_name=example --defaults --strict-answers --trust --json
cd example
cargo generate-lockfile
cargo test --locked
cargo build --locked --release --target wasm32-wasip3
cp target/wasm32-wasip3/release/example.wasm embedding.wasm
python3 tests/conformance.py
```

In a plugin project, the parent descriptor declares the module at
`embeddings/<id>/memcastle-embedding.toml` with entry `embeddings/<id>/embedding.wasm` and contract `0.2.0`.
The parent builds, packages and runs `memcastle plugin test` against the prebuilt component.
Update the model metadata and `models()` together: Core checks that they agree before installation.
`embed()` must return one finite vector of the requested dimension per input in order.
Run `TEMPLATE_ROOT="$PWD" git tpl test --json` to build, validate and execute standalone and nested components.
The generated `tests/conformance.py` uses a disposable plugin and isolated Core daemon to execute sample embeddings.
It also accepts `--archive PATH --plugin-id ID --module-id ID` to check a containing plugin's actual release artifact.
Core validates vector count, dimensions and finiteness; native tests check deterministic vectors and batch ordering.
CI records the tested development Core SHA.
See [Core's embedding module contract](https://github.com/memcastle/memcastle/blob/main/docs/plugins.md#plugin-packages).
