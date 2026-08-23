# Ktor Rig Catalog Migration Plan

## Outcome

Migrate Sakura Rig Utilities from the legacy static `sacr-index.json` and
companion checksum files to the normalized Sedaia Designs Ktor release API.
Blender should be able to refresh the available rig list, retain a known-good
catalog when a refresh fails, and construct working artifact download URLs.

The catalog endpoint is:

```text
https://sakura-sedaia.com/api/v1/projects/sakura-character-rig/releases
```

The endpoint returns all enabled release channels, releases, and artifacts.
Use the complete `/releases` endpoint rather than `/releases/latest`, because
the Rig Manager needs to present more than one selectable rig.

## Current behavior

`Extension/src/rig_manager/lib/manifest.py` downloads both
`sacr-index.json.sha256` and `sacr-index.json`. It compares the remote checksum
with the stored checksum and the locally calculated hash before replacing the
cached manifest.

That workflow assumes two static files. The Ktor API instead provides one JSON
response with a normalized schema and currently sends
`Cache-Control: public, max-age=300`. It does not provide a companion checksum
resource.

The migration should therefore replace the remote-checksum protocol rather
than reproduce it in Ktor. HTTPS protects the response in transit, while JSON
validation and atomic replacement protect the extension's local cache from an
invalid or interrupted refresh.

## Target API contract

Model only the response fields the extension consumes. At minimum, expect:

```json
{
  "project": {
    "displayName": "Sakura Character Rig",
    "software": "Blender",
    "summary": "A production-ready character rig for Blender."
  },
  "channels": [
    {
      "name": "stable",
      "description": "Stable Branch",
      "latestVersion": "R7.4.1",
      "releases": [
        {
          "version": "R7.4.1",
          "displayName": "Release 7.4.1",
          "publishedAt": "2025-12-20",
          "notes": "SACR R7.4.1",
          "artifacts": [
            {
              "name": "Standard",
              "fileName": "SACR.R7.4.1.blend",
              "sizeBytes": 8220836,
              "mediaType": "application/octet-stream",
              "downloadUrl": "/lib/assets/blender/SACR/Stable/SACR.R7.4.1.blend",
              "notes": "The Standard build of the rig"
            }
          ]
        }
      ]
    }
  ]
}
```

Treat additional response fields as forward-compatible. Reject missing or
incorrectly typed required fields, empty channel/release/artifact identifiers,
and artifact download URLs that cannot be resolved safely.

The backend already omits disabled releases and artifacts. The extension does
not need to duplicate that filtering unless the API contract later exposes
disabled records.

## Implementation steps

### 1. Introduce catalog parsing and validation

- Add a reusable, Blender-independent catalog module under
  `Extension/src/rig_manager/lib/`.
- Parse response bytes with Python's `json` module.
- Convert the JSON into typed application data, using dataclasses or
  `TypedDict` plus explicit runtime validation.
- Keep server field names at the parsing boundary and expose clear Python
  names to the rest of the Rig Manager.
- Preserve unknown fields so backend additions do not break older extension
  releases.
- Raise a catalog-specific validation exception that distinguishes malformed
  or incompatible data from network and filesystem failures.

This boundary prevents Blender panels and operators from depending directly on
unvalidated dictionaries.

### 2. Replace the checksum download workflow

- Change the default manifest URL in
  `Extension/src/rig_manager/lib/manifest.py` to the Ktor `/releases`
  endpoint.
- Remove the required `checksum_url` parameter and remote `.sha256` download.
- Download the response into a temporary sibling file.
- Parse and validate the temporary response before it replaces the existing
  cache.
- Atomically replace the cached catalog only after validation succeeds.
- Leave the previous known-good catalog untouched when the request, decoding,
  validation, or replacement fails.
- Clean up temporary files on every exit path.

The cache filename may remain `sacr-index.json` for a low-risk migration, even
though its schema changes. Rename it to `sacr-release-catalog.json` only if all
call sites and stale local files are migrated deliberately.

### 3. Update the shared HTTP boundary

