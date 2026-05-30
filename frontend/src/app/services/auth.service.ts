import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { UserProfile, AuthResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly baseUrl = environment.apiUrl;
  private userSubject = new BehaviorSubject<UserProfile | null>(this.loadUser());
  private tokenSubject = new BehaviorSubject<string | null>(localStorage.getItem('token'));

  user$ = this.userSubject.asObservable();
  token$ = this.tokenSubject.asObservable();

  get currentUser(): UserProfile | null {
    return this.userSubject.value;
  }

  get isAuthenticated(): boolean {
    return !!this.tokenSubject.value && !!this.userSubject.value;
  }

  constructor(private http: HttpClient, private router: Router) {}

  private loadUser(): UserProfile | null {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  }

  login(mobile: string, password: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.baseUrl}/auth/login`, { mobile, password })
      .pipe(tap((res) => this.storeSession(res)));
  }

  register(data: {
    mobile: string;
    password: string;
    first_name: string;
    last_name: string;
    address: string;
    city: string;
    state: string;
    zip_code: string;
    email?: string;
  }): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.baseUrl}/auth/register`, data)
      .pipe(tap((res) => this.storeSession(res)));
  }

  getStatus(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.baseUrl}/auth/status`);
  }

  getProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.baseUrl}/auth/profile`);
  }

  updateProfile(data: Partial<UserProfile>): Observable<UserProfile> {
    return this.http
      .put<UserProfile>(`${this.baseUrl}/auth/profile`, data)
      .pipe(
        tap((updated) => {
          this.userSubject.next(updated);
          localStorage.setItem('user', JSON.stringify(updated));
        })
      );
  }

  logout(): void {
    this.userSubject.next(null);
    this.tokenSubject.next(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.router.navigate(['/']);
  }

  private storeSession(res: AuthResponse): void {
    this.tokenSubject.next(res.token);
    this.userSubject.next(res.user);
    localStorage.setItem('token', res.token);
    localStorage.setItem('user', JSON.stringify(res.user));
  }
}
