# Versioning and releases

The whole repo is versioned as one unit rather than as five
independently-versioned services. Every merge to `main` inspects the
commit messages since the last tag and bumps accordingly: a `feat:` commit
bumps minor, a breaking-change marker (`!` after the type, or a
`BREAKING CHANGE` footer) bumps major, anything else bumps patch. That
version becomes the new git tag, a GitHub Release, and the tag applied to
all four images on GHCR in the same run.

There's no manual version bump and no changelog to maintain by hand. The
current version always matches the latest tag; check the
[Releases page](https://github.com/platformfix/k8coins/releases) or
`git tag` rather than trusting a number written into prose.

## Published images

Each built service publishes to GHCR on every release, tagged with the
release version and `latest`:

```
ghcr.io/platformfix/k8coins-rng:<version>
ghcr.io/platformfix/k8coins-hasher:<version>
ghcr.io/platformfix/k8coins-worker:<version>
ghcr.io/platformfix/k8coins-webui:<version>
```

`redis` isn't built by this repo; pull the upstream `redis:7-alpine` image
directly. The four published images are public - anyone can `docker pull`
them without credentials.
