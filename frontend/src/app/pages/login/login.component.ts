import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

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
              <mat-error *ngIf="form.get('mobile')?.invalid">Valid mobile number required</mat-error>
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
export class LoginComponent {
  form: FormGroup;
  loading = false;
  error = '';
  showPwd = false;

  constructor(private fb: FormBuilder, private auth: AuthService, private router: Router) {
    this.form = this.fb.group({
      mobile: ['', [Validators.required, Validators.minLength(10)]],
      password: ['', Validators.required],
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.error = '';
    this.loading = true;
    const { mobile, password } = this.form.value;

    this.auth.login(mobile, password).subscribe({
      next: () => { this.router.navigate(['/']); },
      error: (err) => {
        this.error = err.error?.detail || 'Login failed. Please check your credentials.';
        this.loading = false;
      },
    });
  }
}
