/**
 * Docked Panel Demo Component
 * 
 * Demonstrates multiple docked slide-out panels on the same view.
 * Shows different configurations and use cases.
 * 
 * This demo includes:
 * - 2 panels on the right side with different sizes
 * - 1 panel on the left side
 * - Different content types
 * - Controlled and uncontrolled modes
 */

import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { DockedSlideOutPanelComponent } from './docked-slide-out-panel.component';
import { DockedPanelHostComponent } from './docked-panel-host.component';

@Component({
  selector: 'app-docked-panel-demo',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatDividerModule,
    DockedSlideOutPanelComponent,
    DockedPanelHostComponent
  ],
  template: `
    <div class="demo-container">
      <!-- Main Content Area -->
      <div class="demo-content">
        <mat-card>
          <mat-card-header>
            <mat-card-title>Docked Slide-Out Panel Demo</mat-card-title>
            <mat-card-subtitle>Multiple independent panels on the same view</mat-card-subtitle>
          </mat-card-header>
          
          <mat-card-content>
            <h3>Features Demonstrated:</h3>
            <ul>
              <li>✅ Persistent vertical title strips when collapsed</li>
              <li>✅ Multiple panels on same view (left and right sides)</li>
              <li>✅ Independent collapse/expand (no auto-close)</li>
              <li>✅ Configurable size (width/height ratios)</li>
              <li>✅ Smooth slide animations</li>
              <li>✅ Controlled and uncontrolled modes</li>
              <li>✅ Click title strip to toggle (configurable)</li>
            </ul>

            <mat-divider style="margin: 24px 0;"></mat-divider>

            <h3>Panel Controls:</h3>
            <div class="button-group">
              <button mat-raised-button color="primary" (click)="togglePanel1()">
                <mat-icon>{{ panel1Collapsed() ? 'open_in_new' : 'close' }}</mat-icon>
                {{ panel1Collapsed() ? 'Open' : 'Close' }} Settings Panel
              </button>
              
              <button mat-raised-button color="accent" (click)="togglePanel2()">
                <mat-icon>{{ panel2Collapsed() ? 'open_in_new' : 'close' }}</mat-icon>
                {{ panel2Collapsed() ? 'Open' : 'Close' }} Validation Panel
              </button>
              
              <button mat-raised-button (click)="togglePanel3()">
                <mat-icon>{{ panel3Collapsed() ? 'open_in_new' : 'close' }}</mat-icon>
                {{ panel3Collapsed() ? 'Open' : 'Close' }} Navigation Panel
              </button>
            </div>

            <mat-divider style="margin: 24px 0;"></mat-divider>

            <h3>Instructions:</h3>
            <p>
              Look at the edges of the viewport. You'll see vertical title strips for each panel.
              Click the arrow or title strip to expand/collapse panels.
            </p>
            <p>
              <strong>Right side:</strong> Settings (small) and Validation (large) panels<br>
              <strong>Left side:</strong> Navigation panel
            </p>
          </mat-card-content>
        </mat-card>
      </div>

      <!-- Panel Host with Multiple Panels -->
      <app-docked-panel-host>
        
        <!-- Panel 1: Settings (Right, Small) -->
        <app-docked-slide-out-panel
          id="settings-panel"
          title="Settings"
          side="right"
          [widthRatio]="0.3"
          [heightRatio]="0.4"
          [collapsed]="panel1Collapsed()"
          (collapsedChange)="panel1Collapsed.set($event)"
          [zIndex]="1001">
          
          <div panel-content class="panel-content">
            <div class="panel-header">
              <h2>Settings</h2>
              <p class="subtitle">Configure your preferences</p>
            </div>
            
            <div class="panel-body">
              <div class="setting-item">
                <h4>Theme</h4>
                <p>Light mode</p>
              </div>
              
              <div class="setting-item">
                <h4>Language</h4>
                <p>English</p>
              </div>
              
              <div class="setting-item">
                <h4>Notifications</h4>
                <p>Enabled</p>
              </div>
              
              <div class="setting-item">
                <h4>Auto-save</h4>
                <p>Every 5 minutes</p>
              </div>
            </div>
          </div>
        </app-docked-slide-out-panel>

        <!-- Panel 2: Validation Response (Right, Large) -->
        <app-docked-slide-out-panel
          id="validation-panel"
          title="Validation Response"
          side="right"
          [widthRatio]="0.5"
          [heightRatio]="0.8"
          [collapsed]="panel2Collapsed()"
          (collapsedChange)="panel2Collapsed.set($event)"
          [zIndex]="1002">
          
          <div panel-content class="panel-content">
            <div class="panel-header">
              <h2>API Validation Response</h2>
              <p class="subtitle">Last validated: {{ currentTime }}</p>
            </div>
            
            <div class="panel-body">
              <pre class="json-response">{{
                sampleValidationResponse | json
              }}</pre>
            </div>
          </div>
        </app-docked-slide-out-panel>

        <!-- Panel 3: Navigation (Left, Medium) -->
        <app-docked-slide-out-panel
          id="navigation-panel"
          title="Navigation"
          side="left"
          [widthRatio]="0.35"
          [heightRatio]="0.6"
          [collapsed]="panel3Collapsed()"
          (collapsedChange)="panel3Collapsed.set($event)"
          [zIndex]="1000">
          
          <div panel-content class="panel-content">
            <div class="panel-header">
              <h2>Navigation</h2>
              <p class="subtitle">Quick links</p>
            </div>
            
            <div class="panel-body">
              <nav class="nav-menu">
                <a href="#" class="nav-item">
                  <mat-icon>home</mat-icon>
                  <span>Home</span>
                </a>
                <a href="#" class="nav-item">
                  <mat-icon>dashboard</mat-icon>
                  <span>Dashboard</span>
                </a>
                <a href="#" class="nav-item">
                  <mat-icon>list</mat-icon>
                  <span>Trades</span>
                </a>
                <a href="#" class="nav-item">
                  <mat-icon>analytics</mat-icon>
                  <span>Analytics</span>
                </a>
                <a href="#" class="nav-item">
                  <mat-icon>settings</mat-icon>
                  <span>Settings</span>
                </a>
                <a href="#" class="nav-item">
                  <mat-icon>help</mat-icon>
                  <span>Help</span>
                </a>
              </nav>
            </div>
          </div>
        </app-docked-slide-out-panel>

      </app-docked-panel-host>
    </div>
  `,
  styles: [`
    .demo-container {
      min-height: 100vh;
      background-color: #f5f5f5;
      padding: 40px;
    }

    .demo-content {
      max-width: 1200px;
      margin: 0 auto;
    }

    .button-group {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin: 16px 0;
    }

    /* Panel Content Styling */
    .panel-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      background-color: white;
    }

    .panel-header {
      padding: 24px;
      background-color: #e3f2fd;
      border-bottom: 2px solid #1976d2;
      flex-shrink: 0;
    }

    .panel-header h2 {
      margin: 0 0 8px 0;
      color: #1976d2;
      font-size: 20px;
      font-weight: 500;
    }

    .panel-header .subtitle {
      margin: 0;
      color: #666;
      font-size: 13px;
    }

    .panel-body {
      flex: 1;
      overflow: auto;
      padding: 24px;
    }

    /* Settings Panel Styling */
    .setting-item {
      padding: 16px 0;
      border-bottom: 1px solid #e0e0e0;
    }

    .setting-item:last-child {
      border-bottom: none;
    }

    .setting-item h4 {
      margin: 0 0 8px 0;
      font-size: 14px;
      font-weight: 500;
      color: #333;
    }

    .setting-item p {
      margin: 0;
      font-size: 13px;
      color: #666;
    }

    /* Validation Response Styling */
    .json-response {
      background-color: #263238;
      color: #aed581;
      padding: 20px;
      border-radius: 4px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 13px;
      line-height: 1.6;
      margin: 0;
      overflow-x: auto;
    }

    /* Navigation Menu Styling */
    .nav-menu {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 12px 16px;
      color: #333;
      text-decoration: none;
      border-radius: 4px;
      transition: background-color 0.2s ease;
    }

    .nav-item:hover {
      background-color: #f5f5f5;
    }

    .nav-item mat-icon {
      color: #1976d2;
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .nav-item span {
      font-size: 14px;
      font-weight: 500;
    }
  `]
})
export class DockedPanelDemoComponent {
  
