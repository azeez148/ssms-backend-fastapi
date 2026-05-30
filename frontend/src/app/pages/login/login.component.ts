import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import * as AuthActions from '../../store/auth/auth.actions';
import { selectAuthLoading, selectAuthError } from '../../store/auth/auth.selectors';

@Component({
  selector: 'app-login',
  standalone: false,
  template: `
    <div class="page-wrap">
      <mat-card class="auth-card">
        <mat-card-content>
          <h1 class="auth-title">Welcome Back</h1>
          <p class="auth-sub">Sign in to your account</p>

          <mat-error *ngIf="error" class="error-alert">{{ error }}</mat-error>

          <form [formGroup]="form" (ngSubmit)="onSubmit()">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Mobile Number</mat-label>
              <input matInput formControlName="mobile" type="tel" />
              <mat-error *ngIf="form.get('mobile')?.hasError('required')">Mobile number is required</mat-error>
              <mat-error *ngIf="form.get('mobile')?.hasError('pattern')">Enter a valid 10-digit mobile number</mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Password</mat-label>
              <input matInput formControlName="password" [type]="showPwd ? 'text' : 'password'" />
              <button matSuffix mat-icon-button type="button" (click)="showPwd = !showPwd">
                <mat-icon>{{ showPwd ? 'visibility_off' : 'visibility' }}</mat-icon>
              </button>
              <mat-error *ngIf="form.get('password')?.invalid">Password required</mat-error>
            </mat-form-field>

            <button
              mat-raised-button
              color="primary"
              type="submit"
              class="full-width submit-btn"
              [disabled]="loading || form.invalid"
            >
              {{ loading ? 'Signing in...' : 'Sign In' }}
            </button>
          </form>

          <p class="auth-footer">
            Don't have an account?
            <a routerLink="/register">Register</a>
          </p>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .page-wrap { display: flex; justify-content: center; padding: 64px 24px; }
    .auth-card { width: 100%; max-width: 440px; padding: 16px; }
    .auth-title { font-size: 1.75rem; font-weight: 700; text-align: center; margin: 0 0 8px; }
    .auth-sub { color: #666; text-align: center; margin: 0 0 24px; }
    .full-width { width: 100%; }
    .submit-btn { margin-top: 16px; padding: 12px; }
    .auth-footer { text-align: center; margin-top: 16px; }
    .error-alert { display: block; padding: 12px; background: #fde8e8; border-radius: 4px; margin-bottom: 16px; }
    mat-form-field { margin-bottom: 8px; }
  `],
})
export class LoginComponent implements OnInit, OnDestroy {
  form: FormGroup;
  loading = false;
  error = '';
  showPwd = false;
  private destroy$ = new Subject<void>();

  constructor(private fb: FormBuilder, private store: Store) {
    this.form = this.fb.group({
      mobile: ['', [Validators.required, Validators.pattern(/^[6-9][0-9]{9}$/)]],
      password: ['', Validators.required],
    });
  }

  ngOnInit(): void {
    this.store.select(selectAuthLoading).pipe(takeUntil(this.destroy$))
      .subscribe((loading) => (this.loading = loading));
    this.store.select(selectAuthError).pipe(takeUntil(this.destroy$))
      .subscribe((error) => (this.error = error || ''));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    const { mobile, password } = this.form.value;
    this.store.dispatch(AuthActions.login({ mobile, password }));
  }
}
