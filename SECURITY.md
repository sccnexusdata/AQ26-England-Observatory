# Security policy

This repository is intentionally public and must contain only material approved for public release.

## Reporting a security concern

If you believe a credential, private key, token, internal-only document or other sensitive material has been exposed, **do not reproduce the sensitive value in a public issue or pull request**. Report the concern through GitHub's private security-reporting facilities where available, or contact the repository owner without including the secret in public discussion.

## Publication boundary

The public release process rejects protected/test paths, common credential/private-key markers, unexpected symlinks and oversized files. The public repository does not require read access to the private AQ26 scientific engine.

## Scope

Security reports are especially useful for:

- accidental credential or private-key disclosure;
- a public workflow that could gain broader repository permissions than intended;
- provenance or manifest tampering;
- path traversal/symlink behaviour in a release bundle;
- publication of material that was explicitly classified as protected/internal.

Scientific disagreements and data corrections should normally use the contribution process rather than the security channel unless sensitive information is involved.
