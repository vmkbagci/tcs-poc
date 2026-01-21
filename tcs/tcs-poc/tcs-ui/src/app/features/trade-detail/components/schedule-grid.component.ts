/**
 * Schedule Grid Component
 * 
 * Presentational component for displaying schedule periods in a grid format.
 * Shows fixed columns: periodIndex, startDate, endDate, paymentDate, notional, rate, interest
 * Supports sorting, row selection, and edit/delete actions.
 * 
 * Requirements:
 * - 4.3: Display schedule in data grid
 * - 4.4: Dynamic column generation
 * - 5.1, 5.2: Column detection from schedule data
 * - 5.3: Date formatting
 * - 5.4: Numeric formatting
 * - 5.5: Column sorting
 */

import { Component, Input, Output, EventEmitter, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { SchedulePeriod } from '@core/models';
import { DateFormatPipe } from '@shared/pipes/date-format.pipe';
import { CurrencyFormatPipe } from '@shared/pipes/currency-format.pipe';
import { SchedulePeriodDetailComponent, SchedulePeriodDetailData } from './schedule-period-detail.component';

@Component({
  selector: 'app-schedule-grid',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatSortModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatDialogModule,
    DateFormatPipe,
    CurrencyFormatPipe
  ],
  template: `
    <div class="schedule-grid-container">
      <!-- Header with Add Button -->
      @if (editable()) {
        <div class="grid-header">
          <button 
            mat-raised-button 
            color="primary"
            (click)="onAddPeriod()"
            class="add-button">
            <mat-icon>add</mat-icon>
            Add Schedule Period
          </button>
        </div>
      }

      <!-- Schedule Table -->
      @if (schedule().length > 0) {
        <div class="table-container">
          <table 
            mat-table 
            [dataSource]="sortedSchedule()" 
            matSort
            (matSortChange)="onSortChange($event)"
            class="schedule-table">

            <!-- Period Index Column -->
            <ng-container matColumnDef="periodIndex">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Period</th>
              <td mat-cell *matCellDef="let period">{{ period.periodIndex }}</td>
            </ng-container>

            <!-- Start Date Column -->
            <ng-container matColumnDef="startDate">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Start Date</th>
              <td mat-cell *matCellDef="let period">
                {{ period.startDate | dateFormat:'short' }}
              </td>
            </ng-container>

            <!-- End Date Column -->
            <ng-container matColumnDef="endDate">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>End Date</th>
              <td mat-cell *matCellDef="let period">
                {{ period.endDate | dateFormat:'short' }}
              </td>
            </ng-container>

            <!-- Payment Date Column -->
            <ng-container matColumnDef="paymentDate">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Payment Date</th>
              <td mat-cell *matCellDef="let period">
                {{ period.paymentDate | dateFormat:'short' }}
              </td>
            </ng-container>

            <!-- Notional Column -->
            <ng-container matColumnDef="notional">
              <th mat-header-cell *matHeaderCellDef mat-sort-header class="numeric-column">Notional</th>
              <td mat-cell *matCellDef="let period" class="numeric-cell">
                {{ period.notional | currencyFormat:'number':'USD':2 }}
              </td>
            </ng-container>

            <!-- Rate Column -->
            <ng-container matColumnDef="rate">
              <th mat-header-cell *matHeaderCellDef mat-sort-header class="numeric-column">Rate (%)</th>
              <td mat-cell *matCellDef="let period" class="numeric-cell">
                {{ period.rate | currencyFormat:'number':'USD':4 }}
              </td>
            </ng-container>

            <!-- Interest Column -->
            <ng-container matColumnDef="interest">
              <th mat-header-cell *matHeaderCellDef mat-sort-header class="numeric-column">Interest</th>
              <td mat-cell *matCellDef="let period" class="numeric-cell">
                {{ period.interest | currencyFormat:'number':'USD':2 }}
              </td>
            </ng-container>

            <!-- Actions Column -->
            @if (editable()) {
              <ng-container matColumnDef="actions">
                <th mat-header-cell *matHeaderCellDef class="actions-column">Actions</th>
                <td mat-cell *matCellDef="let period; let i = index" class="actions-cell">
                  <button 
                    mat-icon-button 
                    color="warn"
                    (click)="onDeletePeriod(i); $event.stopPropagation()"
                    matTooltip="Delete period"
                    class="delete-button">
                    <mat-icon>delete</mat-icon>
                  </button>
                </td>
              </ng-container>
            }

            <!-- Table Header and Rows -->
            <tr mat-header-row *matHeaderRowDef="displayedColumns()"></tr>
            <tr 
              mat-row 
              *matRowDef="let row; columns: displayedColumns();"
              (click)="onRowClick(row)"
              class="schedule-row"
              [class.clickable]="true">
            </tr>
          </table>
        </div>
      } @else {
        <div class="no-data">
          <mat-icon>info</mat-icon>
          <p>No schedule periods available</p>
          @if (editable()) {
            <p class="hint">Click "Add Schedule Period" to create a new period</p>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .schedule-grid-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
      width: 100%;
    }

    .grid-header {
      display: flex;
      justify-content: flex-start;
      align-items: center;
      padding: 8px 0;
    }

    .add-button {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .table-container {
      overflow-x: auto;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
    }

    .schedule-table {
      width: 100%;
      background-color: white;

      th {
        background-color: #f5f5f5;
        font-weight: 600;
        color: rgba(0, 0, 0, 0.87);
        padding: 12px 16px;
      }

      td {
        padding: 12px 16px;
        color: rgba(0, 0, 0, 0.87);
      }

      .numeric-column {
        text-align: right;
      }

      .numeric-cell {
        text-align: right;
        font-family: 'Roboto Mono', monospace;
      }

      .actions-column {
        width: 80px;
        text-align: center;
      }

      .actions-cell {
        text-align: center;
      }
    }

    .schedule-row {
      &.clickable {
        cursor: pointer;
        transition: background-color 0.2s;

        &:hover {
          background-color: #f5f5f5;
        }
      }
    }

    .delete-button {
      &:hover {
        background-color: rgba(244, 67, 54, 0.1);
      }
    }

    .no-data {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 24px;
      text-align: center;
      background-color: #fafafa;
      border: 1px dashed #ccc;
      border-radius: 4px;

      mat-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        color: rgba(0, 0, 0, 0.38);
        margin-bottom: 16px;
      }

      p {
        margin: 4px 0;
        color: rgba(0, 0, 0, 0.6);
        font-size: 14px;

        &.hint {
          font-size: 13px;
          font-style: italic;
          color: rgba(0, 0, 0, 0.5);
        }
      }
    }

    // Responsive adjustments
    @media (max-width: 768px) {
      .schedule-table {
        font-size: 12px;

        th, td {
          padding: 8px 12px;
        }
      }
    }
  `]
})
export class ScheduleGridComponent {
  private dialog = inject(MatDialog);

