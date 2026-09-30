/**
 * Domain-friendly re-exports of generated API models.
 *
 * Import from here instead of reaching into `api/generated/models/` directly.
 * This barrel strips transport-layer suffixes (Response, Request) so that
 * services and components think in domain terms.
 */

export type { CheckInResponse as CheckIn } from './generated/models/check-in-response';
export type { CreateCheckInRequest as CreateCheckIn } from './generated/models/create-check-in-request';
export type { CreateEventRequest as CreateEvent } from './generated/models/create-event-request';
export type { CreateGeneralCheckInRequest as CreateGeneralCheckIn } from './generated/models/create-general-check-in-request';
export type { EventResponse as Event } from './generated/models/event-response';
export type { HttpValidationError } from './generated/models/http-validation-error';
export type { TokenResponse as Token } from './generated/models/token-response';
export type { UpdateCheckInRequest as UpdateCheckIn } from './generated/models/update-check-in-request';
export type { UpdateEventRequest as UpdateEvent } from './generated/models/update-event-request';
export type { UpdateProfileRequest as UpdateProfile } from './generated/models/update-profile-request';
export type { UserLoginRequest as UserLogin } from './generated/models/user-login-request';
export type { UserProfile } from './generated/models/user-profile';
export type { UserSignUpRequest as UserSignUp } from './generated/models/user-sign-up-request';
export type { ValidationError } from './generated/models/validation-error';
export type { DietaryPreference } from './generated/models/dietary-preference';
export { DIETARY_PREFERENCE } from './generated/models/dietary-preference-array';
export type { EventCreationType } from './generated/models/event-creation-type';
export { EVENT_CREATION_TYPE } from './generated/models/event-creation-type-array';
export type { EventStatus } from './generated/models/event-status';
export { EVENT_STATUS } from './generated/models/event-status-array';
export type { UserRole } from './generated/models/user-role';
export { USER_ROLE } from './generated/models/user-role-array';
