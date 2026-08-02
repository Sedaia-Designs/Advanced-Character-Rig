# Versions Archive

Archived builds are organized by project family and semantic version:

```text
Versions/
├── Legacy/
│   └── SAMR <major.minor.patch>/
└── SACR R<major>/
    └── R<major.minor.patch>/
        ├── Dev/       # Pre-release and development builds, when available
        └── Extras/    # Release-specific supporting assets, when available
```

Stable release files live directly in their version directory. Development builds
and release-specific extras remain inside the version they belong to. Development
builds for an abandoned version number are filed under the release they transitioned
into rather than creating a version directory for an unreleased version.

See the project [changelog](../CHANGELOG.md) for documented release dates and changes.
