# Observability and Debugging

## Objective
Treat logging, tracing, and error handling as first-class platform systems from day one.

## Baseline Implemented
- Structured JSON logs in API runtime.
- Request ID propagation via `x-request-id` header.
- Centralized exception handling for HTTP and unhandled errors.
- Consistent error response envelope with `request_id` for support/debug correlation.

## API Logging Model
Each request emits a completion log with:
- `event`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`

Each error emits:
- `event` (`http.exception` or `unhandled.exception`)
- `request_id`
- method/path/status metadata
- stack trace for unhandled errors

## Environment Controls
- `LOG_LEVEL` (default `INFO`)
- `LOG_FORMAT` (default `json`; reserved for future formatter switch)

## Request Tracing Flow
1. Client can send `x-request-id`.
2. If missing, API generates UUID.
3. Request ID is attached to logs and response headers.
4. Request ID is returned in error payloads.

This enables fast incident triage from client report -> API logs -> DB/API action path.

## Debugging Runbook
1. Capture failing request `x-request-id` from client or gateway logs.
2. Filter API logs by `request_id`.
3. Inspect:
   - request completion event
   - HTTP/unhandled exception event
   - status code and duration spikes
4. Correlate with DB events and external calls (Stripe/Firebase once integrated).
5. If root cause is unknown, add temporary targeted debug logs behind env flags.

## Next Integrations
- Sentry for error aggregation and release tracking.
- PostHog events for funnel and behavior analytics.
- Optional OpenTelemetry export for distributed traces as services expand.

## Cross-Project Pattern Reuse
This implementation follows the same strategic pattern used in other projects:
- strict env-driven config
- centralized middleware
- standardized error envelope
- log-first debugging and incident response
