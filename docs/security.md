# Security status

The Phase 1 foundation is not ready for public use. Authentication, authorization, CSRF protection, rate limiting, per-user quotas, account lifecycle, and upload validation are not implemented yet. Do not expose the service publicly.

Current safeguards: settings reject the development secret and localhost/local database URL in production mode; CORS origins are configurable; Docker excludes `.env` and data directories; production container runs as non-root; the app has no user-controlled filesystem route. The health endpoint exposes operational status only, not absolute data paths or exception messages.

Phase 1B must choose an owner-managed/invite-only authentication design, hash passwords with Argon2id or bcrypt, use secure same-site cookies or short-lived tokens, authenticate API and WebSocket access, validate origins, add request/upload quotas, security headers, secret rotation instructions, and verify threat boundaries before public deployment. Self-registration/provider login require explicit owner approval.