  // ============================================================================
  // Panel State (Controlled Mode)
  // ============================================================================

  panel1Collapsed = signal<boolean>(true);
  panel2Collapsed = signal<boolean>(true);
  panel3Collapsed = signal<boolean>(true);

  // ============================================================================
  // Demo Data
  // ============================================================================

  currentTime = new Date().toLocaleString();

  sampleValidationResponse = {
    status: 'success',
    timestamp: new Date().toISOString(),
    validations: {
      tradeId: { valid: true, message: 'Valid trade ID' },
      counterparty: { valid: true, message: 'Valid counterparty' },
      amount: { valid: true, message: 'Amount within limits' },
      date: { valid: true, message: 'Valid trade date' }
    },
    warnings: [
      'Trade date is in the past',
      'Counterparty has high exposure'
    ],
    summary: {
      totalChecks: 12,
      passed: 12,
      failed: 0,
      warnings: 2
    }
  };

  // ============================================================================
  // Panel Controls
  // ============================================================================

  togglePanel1(): void {
    this.panel1Collapsed.update(collapsed => !collapsed);
  }

  togglePanel2(): void {
    this.panel2Collapsed.update(collapsed => !collapsed);
  }

  togglePanel3(): void {
    this.panel3Collapsed.update(collapsed => !collapsed);
  }
}
