import { Component, OnInit, Output, EventEmitter, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

import { TradeFilters, DateRange } from '@core/models/filter.model';
import { TradeType } from '@core/models/trade.model';

/**
 * Trade Filter Component
 * 
 * Provides filter controls for the trade list including:
 * - Trade type selection
 * - Date range picker
 * - Counterparty search
 * - Book search
 * 
 * Uses reactive forms and emits filter changes to parent component.
 */
@Component({
  selector: 'app-trade-filter',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatExpansionModule
  ],
  template: `
    <mat-expansion-panel [expanded]="expanded()" (opened)="expanded.set(true)" (closed)="expanded.set(false)">
      <mat-expansion-panel-header>
        <mat-panel-title>
          <mat-icon>filter_list</mat-icon>
          <span>Filters</span>
          <span class="filter-count" *ngIf="activeFilterCount() > 0">
            ({{ activeFilterCount() }} active)
          </span>
        </mat-panel-title>
      </mat-expansion-panel-header>

      <form [formGroup]="filterForm" class="filter-form">
        <div class="filter-row">
          <!-- Trade Type Filter -->
          <mat-form-field appearance="outline" class="filter-field">
            <mat-label>Trade Type</mat-label>
            <mat-select formControlName="tradeType">
              <mat-option [value]="null">All Types</mat-option>
              <mat-option value="ir-swap">IR Swap</mat-option>
              <mat-option value="commodity-option">Commodity Option</mat-option>
              <mat-option value="index-swap">Index Swap</mat-option>
            </mat-select>
            <mat-icon matSuffix>category</mat-icon>
          </mat-form-field>

          <!-- Book Filter -->
          <mat-form-field appearance="outline" class="filter-field">
            <mat-label>Book</mat-label>
            <input matInput formControlName="book" placeholder="Enter book name">
            <mat-icon matSuffix>book</mat-icon>
          </mat-form-field>

          <!-- Counterparty Filter -->
          <mat-form-field appearance="outline" class="filter-field">
            <mat-label>Counterparty</mat-label>
            <input matInput formControlName="counterparty" placeholder="Enter counterparty">
            <mat-icon matSuffix>business</mat-icon>
          </mat-form-field>
        </div>

        <div class="filter-row">
          <!-- Start Date Filter -->
          <mat-form-field appearance="outline" class="filter-field">
            <mat-label>Start Date</mat-label>
            <input matInput [matDatepicker]="startPicker" formControlName="startDate">
            <mat-datepicker-toggle matSuffix [for]="startPicker"></mat-datepicker-toggle>
            <mat-datepicker #startPicker></mat-datepicker>
          </mat-form-field>

          <!-- End Date Filter -->
          <mat-form-field appearance="outline" class="filter-field">
            <mat-label>End Date</mat-label>
            <input matInput [matDatepicker]="endPicker" formControlName="endDate">
            <mat-datepicker-toggle matSuffix [for]="endPicker"></mat-datepicker-toggle>
            <mat-datepicker #endPicker></mat-datepicker>
          </mat-form-field>

          <!-- Search Text Filter -->
          <mat-form-field appearance="outline" class="filter-field">
            <mat-label>Search</mat-label>
            <input matInput formControlName="searchText" placeholder="Search trades...">
            <mat-icon matSuffix>search</mat-icon>
          </mat-form-field>
        </div>

        <div class="filter-actions">
          <button 
            mat-raised-button 
            color="primary" 
            type="button"
            (click)="applyFilters()">
            <mat-icon>check</mat-icon>
            Apply Filters
          </button>
          <button 
            mat-button 
            type="button"
            (click)="clearFilters()">
            <mat-icon>clear</mat-icon>
            Clear All
          </button>
        </div>
      </form>
    </mat-expansion-panel>
  `,
  styles: [`
    mat-expansion-panel {
      margin-bottom: 0;
      box-shadow: none;
      border-bottom: 1px solid #e0e0e0;
    }

    mat-panel-title {
      display: flex;
      align-items: center;
      gap: 8px;
      
      mat-icon {
        color: rgba(0, 0, 0, 0.54);
      }
      
      .filter-count {
        color: #1976d2;
        font-weight: 500;
        margin-left: 4px;
      }
    }

    .filter-form {
      padding: 16px 0;
    }

    .filter-row {
      display: flex;
      gap: 16px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }

    .filter-field {
      flex: 1 1 200px;
      min-width: 200px;
    }

    .filter-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      margin-top: 8px;
      
      button {
        mat-icon {
          margin-right: 4px;
        }
      }
    }

    @media (max-width: 768px) {
      .filter-row {
        flex-direction: column;
      }
      
      .filter-field {
        width: 100%;
      }
      
      .filter-actions {
        flex-direction: column;
        
        button {
          width: 100%;
        }
      }
    }
  `]
})
export class TradeFilterComponent implements OnInit {
  private fb = inject(FormBuilder);

  /**
   * Event emitted when filters change
   */
  @Output() filterChange = new EventEmitter<TradeFilters>();

  /**
   * Whether the filter panel is expanded
   */
  expanded = signal<boolean>(false);

  /**
   * Reactive form for filter inputs
   */
  filterForm: FormGroup;

  /**
   * Number of active filters
   */
  activeFilterCount = signal<number>(0);

  constructor() {
    // Initialize form with all filter controls
    this.filterForm = this.fb.group({
      tradeType: [null],
      book: [''],
      counterparty: [''],
      startDate: [null],
      endDate: [null],
      searchText: ['']
    });
  }

  ngOnInit(): void {
    // Subscribe to form changes with debouncing for text inputs
    this.filterForm.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged()
      )
      .subscribe(() => {
        this.updateActiveFilterCount();
        // Auto-apply filters on change (optional - can be removed if manual apply is preferred)
        // this.applyFilters();
      });
  }

  /**
   * Apply current filter values and emit to parent
   */
  applyFilters(): void {
    const formValue = this.filterForm.value;
    
    const filters: TradeFilters = {
      tradeType: formValue.tradeType || null,
      book: formValue.book || null,
      counterparty: formValue.counterparty || null,
      searchText: formValue.searchText || null,
      dateRange: this.getDateRange(formValue.startDate, formValue.endDate)
    };

    this.filterChange.emit(filters);
  }

  /**
   * Clear all filters and emit empty filter state
   */
  clearFilters(): void {
    this.filterForm.reset({
      tradeType: null,
      book: '',
      counterparty: '',
      startDate: null,
      endDate: null,
      searchText: ''
    });
    
    this.updateActiveFilterCount();
    this.applyFilters();
  }

  /**
   * Update the count of active filters
   */
  private updateActiveFilterCount(): void {
    const formValue = this.filterForm.value;
    let count = 0;

    if (formValue.tradeType) count++;
    if (formValue.book) count++;
    if (formValue.counterparty) count++;
    if (formValue.startDate) count++;
    if (formValue.endDate) count++;
    if (formValue.searchText) count++;

    this.activeFilterCount.set(count);
  }

  /**
   * Create date range object from start and end dates
   */
  private getDateRange(startDate: Date | null, endDate: Date | null): DateRange | null {
    if (!startDate && !endDate) {
      return null;
    }

    return {
      startDate: startDate || null,
      endDate: endDate || null
    };
  }
}
