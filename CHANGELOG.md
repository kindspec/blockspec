<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Changelog

Notable changes to blockspec. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning is
[SemVer](https://semver.org/).

## [0.1.0] — 2026-11-09

The first release of draft 0.

### Added

- `blockspec check`, which reads files and directories and reports each
  document the profile refuses, with a code. It exits 0 when every document
  reads, 1 when one is refused, and 2 when nothing could be checked.
- A GitHub Action, `kindspec/blockspec@v0.1.0`.
- The reference reader, the anchor resolver and the editing API.
- A second implementation, written from `SPEC.md` alone, run against the same
  767 conformance cases.
- `merge` conformance cases, which run stock `git merge` and read the result.
- Two refusals, `dangling-link` and `name-shadows-slug`, from adjudication 0005.

[0.1.0]: https://github.com/kindspec/blockspec/releases/tag/v0.1.0
