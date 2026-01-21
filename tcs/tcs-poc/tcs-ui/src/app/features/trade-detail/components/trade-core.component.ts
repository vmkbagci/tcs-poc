/**
 * Trade Core Component
 * 
 * Displays core trade information (general and common sections)
 * that applies to all trade types.
 * Supports edit mode and emits changes from sub-components.
 */

import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { TradeCore, GeneralSection, CommonSection } from '@core/models/trade-core.model';
import { GeneralSectionComponent } from './general-section.component';
import { CommonSectionComponent } from './common-section.component';

@Component({
  selector: 'app-trade-core',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatExpansionModule,
    GeneralSectionComponent,
    CommonSectionComponent
  ],
  template: `
    <div class="trade-core-container">
      <!-- General Section Component -->
      <app-general-section
        [generalSection]="tradeCore()?.general"
        [isEditMode]="editMode()"
        (valueChange)="onGeneralChange($event)">
      </app-general-section>

      <!-- Common Section Component -->
      <app-common-section
        [commonSection]="tradeCore()?.common"
        [isEditMode]="editMode()"
        (valueChange)="onCommonChange($event)">
      </app-common-section>
    </div>
  `,
  styles: [`
    .trade-core-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
  `]
})
export class TradeCoreComponent {
  /**
   * Trade core data
   */
  @Input() set trade(value: TradeCore | null) {
    this.tradeCore.set(value);
  }

  /**
   * Edit mode flag
   */
  @Input() set isEditMode(value: boolean) {
    this.editMode.set(value);
  }

  /**
   * Event emitted when trade core data changes
   */
  @Output() valueChange = new EventEmitter<TradeCore>();

  /**
   * Trade core signal
   */
  tradeCore = signal<TradeCore | null>(null);

  /**
   * Edit mode signal
   */
  editMode = signal<boolean>(false);

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle general section changes
   * 
   * @param general - Updated general section data
   */
  onGeneralChange(general: GeneralSection): void {
    const currentTrade = this.tradeCore();
    if (currentTrade) {
      const updatedTrade: TradeCore = {
        ...currentTrade,
        general
      };
      this.tradeCore.set(updatedTrade);
      this.valueChange.emit(updatedTrade);
    }
  }

  /**
   * Handle common section changes
   * 
   * @param common - Updated common section data
   */
  onCommonChange(common: CommonSection): void {
    const currentTrade = this.tradeCore();
    if (currentTrade) {
      const updatedTrade: TradeCore = {
        ...currentTrade,
        common
      };
      this.tradeCore.set(updatedTrade);
      this.valueChange.emit(updatedTrade);
    }
  }
}
