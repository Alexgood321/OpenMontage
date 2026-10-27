# Security-hardened macOS usage (Apple Silicon)

**Use only the isolated Docker mode.** No macOS home folder, SSH keys,
Codex credentials, VPN configuration, or API secrets are mounted.
Docker Desktop is required; no direct host installation is needed.

Run from the cloned fork:

```bash
bash scripts/macos-safe.sh build
bash scripts/macos-safe.sh doctor
bash scripts/macos-safe.sh run python -c "import shutil; print(shutil.which('ffmpeg'))"
```

- `input/`: read-only source videos.
- `projects/`, `output/`, `library/`: writable by sandboxed processes.
  Store no secrets in these three folders.
- Docker's Linux VM performs dependency download during **explicit build**;
  runtime is fully offline (`network_mode: none`).
- Runtime is non-root; read-only root filesystem; dropped Linux capabilities;
  bounded RAM, CPU, process count and temporary storage.
- Docker images and dependencies are NOT fully digest/hash pinned. Review image
  builds and supply-chain updates. Do not treat Docker as infallible.
- Cloud APIs, external media acquisition and runtime npm fetches intentionally
  do not work offline. Remotion browser provisioning may require additional
  reviewed dependencies at image build time; full rendering parity is unverified.
- Host invocation of agent-written Python code is disabled by a code-level guard.
- HyperFrames requires an exact explicitly selected npm package version.
- Do NOT grant an agent unrestricted macOS host shell access when using this
  repository. Project text instructions are not an OS security boundary.
- `budget.mode: cap` does not reliably prevent paid API spend. Offline runtime
  provides a network-level spending barrier instead.
- Never run `make setup` directly on macOS. Its host mode is blocked unless
  `OPENMONTAGE_UNSAFE_HOST_SETUP=1` is deliberately set.

Rollback reference: `backup/pre-macos-hardening-2026-10-27`.
Original head: `e01dbf433f46eeb91d39bf905e194162921019a3`.
