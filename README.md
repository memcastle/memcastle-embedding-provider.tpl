# MemCastle embedding-provider template

Render a standalone embedding module, or compose it into a provider plugin with `memcastle-plugin.tpl`.
It implements the `memcastle:embedding@0.1.0` component contract with a deterministic sample model; replace the
sample vectors and model declaration with your actual embedding implementation before publication.

Requires GitTPL 0.14+, Rust with `wasm32-wasip2`, and a plugin-capable MemCastle binary.

```sh
git tpl init https://github.com/memcastle/memcastle-embedding-provider.tpl example --init \
  --answer module_name=example --defaults --strict-answers --trust --json
cd example
cargo generate-lockfile
cargo test --locked
cargo build --locked --release --target wasm32-wasip2
cp target/wasm32-wasip2/release/example.wasm embedding.wasm
```

In a plugin project, the parent descriptor declares the module at
`embeddings/<id>/memcastle-embedding.toml` with entry `embeddings/<id>/embedding.wasm` and contract `0.1.0`.
The parent builds, packages and runs `memcastle plugin test` against the prebuilt component.
Update the model metadata and `models()` together: Core checks that they agree before installation.
`embed()` must return one finite vector of the requested dimension per input in order.
See [Core's embedding module contract](https://github.com/memcastle/memcastle/blob/main/docs/plugins.md#plugin-packages).