- Reuse `Extension/src/sru_lib/http.py` for network access rather than placing
  `urllib` calls in the Blender operator.
- Continue passing an explicit timeout from extension preferences.
- Ensure the helper validates the HTTP response before returning or replacing
  a destination.
- If response metadata becomes useful, add a small response/result type rather
  than leaking a live `urllib` response outside the helper.

Conditional requests are optional for the first migration. If the Ktor API
later sends `ETag`, persist it beside the cache and send `If-None-Match` on the
next refresh; treat `304 Not Modified` as a successful reuse of the cached
catalog.

### 4. Adapt Rig Manager consumers

- Replace lookups based on the legacy `SACR.branches.*.versions[].builds`
  hierarchy with the normalized `channels[].releases[].artifacts` hierarchy.
- Use the API channel names directly, including `stable` and `development`.
- Display `displayName`, `publishedAt`, `notes`, and `sizeBytes` without
  reintroducing legacy string fields such as `size: "1.6mb"`.
- Keep stable identifiers separate from display labels: use `version` and
  `fileName` for selection/storage, and `displayName` or `name` for UI text.
- Resolve root-relative artifact URLs against the configured site origin:

  ```python
  from urllib.parse import urljoin

  artifact_url = urljoin("https://sakura-sedaia.com", download_url)
  ```

- Reject artifact URLs that resolve to an unexpected scheme or host before
  downloading. This keeps catalog data from silently redirecting downloads to
  an unintended origin.

### 5. Keep the Blender operator thin

- Retain the `bpy.app.online_access` check in
  `OT_download_available_riglist.py`.
- Let the library layer perform downloading, parsing, validation, caching, and
  cleanup.
- Translate expected network, JSON validation, and filesystem exceptions into
  concise `self.report({"ERROR"}, ...)` messages and return `{"CANCELLED"}`.
- Return `{"FINISHED"}` only when the new catalog was installed or a valid
  cached catalog was intentionally reused.

## Test plan

Update `Extension/tests/test_manifest.py` and add focused parser tests that run
without Blender.

Cover at least:

- a valid API response is parsed and atomically cached;
- stable and development channels retain their releases and artifacts;
- root-relative download URLs resolve against the public site origin;
- unknown response fields are accepted;
- malformed JSON is rejected and the previous cache remains unchanged;
- missing or incorrectly typed required fields are rejected;
- an empty or invalid artifact URL is rejected;
- an HTTP failure preserves the previous cache;
- a failed filesystem replacement preserves the previous cache and removes
  temporary files;
- a first-run failure does not leave a partial catalog;
- the configured timeout reaches the HTTP helper;
- tests and production code no longer request a `.sha256` URL.

Use representative fixtures trimmed to the smallest complete project, channel,
release, and artifact objects. Avoid copying the entire production catalog into
unit tests.

## Verification

From the repository root, run:

```shell
uv run python -m compileall Extension/src
uv run python -m unittest discover -s Extension/tests -v
```

Then validate inside a supported Blender version:

1. Enable online access and refresh the available rig list.
2. Confirm stable and development releases appear with the expected artifacts.
3. Download one root-relative artifact and confirm the resolved URL works.
4. Disable connectivity, refresh again, and confirm the last known-good catalog
   remains usable with an understandable error report.
5. Disable Blender online access and confirm the operator cancels before making
   a request.

The automated checks prove the reusable Python behavior. They do not prove
Blender operator reporting, UI presentation, or interactive download behavior,
which require the final Blender validation.

## Completion criteria

- The extension makes no request for `sacr-index.json.sha256`.
- The Ktor `/releases` endpoint is the single source of available rig data.
- Invalid or interrupted refreshes cannot overwrite a valid local catalog.
- Rig Manager code consumes validated catalog objects rather than raw nested
  dictionaries.
- Artifact URLs are resolved and checked before download.
- Unit tests cover success, compatibility, and cache-preservation failures.
- The extension passes compilation and unit tests, followed by a successful
  interactive Blender refresh and artifact download.
