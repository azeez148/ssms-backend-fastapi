import { createReducer, on } from '@ngrx/store';
import { UserProfile } from '../../models';
import * as AuthActions from './auth.actions';

export interface AuthState {
  token: string | null;
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
}

export const initialState: AuthState = {
  token: null,
  user: null,
  loading: false,
  error: null,
};

export const authReducer = createReducer(
  initialState,

  on(AuthActions.login, AuthActions.register, (state) => ({
    ...state,
    loading: true,
    error: null,
  })),

  on(AuthActions.loginSuccess, AuthActions.registerSuccess, (state, { token, user }) => ({
    ...state,
    token,
    user,
    loading: false,
    error: null,
  })),

  on(AuthActions.loginFailure, AuthActions.registerFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),

  on(AuthActions.restoreSession, (state, { token, user }) => ({
    ...state,
    token,
    user,
  })),

  on(AuthActions.loadProfile, (state) => ({
    ...state,
    loading: true,
  })),

  on(AuthActions.loadProfileSuccess, AuthActions.updateProfileSuccess, (state, { user }) => ({
    ...state,
    user,
    loading: false,
    error: null,
  })),

  on(AuthActions.loadProfileFailure, AuthActions.updateProfileFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),

  on(AuthActions.updateProfile, (state) => ({
    ...state,
    loading: true,
    error: null,
  })),

  on(AuthActions.logout, () => ({
    ...initialState,
  }))
);