  // ============================================================================
  // Inputs & Outputs
  // ============================================================================

  /**
   * Schedule data to display
   */
  @Input() set scheduleData(value: SchedulePeriod[]) {
    this.schedule.set(value || []);
  }

  /**
   * Whether the grid is in edit mode
   */
  @Input() set isEditable(value: boolean) {
    this.editable.set(value);
  }

  /**
   * Event emitted when a row is clicked
   */
  @Output() rowClick = new EventEmitter<SchedulePeriod>();

  /**
   * Event emitted when schedule data changes
   */
  @Output() scheduleChange = new EventEmitter<SchedulePeriod[]>();

  /**
   * Event emitted when add period is clicked
   */
  @Output() addPeriod = new EventEmitter<void>();

  /**
   * Event emitted when delete period is clicked
   */
  @Output() deletePeriod = new EventEmitter<number>();

  // ============================================================================
  // Signals
  // ============================================================================

  /**
   * Schedule data signal
   */
  schedule = signal<SchedulePeriod[]>([]);

  /**
   * Editable mode signal
   */
  editable = signal<boolean>(false);

  /**
   * Current sort state
   */
  sortState = signal<Sort>({ active: '', direction: '' });

  /**
   * Displayed columns (includes actions if editable)
   */
  displayedColumns = computed(() => {
    const baseColumns = [
      'periodIndex',
      'startDate',
      'endDate',
      'paymentDate',
      'notional',
      'rate',
      'interest'
    ];

    return this.editable() ? [...baseColumns, 'actions'] : baseColumns;
  });

