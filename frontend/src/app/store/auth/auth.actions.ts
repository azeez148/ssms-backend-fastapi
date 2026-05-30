import { createAction, props } from '@ngrx/store';
import { UserProfile } from '../../models';

export const login = createAction(
  '[Auth] Login',
  props<{ mobile: string; password: string }>()
);

export const loginSuccess = createAction(
  '[Auth] Login Success',
  props<{ token: string; user: UserProfile }>()
);

export const loginFailure = createAction(
  '[Auth] Login Failure',
  props<{ error: string }>()
);

export const register = createAction(
  '[Auth] Register',
  props<{ data: any }>()
);

export const registerSuccess = createAction(
  '[Auth] Register Success',
  props<{ token: string; user: UserProfile }>()
);

export const registerFailure = createAction(
  '[Auth] Register Failure',
  props<{ error: string }>()
);

export const loadProfile = createAction('[Auth] Load Profile');

export const loadProfileSuccess = createAction(
  '[Auth] Load Profile Success',
  props<{ user: UserProfile }>()
);

export const loadProfileFailure = createAction(
  '[Auth] Load Profile Failure',
  props<{ error: string }>()
);

export const updateProfile = createAction(
  '[Auth] Update Profile',
  props<{ data: Partial<UserProfile> }>()
);

export const updateProfileSuccess = createAction(
  '[Auth] Update Profile Success',
  props<{ user: UserProfile }>()
);

export const updateProfileFailure = createAction(
  '[Auth] Update Profile Failure',
  props<{ error: string }>()
);

export const logout = createAction('[Auth] Logout');

export const restoreSession = createAction(
  '[Auth] Restore Session',
  props<{ token: string; user: UserProfile }>()
);
