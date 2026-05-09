# BlaBlaIF Next Steps

These items are intentionally outside V1 so the first platform version stays small and usable.

## Product
- Real institutional email verification instead of domain-only validation.
- Multi-campus support with campus selection and campus-specific ride feeds.
- Maps, geocoding, route distance, and automatic price suggestions.
- Notifications for accepted/rejected requests and cancelled rides.
- In-app chat or structured contact flow after request acceptance.
- Copy button and WhatsApp button (`wa.me` link) wherever a phone number is revealed after acceptance.
- Profile page for users to edit their own account/contact information.
- Recurring rides for common weekly schedules.
- Ratings, reports, and moderation tools.
- Admin views for campuses, users, rides, and safety review.

## Engineering
- Add database migrations before the schema becomes harder to reset.
- Move from local SQLite to a production database for deployment.
- Replace localStorage token handling with a more secure session strategy.
- Add API pagination/filtering once ride volume grows.
- Add end-to-end browser tests for the main dashboard flow.
- Add deployment configuration and production CORS settings.
