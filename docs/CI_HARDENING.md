# CI Hardening & Optimization

## Build Immutability
-   **Tags**: We tag images with the Git Commit SHA (`app:a1b2c3d`). This ensures we know exactly what code is in the container.
-   **Reproducibility**: We use pinned base images (SHA256 digests) and pinned dependencies to ensure builds are repeatable.

## Artifact Signing
-   We use `cosign` to sign container images.
-   This proves the image came from our CI pipeline and hasn't been tampered with.

## SBOM (Software Bill of Materials)
-   Every build generates an SBOM (`sbom.json`).
-   This list of ingredients allows us to quickly check if we are affected by new vulnerabilities (like Log4j) without rescanning everything.

## Gating Rules
-   **Vulnerabilities**: CI fails if `pip-audit` finds High/Critical bugs.
-   **Image Size**: CI fails if the image is > 200MB.
-   **Pinning**: CI fails if Dockerfile uses mutable tags like `latest`.

## Rollback Strategy
If a bad image is deployed:
1.  Identify the last known good Commit SHA.
2.  Run `aws ecs update-service --task-definition family:revision` to revert.
3.  Or use the `canary_release.sh` script to deploy the old tag.

## Local Validation
Before pushing:
1.  Run `python infra/ci/verify_pinned_base.py`
2.  Run `python infra/ci/check_image_size.py`
