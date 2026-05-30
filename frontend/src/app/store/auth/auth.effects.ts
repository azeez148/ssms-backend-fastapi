import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Router } from '@angular/router';
import { of } from 'rxjs';
import { map, exhaustMap, catchError, tap } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { AuthResponse, UserProfile } from '../../models';
import * as AuthActions from './auth.actions';

@Injectable()
export class AuthEffects {
  private readonly baseUrl = environment.apiUrl;

  login$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.login),
      exhaustMap(({ mobile, password }) =>
        this.http.post<AuthResponse>(`${this.baseUrl}/auth/login`, { mobile, password }).pipe(
          map((res) => AuthActions.loginSuccess({ token: res.token, user: res.user })),
          catchError((err) =>
            of(AuthActions.loginFailure({ error: err.error?.detail || 'Login failed' }))
          )
        )
      )
    )
  );

  register$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.register),
      exhaustMap(({ data }) =>
        this.http.post<AuthResponse>(`${this.baseUrl}/auth/register`, data).pipe(
          map((res) => AuthActions.registerSuccess({ token: res.token, user: res.user })),
          catchError((err) =>
            of(AuthActions.registerFailure({ error: err.error?.detail || 'Registration failed' }))
          )
        )
      )
    )
  );

  loadProfile$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.loadProfile),
      exhaustMap(() =>
        this.http.get<UserProfile>(`${this.baseUrl}/auth/profile`).pipe(
          map((user) => AuthActions.loadProfileSuccess({ user })),
          catchError((err) =>
            of(AuthActions.loadProfileFailure({ error: err.error?.detail || 'Failed to load profile' }))
          )
        )
      )
    )
  );

  updateProfile$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.updateProfile),
      exhaustMap(({ data }) =>
        this.http.put<UserProfile>(`${this.baseUrl}/auth/profile`, data).pipe(
          map((user) => AuthActions.updateProfileSuccess({ user })),
          catchError((err) =>
            of(AuthActions.updateProfileFailure({ error: err.error?.detail || 'Failed to update profile' }))
          )
        )
      )
    )
  );

  persistSession$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.loginSuccess, AuthActions.registerSuccess),
        tap(({ token, user }) => {
          localStorage.setItem('token', token);
          localStorage.setItem('user', JSON.stringify(user));
        })
      ),
    { dispatch: false }
  );

  persistProfile$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.loadProfileSuccess, AuthActions.updateProfileSuccess),
        tap(({ user }) => {
          localStorage.setItem('user', JSON.stringify(user));
        })
      ),
    { dispatch: false }
  );

  logout$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.logout),
        tap(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          this.router.navigate(['/']);
        })
      ),
    { dispatch: false }
  );

  navigateOnLogin$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.loginSuccess, AuthActions.registerSuccess),
        tap(() => {
          this.router.navigate(['/']);
        })
      ),
    { dispatch: false }
  );

  constructor(
    private actions$: Actions,
    private http: HttpClient,
    private router: Router
  ) {}
}
