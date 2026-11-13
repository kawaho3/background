# Background — transparent character video extraction

**Goal:** Turn a video with a moving character into a **silent, transparent video containing the original moving character and no background**. Preserve movement and original frame order so the result can be placed into any new scene.

This is a **local-first, free-tool** project: no paid API, plugin, or per-video credit is required. Contributors are welcome; see CONTRIBUTING.md.

## Current status (13 November 2026)

A prior session produced a 19.4-second / 485-frame silent transparent character export (WebM and MOV). Those existing videos are **not uploaded here**, and the precise original extraction pipeline is not recovered. This repository now contains a **new baseline extractor**, local tests, project goals, roadmap, quality checklist and recovered source files from a related still-image animation experiment. **The new extractor has not yet been run end-to-end against the original clip.** Avoid treating earlier output as a test of the new implementation.

## Quick start

Install Python, FFmpeg and ffprobe (both available on PATH). The local rembg model downloads once at initial use; no cloud inference is required.

~~~bash
git clone https://github.com/kawaho3/background.git
cd background
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/extract_character.py source.mp4 character.webm
# Or editor-friendly alpha MOV, usually much larger:
python scripts/extract_character.py source.mp4 character.mov
python -m unittest discover -s tests -v
~~~

**Output:** WebM VP9 with alpha (not all players show alpha) or MOV QuickTime Animation with alpha; both have **no audio**. The baseline uses independently segmented frames and may show flicker, missed details and variable-frame-rate drift. It is a starting point, not a finished temporal matting system.


## New contributor — full project handoff

**Start with [PROJECT_HANDOFF.md](docs/PROJECT_HANDOFF.md).** It explains the exact request, constraints, known historical outputs, what was recovered, what is missing, and the next steps. No ChatGPT conversation is needed.

1. [Developer setup](docs/DEVELOPER_SETUP.md) — clone/install and local demo
2. [Verified original exports](docs/VERIFIED_MEDIA.md) — original input/output hashes, 485-frame/19.4-second evidence, sampled alpha, zero audio
3. [Release checklist](docs/RELEASE_CHECKLIST.md) — objective done criteria
4. [Asset provisioning](docs/ASSET_PROVISIONING.md) — which files are outside Git and how the owner can supply them
5. [Decision log](docs/DECISION_LOG.md) — architectural and policy decisions

A self-contained **synthetic** character/transparent-reference demo is generated locally, without the original source video or paid services:

```sh
python scripts/make_demo.py --output-dir output/synthetic-demo
python scripts/verify_export.py output/synthetic-demo/synthetic_reference_alpha.mov --strict
python -m unittest discover -s tests -v
```

The old historical MOV uses ProRes alpha, so the new extractor now defaults to a ProRes MOV when given a `.mov` output. This change was checked with local codec/alpha tests; the new rembg extraction model has not yet been validated end-to-end against the original video.

## Read this to contribute

- [Project brief](docs/PROJECT_BRIEF.md) — the user request, constraints and acceptance criteria
- [Architecture](docs/ARCHITECTURE.md) — what works, what is planned and how the pipeline flows
- [Status](docs/STATUS.md) — honest completed-vs-unfinished checklist
- [Roadmap](docs/ROADMAP.md) — prioritized development tasks
- [Quality checklist](docs/QUALITY.md) — verify actual alpha, motion and silence
- [Asset manifest](docs/ASSET_MANIFEST.md) — which original videos/exports exist outside Git
- [Related work](docs/RELATED_WORK.md) — source from 2D eye/lip animation and separate Blender work
- [Contributing](CONTRIBUTING.md) — setup, rules and PR process

### Repository layout

| Path | Purpose |
| --- | --- |
| scripts/extract_character.py | New free, local extraction baseline |
| tests/ | Unit tests for alpha formats and audio exclusion |
| docs/ | Goal, status, architecture, roadmap, media inventory and quality gates |
| examples/flower-friends/ | Previously produced *text/source* for a separate 30s animated flower lesson |

## Scope and ownership

The project focuses on **extracting the foreground from existing video**, not downloading third-party media, web scraping, or full 3D show production. All source videos, proprietary media, model weights and big rendered outputs require rights review before public distribution. A project-wide original-code/asset license has **not yet been selected**; maintainers should decide it before unrestricted reuse.

**Reproducibility update:** `tests/test_synthetic_integration.py` runs a tiny generated character through both alpha codecs and verifies sampled alpha, size and silence. The media analysis from historical outputs is also available as machine-readable [JSON](docs/evidence/historical_exports_verified.json). Seven local tests now pass (the integration test skips when FFmpeg/Pillow are missing).
