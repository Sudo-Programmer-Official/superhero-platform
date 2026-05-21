# S3 Storage Prefix Isolation Policy

## Bucket Contract
- Bucket: `openmat-media-prod`
- Region: `us-east-1`
- Project prefix: `superhero-platform`

## Security Baseline
- ACLs disabled.
- Block public access: all enabled.
- Encryption: SSE-S3 default encryption.
- Versioning: enabled.

## Prefix Contract
Under `superhero-platform/`, enforce:
- `practitioners/`
- `deals/`
- `wallet-assets/`
- `branding/`
- `temp/`

## Effective Path Example
- `superhero-platform/deals/<firebase_uid>/<uuid>.jpg`

## Backend-Controlled Upload Rule
Frontend must never write random S3 paths.
Backend API controls:
- key generation
- folder validation
- ownership binding
- MIME/type and size policy checks
- signed URL issuance
- final metadata binding to domain records

## API Contract
1. `POST /api/v1/storage/presign-upload`
- Request:
  - `folder`: `practitioners | deals | wallet-assets | branding | temp`
  - `filename`
  - `content_type`
  - `content_length`
- Response:
  - `object_key`
  - `upload_url`
  - `content_type`
  - `expires_in`
  - `max_content_length`

2. `POST /api/v1/storage/finalize-asset`
- Binds uploaded key to domain models with ownership checks.
- Current targets:
  - `practitioner.profile_image`
  - `deal_card.image`

## Environment Variables
- `AWS_REGION=us-east-1`
- `S3_BUCKET=openmat-media-prod`
- `S3_PREFIX=superhero-platform`
- `S3_PRESIGN_EXPIRES_SECONDS=900`

## Future Extensions (Non-MVP)
- CloudFront signed delivery
- image variants/optimization pipeline
- lifecycle transitions by prefix
