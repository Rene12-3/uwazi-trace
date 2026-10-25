# Security and responsible disclosure

This is a prototype that runs on synthetic data. It has no authentication, so **do not deploy it with real or sensitive data**.

If you find a vulnerability, please report it privately through GitHub's "Report a vulnerability" feature on this repository
rather than opening a public issue. A production deployment needs, at minimum: SSO with MFA, role-based access and row-level
security, encryption at rest and in transit, an append-only evidence store, and a penetration test before any public launch
(see `docs/ARCHITECTURE.md`).