  /**
   * Sorted schedule data
   */
  sortedSchedule = computed(() => {
    const data = [...this.schedule()];
    const sort = this.sortState();

    if (!sort.active || sort.direction === '') {
      return data;
    }

    return data.sort((a, b) => {
      const aValue = this.getPropertyValue(a, sort.active);
      const bValue = this.getPropertyValue(b, sort.active);

      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      const comparison = this.compare(aValue, bValue);
      return sort.direction === 'asc' ? comparison : -comparison;
    });
  });

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle row click - opens detail dialog
   */
  onRowClick(period: SchedulePeriod): void {
    const dialogData: SchedulePeriodDetailData = {
      period: period,
      editable: this.editable()
    };

    const dialogRef = this.dialog.open(SchedulePeriodDetailComponent, {
      width: '800px',
      maxWidth: '95vw',
      maxHeight: '90vh',
      data: dialogData,
      disableClose: false
    });

    dialogRef.afterClosed().subscribe((updatedPeriod: SchedulePeriod | undefined) => {
      if (updatedPeriod) {
        // Find and update the period in the schedule
        const currentSchedule = this.schedule();
        const updatedSchedule = currentSchedule.map(p => 
          p.periodIndex === updatedPeriod.periodIndex ? updatedPeriod : p
        );
        
        this.schedule.set(updatedSchedule);
        this.scheduleChange.emit(updatedSchedule);
      }
    });

    this.rowClick.emit(period);
  }

  /**
   * Handle sort change
   */
  onSortChange(sort: Sort): void {
    this.sortState.set(sort);
  }

  /**
   * Handle add period button click
   */
  onAddPeriod(): void {
    const currentSchedule = this.schedule();
    const newPeriodIndex = currentSchedule.length;
    
    // Create new empty schedule period with default values
    const newPeriod: SchedulePeriod = {
      periodIndex: newPeriodIndex,
      startDate: '',
      endDate: '',
      paymentDate: '',
      rate: 0,
      notional: 0,
      interest: 0
    };

    // Add to schedule array
    const updatedSchedule = [...currentSchedule, newPeriod];
    this.schedule.set(updatedSchedule);
    
    // Emit changes to parent
    this.scheduleChange.emit(updatedSchedule);
    this.addPeriod.emit();
  }

  /**
   * Handle delete period button click
   */
  onDeletePeriod(index: number): void {
    const currentSchedule = this.schedule();
    
    // Remove period from array
    const updatedSchedule = currentSchedule.filter((_, i) => i !== index);
    
    // Update period indices after deletion
    const reindexedSchedule = updatedSchedule.map((period, i) => ({
      ...period,
      periodIndex: i
    }));
    
    this.schedule.set(reindexedSchedule);
    
    // Emit changes to parent
    this.scheduleChange.emit(reindexedSchedule);
    this.deletePeriod.emit(index);
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  /**
   * Get property value from object
   */
  private getPropertyValue(obj: any, property: string): any {
    return obj[property];
  }

  /**
   * Compare two values for sorting
   */
  private compare(a: any, b: any): number {
    // Handle dates
    if (this.isDateString(a) && this.isDateString(b)) {
      return new Date(a).getTime() - new Date(b).getTime();
    }

    // Handle numbers
    if (typeof a === 'number' && typeof b === 'number') {
      return a - b;
    }

    // Handle strings
    if (typeof a === 'string' && typeof b === 'string') {
      return a.localeCompare(b);
    }

    // Default comparison
    return String(a).localeCompare(String(b));
  }

  /**
   * Check if string is a date
   */
  private isDateString(value: any): boolean {
    if (typeof value !== 'string') {
      return false;
    }

    // Check for ISO date format (YYYY-MM-DD)
    const isoDatePattern = /^\d{4}-\d{2}-\d{2}/;
    return isoDatePattern.test(value);
  }
}
