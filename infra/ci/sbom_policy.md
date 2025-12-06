# SBOM Policy

## Format
We use **CycloneDX** JSON format for Software Bill of Materials (SBOM).

## Generation
SBOMs are generated during the CI build process using `syft`.
```bash
syft <image> -o cyclonedx-json > sbom.json
```

## Retention
-   SBOMs are stored as GitHub Actions artifacts for 90 days.
-   For production releases, SBOMs are uploaded to S3 bucket `s3://REPLACE_ME_BUCKET/sboms/`.

## Verification
We use `grype` to scan the SBOM for vulnerabilities.
```bash
grype sbom:sbom.json
```

## Policy
-   All production images MUST have an associated SBOM.
-   SBOMs must be signed using `cosign` (future enforcement).
