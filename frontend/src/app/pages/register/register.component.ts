import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

function passwordsMatch(group: AbstractControl): ValidationErrors | null {
  const pw = group.get('password')?.value;
  const confirm = group.get('confirmPassword')?.value;
  return pw === confirm ? null : { passwordsMismatch: true };
}

@Component({
  selector: 'app-register',
  standalone: false,
  template: `
    <div class="page-wrap">
      <mat-card class="auth-card">
        <mat-card-content>
          <h1 class="auth-title">Create Account</h1>
          <p class="auth-sub">Join Adrenaline Store today</p>

          <mat-error *ngIf="error" class="error-alert">{{ error }}</mat-error>

          <form [formGroup]="form" (ngSubmit)="onSubmit()">
            <div class="name-row">
              <mat-form-field appearance="outline">
                <mat-label>First Name</mat-label>
                <input matInput formControlName="first_name" />
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Last Name</mat-label>
                <input matInput formControlName="last_name" />
              </mat-form-field>
            </div>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Mobile Number</mat-label>
              <input matInput formControlName="mobile" type="tel" />
              <mat-error *ngIf="form.get('mobile')?.invalid">Valid mobile number required (min 10 digits)</mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Email (optional)</mat-label>
              <input matInput formControlName="email" type="email" />
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Password</mat-label>
              <input matInput formControlName="password" [type]="showPwd ? 'text' : 'password'" />
              <button matSuffix mat-icon-button type="button" (click)="showPwd = !showPwd">
                <mat-icon>{{ showPwd ? 'visibility_off' : 'visibility' }}</mat-icon>
              </button>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Confirm Password</mat-label>
              <input matInput formControlName="confirmPassword" [type]="showPwd ? 'text' : 'password'" />
              <mat-error *ngIf="form.hasError('passwordsMismatch')">Passwords do not match</mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Address</mat-label>
              <textarea matInput rows="2" formControlName="address"></textarea>
            </mat-form-field>

            <div class="city-row">
              <mat-form-field appearance="outline">
                <mat-label>City</mat-label>
                <input matInput formControlName="city" />
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>State</mat-label>
                <input matInput formControlName="state" />
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>ZIP Code</mat-label>
                <input matInput formControlName="zip_code" />
              </mat-form-field>
            </div>

            <button
              mat-raised-button
              color="primary"
              type="submit"
              class="full-width submit-btn"
              [disabled]="loading || form.invalid"
            >
              {{ loading ? 'Creating Account...' : 'Register' }}
            </button>
          </form>

          <p class="auth-footer">
            Already have an account? <a routerLink="/login">Sign In</a>
          </p>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .page-wrap { display: flex; justify-content: center; padding: 32px 24px; }
    .auth-card { width: 100%; max-width: 520px; padding: 16px; }
    .auth-title { font-size: 1.75rem; font-weight: 700; text-align: center; margin: 0 0 8px; }
    .auth-sub { color: #666; text-align: center; margin: 0 0 24px; }
    .full-width { width: 100%; }
    .name-row, .city-row { display: flex; gap: 16px; flex-wrap: wrap; }
    .name-row mat-form-field, .city-row mat-form-field { flex: 1; min-width: 120px; }
    .submit-btn { margin-top: 16px; padding: 12px; }
    .auth-footer { text-align: center; margin-top: 16px; }
    .error-alert { display: block; padding: 12px; background: #fde8e8; border-radius: 4px; margin-bottom: 16px; }
  `],
})
export class RegisterComponent {
  form: FormGroup;
  loading = false;
  error = '';
  showPwd = false;

  constructor(private fb: FormBuilder, private auth: AuthService, private router: Router) {
    this.form = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      mobile: ['', [Validators.required, Validators.minLength(10)]],
      email: [''],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required],
      address: ['', Validators.required],
      city: ['', Validators.required],
      state: ['', Validators.required],
      zip_code: ['', Validators.required],
    }, { validators: passwordsMatch });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.error = '';
    this.loading = true;
    const { confirmPassword, ...data } = this.form.value;

    this.auth.register(data).subscribe({
      next: () => { this.router.navigate(['/']); },
      error: (err) => {
        this.error = err.error?.detail || 'Registration failed. Please try again.';
        this.loading = false;
      },
    });
  }
}
