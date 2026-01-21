/**
 * Home Component
 * 
 * Landing page with navigation links to main features.
 */

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <div class="home-container">
      <div class="header">
        <h1>Trade Management System</h1>
        <p class="subtitle">Manage financial trades with ease</p>
      </div>

      <div class="cards-container">
        <mat-card class="feature-card">
          <mat-card-header>
            <div class="card-icon">
              <mat-icon>add_circle</mat-icon>
            </div>
            <mat-card-title>Create New Trade</mat-card-title>
            <mat-card-subtitle>Start a new trade from template</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <p>Create new trades by selecting a trade type and filling in the required details.</p>
            <ul>
              <li>Interest Rate Swaps</li>
              <li>Commodity Options</li>
              <li>Index Swaps</li>
            </ul>
          </mat-card-content>
          <mat-card-actions>
            <a mat-raised-button color="primary" routerLink="/trades/new">
              <mat-icon>add</mat-icon>
              Create Trade
            </a>
          </mat-card-actions>
        </mat-card>

        <mat-card class="feature-card">
          <mat-card-header>
            <div class="card-icon">
              <mat-icon>list</mat-icon>
            </div>
            <mat-card-title>View Trade List</mat-card-title>
            <mat-card-subtitle>Browse and manage existing trades</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <p>View, filter, and manage all your trades in one place.</p>
            <ul>
              <li>Filter by trade type</li>
              <li>Search by counterparty</li>
              <li>View trade details</li>
            </ul>
          </mat-card-content>
          <mat-card-actions>
            <a mat-raised-button color="accent" routerLink="/trades">
              <mat-icon>list</mat-icon>
              View Trades
            </a>
          </mat-card-actions>
        </mat-card>

        <mat-card class="feature-card demo-card">
          <mat-card-header>
            <div class="card-icon demo-icon">
              <mat-icon>widgets</mat-icon>
            </div>
            <mat-card-title>UI Capabilities Demo</mat-card-title>
            <mat-card-subtitle>Explore advanced UI components</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <p>Interactive demonstration of advanced UI patterns and components.</p>
            <ul>
              <li>Docked slide-out panels</li>
              <li>Multiple panel coordination</li>
              <li>Vertical title strips</li>
            </ul>
          </mat-card-content>
          <mat-card-actions>
            <a mat-raised-button routerLink="/demo/panels">
              <mat-icon>play_arrow</mat-icon>
              View Demo
            </a>
          </mat-card-actions>
        </mat-card>
      </div>

      <div class="info-section">
        <mat-card class="info-card">
          <mat-card-content>
            <div class="info-item">
              <mat-icon>check_circle</mat-icon>
              <span>Real-time validation</span>
            </div>
            <div class="info-item">
              <mat-icon>check_circle</mat-icon>
              <span>Schedule management</span>
            </div>
            <div class="info-item">
              <mat-icon>check_circle</mat-icon>
              <span>Auto-save functionality</span>
            </div>
            <div class="info-item">
              <mat-icon>check_circle</mat-icon>
              <span>Comprehensive validation</span>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .home-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px;
    }

    .header {
      text-align: center;
      margin-bottom: 48px;
    }

    .header h1 {
      font-size: 2.5rem;
      font-weight: 500;
      color: #1976d2;
      margin: 0 0 16px 0;
    }

    .subtitle {
      font-size: 1.25rem;
      color: rgba(0, 0, 0, 0.6);
      margin: 0;
    }

    .cards-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 32px;
      margin-bottom: 48px;
    }

    .feature-card {
      display: flex;
      flex-direction: column;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .feature-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }

    .feature-card mat-card-header {
      padding: 24px 24px 16px 24px;
    }

    .card-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background-color: #e3f2fd;
      margin-bottom: 16px;
    }

    .card-icon mat-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
      color: #1976d2;
    }

    .feature-card mat-card-title {
      font-size: 1.5rem;
      font-weight: 500;
      margin-bottom: 8px;
    }

    .feature-card mat-card-subtitle {
      font-size: 1rem;
      color: rgba(0, 0, 0, 0.6);
    }

    .feature-card mat-card-content {
      padding: 16px 24px;
      flex: 1;
    }

    .feature-card mat-card-content p {
      margin: 0 0 16px 0;
      color: rgba(0, 0, 0, 0.87);
      line-height: 1.6;
    }

    .feature-card mat-card-content ul {
      margin: 0;
      padding-left: 20px;
      color: rgba(0, 0, 0, 0.6);
    }

    .feature-card mat-card-content li {
      margin-bottom: 8px;
      line-height: 1.5;
    }

    .feature-card mat-card-actions {
      padding: 16px 24px 24px 24px;
    }

    .feature-card mat-card-actions a {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .info-section {
      margin-top: 48px;
    }

    .info-card {
      background-color: #f5f5f5;
    }

    .info-card mat-card-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 24px;
      padding: 32px;
    }

    .info-item {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .info-item mat-icon {
      color: #4caf50;
      font-size: 24px;
      width: 24px;
      height: 24px;
    }

    .info-item span {
      font-size: 1rem;
      color: rgba(0, 0, 0, 0.87);
    }

    /* Demo card styling */
    .demo-card {
      border: 2px solid #9c27b0;
    }

    .demo-icon {
      background-color: #f3e5f5 !important;
    }

    .demo-icon mat-icon {
      color: #9c27b0 !important;
    }

    @media (max-width: 768px) {
      .header h1 {
        font-size: 2rem;
      }

      .subtitle {
        font-size: 1rem;
      }

      .cards-container {
        grid-template-columns: 1fr;
        gap: 24px;
      }

      .info-card mat-card-content {
        grid-template-columns: 1fr;
        gap: 16px;
        padding: 24px;
      }
    }
  `]
})
export class HomeComponent {
}
