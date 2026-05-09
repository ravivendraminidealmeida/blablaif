# BlaBlaIF Next Steps

These items are intentionally outside V1 so the first platform version stays small and usable.

## V2 Backlog
Ordered from highest practical return on investment to implementation effort.

- [x] Copy button and WhatsApp button (`wa.me` link) wherever a phone number is revealed after acceptance.
- [x] Split the dashboard into tabs instead of showing all sections in one view.
- [x] Profile page for users to edit their own account/contact information.
- [x] Password change from the profile page.
- [x] Notifications for accepted/rejected requests and cancelled rides.
- [ ] Add database migrations before the schema becomes harder to reset.
- [ ] Add deployment configuration and production CORS settings.
- [ ] Move from local SQLite to a production database for deployment.
- [ ] Add end-to-end browser tests for the main dashboard flow.
- [ ] In-app chat or structured contact flow after request acceptance.
- [ ] Add API pagination/filtering once ride volume grows.
- [ ] Real institutional email verification instead of domain-only validation.
- [ ] Multi-campus support with campus selection and campus-specific ride feeds.
- [ ] Recurring rides for common weekly schedules.
- [ ] Maps, geocoding, route distance, and automatic price suggestions. Consider [OpenFreeMap](https://openfreemap.org/).
- [ ] Ratings, reports, and moderation tools.
- [ ] Admin views for campuses, users, rides, and safety review.
- [ ] Replace localStorage token handling with a more secure session strategy.
