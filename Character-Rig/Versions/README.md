# Versions Archive

The source rig archive follows the same channel and version hierarchy as the
[CDN upload tree](../CDN-Upload/sakura-character-rig/):

```text
Versions/
├── release/
│   └── R<major>/<major.minor.patch>/
├── beta/
│   └── B<major>/<major.minor.patch>/
└── canary/
    └── C<major>/<major.minor.patch>/
```

Each version directory holds its `.blend` files and any version-specific notes,
images, or extras. Legacy SAMR releases use `release/R0/<version>/` and retain
the `SAMR` filename prefix. Release candidates and Beta builds belong in
`beta`; Alpha and Proto builds belong in `canary`.

Rig filenames follow the [build naming conventions](../../README.md#build-naming-conventions):
`SACR.<channel><major.minor.patch>[-modifier].blend`, with `R`, `B`, or `C`
for the channel. For example, `release/R7/7.2.0/SACR.R7.2.0-Standard.blend`
is a source rig. The corresponding download is a ZIP under
`CDN-Upload/sakura-character-rig/release/R7/7.2.0/`; upload archive names omit
`.blend`. The Pack ZIPs for releases 7.2.0 through 7.4.1 also include the
companion `SRGUI.R3.1.0.zip`.

Do not edit a source `.blend` through the CDN copy. Rebuild the matching ZIP
after changing a rig or its supporting files.
