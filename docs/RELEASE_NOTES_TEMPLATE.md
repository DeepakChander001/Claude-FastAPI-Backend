# Release Notes Template

## Release: vX.Y.Z

**Date**: YYYY-MM-DD  
**Author**: REPLACE_ME  
**Reviewers**: REPLACE_ME

---

## Summary

Brief description of what this release contains.

## Changes

### Features
- Feature 1 description
- Feature 2 description

### Bug Fixes
- Fix 1 description
- Fix 2 description

### Breaking Changes
- ⚠️ Breaking change description

## Migration Steps

1. Step 1
2. Step 2
3. Step 3

## Rollback Steps

```bash
./infra/scripts/rollback_release.sh --live
```

## Impacted APIs

| Endpoint | Change |
|----------|--------|
| `POST /api/enqueue` | New field added |
| `GET /health` | No change |

## Testing Performed

- [ ] Unit tests
- [ ] Integration tests
- [ ] Smoke tests (staging)
- [ ] Load test
- [ ] Canary deployment

## Known Issues

- Issue 1 (tracked in REPLACE_ME_TICKET)

## Dependencies

- Dependency 1: version X.Y
- Dependency 2: version X.Y

---

## Approval

| Role | Name | Approved |
|------|------|----------|
| Engineering | REPLACE_ME | [ ] |
| QA | REPLACE_ME | [ ] |
| Product | REPLACE_ME | [ ] |
