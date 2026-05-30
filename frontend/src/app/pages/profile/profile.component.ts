import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { selectUser, selectAuthLoading, selectAuthError } from '../../store/auth/auth.selectors';
import * as AuthActions from '../../store/auth/auth.actions';
import { UserProfile } from '../../models';

@Component({
  selector: 'app-profile',
  standalone: false,
  template: `
    <div class="page-wrap">
      <mat-card class="profile-card" *ngIf="user">
        <mat-card-content>
          <div class="avatar-section">
            <div class="avatar">
              <mat-icon>person</mat-icon>
            </div>
            <h2 class="user-name">{{ user.first_name }} {{ user.last_name }}</h2>
            <p class="user-info">{{ user.mobile }}{{ user.email ? ' | ' + user.email : '' }}</p>
          </div>

          <mat-divider class="divider"></mat-divider>

          <mat-error *ngIf="error" class="alert error-alert">{{ error }}</mat-error>
          <div *ngIf="success" class="alert success-alert">{{ success }}</div>

          <form [formGroup]="form">
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
          </form>

          <div class="actions">
            <ng-container *ngIf="editing; else viewMode">
              <button mat-button (click)="cancelEdit()">Cancel</button>
              <button mat-raised-button color="primary" (click)="save()">Save Changes</button>
            </ng-container>
            <ng-template #viewMode>
              <button mat-stroked-button color="warn" (click)="logout()">Logout</button>
              <button mat-raised-button color="primary" (click)="startEdit()">Edit Profile</button>
            </ng-template>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .page-wrap { display: flex; justify-content: center; padding: 32px 24px; }
    .profile-card { width: 100%; max-width: 520px; padding: 16px; }
    .avatar-section { text-align: center; margin-bottom: 24px; }
    .avatar { width: 80px; height: 80px; border-radius: 50%; background: #1a237e; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
    .avatar mat-icon { font-size: 40px; width: 40px; height: 40px; }
    .user-name { font-size: 1.4rem; font-weight: 700; margin: 0 0 4px; }
    .user-info { color: #666; margin: 0; }
    .divider { margin: 16px 0 24px; }
    .full-width { width: 100%; }
    .name-row, .city-row { display: flex; gap: 16px; flex-wrap: wrap; }
    .name-row mat-form-field, .city-row mat-form-field { flex: 1; min-width: 120px; }
    .actions { display: flex; justify-content: space-between; margin-top: 16px; }
    .alert { display: block; padding: 12px; border-radius: 4px; margin-bottom: 16px; }
    .error-alert { background: #fde8e8; }
    .success-alert { background: #e8f5e9; color: #2e7d32; }
  `],
})
export class ProfileComponent implements OnInit {
  user: UserProfile | null = null;
  form: FormGroup;
  editing = false;
  success = '';
  error = '';

  constructor(private store: Store, private fb: FormBuilder, private router: Router) {
    this.form = this.fb.group({
      first_name: [{ value: '', disabled: true }],
      last_name: [{ value: '', disabled: true }],
      address: [{ value: '', disabled: true }],
      city: [{ value: '', disabled: true }],
      state: [{ value: '', disabled: true }],
      zip_code: [{ value: '', disabled: true }],
    });
  }

  ngOnInit(): void {
    // Dispatch loadProfile to fetch fresh data from API
    this.store.dispatch(AuthActions.loadProfile());

    this.store.select(selectUser).subscribe((user) => {
      if (!user) { this.router.navigate(['/login']); return; }
      this.user = user;
      this.form.patchValue({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        address: user.address || '',
        city: user.city || '',
        state: user.state || '',
        zip_code: user.zip_code || '',
      });
    });

    this.store.select(selectAuthError).subscribe((err) => {
      if (err) this.error = err;
    });
  }

  startEdit(): void {
    this.editing = true;
    this.form.enable();
    this.success = '';
    this.error = '';
  }

  cancelEdit(): void {
    this.editing = false;
    this.form.disable();
    if (this.user) {
      this.form.patchValue({
        first_name: this.user.first_name || '',
        last_name: this.user.last_name || '',
        address: this.user.address || '',
        city: this.user.city || '',
        state: this.user.state || '',
        zip_code: this.user.zip_code || '',
      });
    }
  }

  save(): void {
    this.store.dispatch(AuthActions.updateProfile({ data: this.form.value }));
    this.store.select(selectAuthLoading).subscribe((loading) => {
      if (!loading && !this.error) {
        this.success = 'Profile updated successfully!';
        this.editing = false;
        this.form.disable();
      }
    });
  }

  logout(): void {
    this.store.dispatch(AuthActions.logout());
  }
}
