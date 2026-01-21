/**
 * Docked Slide-Out Panel Component
 * 
 * A partial-size panel that docks to the left or right viewport edge.
 * When collapsed, shows a persistent vertical title strip + arrow toggle.
 * When expanded, slides into view with configurable width/height.
 * 
 * This is NOT:
 * - A hamburger menu
 * - A full-height sidenav
 * - A modal dialog
 * 
 * Key Features:
 * - Persistent vertical title strip when collapsed
 * - Independent collapse/expand (no auto-close)
 * - Supports multiple panels on same view
 * - Configurable size, position, and behavior
 * 
 * @example
 * <app-docked-slide-out-panel
 *   id="validation-panel"
 *   title="Validation Response"
 *   [side]="'right'"
 *   [widthRatio]="0.5"
 *   [heightRatio]="0.8"
 *   [collapsed]="isCollapsed"
 *   (collapsedChange)="onCollapsedChange($event)">
 *   <div panel-content>
 *     Your content here
 *   </div>
 * </app-docked-slide-out-panel>
 */

import { 
  Component, 
  Input, 
  Output, 
  EventEmitter, 
  signal, 
  computed,
  OnInit,
  OnChanges,
  SimpleChanges,
  effect
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

export type PanelSide = 'left' | 'right';

@Component({
  selector: 'app-docked-slide-out-panel',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <div 
      class="docked-panel-wrapper"
      [class.docked-panel-wrapper--left]="side === 'left'"
      [class.docked-panel-wrapper--right]="side === 'right'"
      [style.z-index]="zIndex">
      
      <!-- Chrome: Always visible, fixed position -->
      <div class="docked-panel__chrome" [style.background-color]="chromeColor">
        <!-- Vertical Title Strip -->
        <div 
          class="docked-panel__title-strip"
          [class.docked-panel__title-strip--clickable]="toggleOnTitleClick"
          [style.background-color]="chromeColor"
          (click)="onTitleStripClick()"
          [attr.role]="toggleOnTitleClick ? 'button' : null"
          [attr.tabindex]="toggleOnTitleClick ? 0 : null"
          [attr.aria-label]="toggleOnTitleClick ? (isCollapsed() ? 'Expand ' + title : 'Collapse ' + title) : null">
          <span class="docked-panel__title-text">{{ title }}</span>
        </div>

        <!-- Arrow Toggle -->
        <button 
          mat-icon-button
          class="docked-panel__toggle-arrow"
          [style.background-color]="chromeColor"
          (click)="toggle()"
          [attr.aria-label]="isCollapsed() ? 'Expand ' + title : 'Collapse ' + title"
          [attr.aria-expanded]="!isCollapsed()">
          <mat-icon>{{ arrowIcon() }}</mat-icon>
        </button>
      </div>

      <!-- Panel Surface: Slides in/out -->
      <div 
        class="docked-panel__surface"
        [class.docked-panel__surface--collapsed]="isCollapsed()"
        [class.docked-panel__surface--expanded]="!isCollapsed()"
        [style.width]="panelWidth()"
        [style.height]="panelHeight()"
        [style.transition]="transitionStyle()">
        <ng-content select="[panel-content]"></ng-content>
      </div>
    </div>
  `,
  styles: [`
    /*
     * Wrapper Container
     * Contains both chrome and surface
     */
    .docked-panel-wrapper {
      position: fixed;
      top: 50%;
      transform: translateY(-50%);
      display: flex;
      pointer-events: none; /* Allow clicks through wrapper */
    }

    .docked-panel-wrapper > * {
      pointer-events: auto; /* Re-enable clicks on children */
    }

    /*
     * Left-side positioning
     */
    .docked-panel-wrapper--left {
      left: 0;
      flex-direction: row;
    }

    /*
     * Right-side positioning
     */
    .docked-panel-wrapper--right {
      right: 0;
      flex-direction: row-reverse;
    }

    /*
     * Chrome Container
     * Always visible, contains title strip and arrow
     */
    .docked-panel__chrome {
      display: flex;
      align-items: center;
      flex-shrink: 0;
      position: relative;
      z-index: 2;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      height: 48px; /* Fixed height to match title */
    }

    /*
     * Left panel chrome: arrow on right (toward center)
     */
    .docked-panel-wrapper--left .docked-panel__chrome {
      flex-direction: row;
    }

    /*
     * Right panel chrome: arrow on left (toward center)
     */
    .docked-panel-wrapper--right .docked-panel__chrome {
      flex-direction: row-reverse;
    }

    /*
     * Title Strip
     * Displays panel title horizontally
     * Always visible
     */
    .docked-panel__title-strip {
      padding: 12px 16px;
      color: white;
      font-weight: 500;
      font-size: 14px;
      letter-spacing: 0.5px;
      white-space: nowrap;
      user-select: none;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }

    .docked-panel__title-strip--clickable {
      cursor: pointer;
      transition: background-color 0.2s ease, filter 0.2s ease;
    }

    .docked-panel__title-strip--clickable:hover {
      filter: brightness(0.9);
    }

    .docked-panel__title-strip--clickable:focus {
      outline: 2px solid white;
      outline-offset: -2px;
    }

    .docked-panel__title-text {
      display: block;
    }

    /*
     * Arrow Toggle Button
     * Sized to match title strip height
     */
    .docked-panel__toggle-arrow {
      color: white;
      width: 32px;
      height: 32px;
      flex-shrink: 0;
      border-radius: 4px;
      margin: 0 8px;
      transition: filter 0.2s ease;
    }

    .docked-panel__toggle-arrow:hover {
      filter: brightness(0.9);
    }

    .docked-panel__toggle-arrow mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    /*
     * Panel Surface (Content Area)
     * Slides in/out horizontally
     */
    .docked-panel__surface {
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background-color: white;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      flex-shrink: 0;
    }

    /*
     * Left panel surface - slides from left
     */
    .docked-panel-wrapper--left .docked-panel__surface--collapsed {
      width: 0 !important;
      opacity: 0;
    }

    .docked-panel-wrapper--left .docked-panel__surface--expanded {
      opacity: 1;
    }

    /*
     * Right panel surface - slides from right
     */
    .docked-panel-wrapper--right .docked-panel__surface--collapsed {
      width: 0 !important;
      opacity: 0;
    }

    .docked-panel-wrapper--right .docked-panel__surface--expanded {
      opacity: 1;
    }

    /*
     * Responsive: Mobile adjustments
     */
    @media (max-width: 768px) {
      .docked-panel__surface {
        width: 90vw !important;
        height: 80vh !important;
      }
    }
  `]
})
export class DockedSlideOutPanelComponent implements OnInit, OnChanges {
  
  // ============================================================================
  // Inputs
  // ============================================================================

  /**
   * Unique identifier for this panel
   * Used for coordination in multi-panel scenarios
   */
  @Input({ required: true }) id!: string;

  /**
   * Panel title displayed on the vertical title strip
   */
  @Input({ required: true }) title!: string;

  /**
   * Which side of viewport to dock the panel
   * @default 'right'
   */
  @Input() side: PanelSide = 'right';

  /**
   * Panel width as ratio of viewport width (0.0 to 1.0)
   * @default 0.5 (50% of viewport)
   */
  @Input() widthRatio: number = 0.5;

  /**
   * Panel height as ratio of viewport height (0.0 to 1.0)
   * @default 0.5 (50% of viewport)
   */
  @Input() heightRatio: number = 0.5;

  /**
   * Collapsed state (controlled mode)
   * If provided, component operates in controlled mode
   * If not provided, component manages its own state (uncontrolled mode)
   */
  @Input() collapsed?: boolean;

  /**
   * Whether clicking the title strip toggles the panel
   * @default true
   */
  @Input() toggleOnTitleClick: boolean = true;

  /**
   * Z-index for stacking multiple panels
   * @default 1000
   */
  @Input() zIndex: number = 1000;

  /**
   * Animation duration in milliseconds
   * @default 300
   */
  @Input() animationDuration: number = 300;

  /**
   * CSS easing function for animation
   * @default 'cubic-bezier(0.4, 0.0, 0.2, 1)'
   */
  @Input() animationEasing: string = 'cubic-bezier(0.4, 0.0, 0.2, 1)';

  /**
   * Chrome color (for title strip and arrow)
   * @default '#1976d2' (Material blue)
   * Can be set to indicate status: '#4caf50' (green), '#ff9800' (orange), '#f44336' (red)
   */
  @Input() chromeColor: string = '#1976d2';

  // ============================================================================
  // Outputs
  // ============================================================================

  /**
   * Emitted when collapsed state changes
   * Use for controlled mode: [collapsed]="state" (collapsedChange)="state=$event"
   */
  @Output() collapsedChange = new EventEmitter<boolean>();

  /**
   * Emitted when panel is opened (collapsed -> expanded)
   */
  @Output() opened = new EventEmitter<void>();

  /**
   * Emitted when panel is closed (expanded -> collapsed)
   */
  @Output() closed = new EventEmitter<void>();

  // ============================================================================
  // Internal State
  // ============================================================================

  /**
   * Internal collapsed state
   * Used for both controlled and uncontrolled modes
   * In controlled mode, synced via ngOnChanges
   */
  private _internalCollapsed = signal<boolean>(true);

  /**
   * Computed collapsed state
   * Always reads from internal signal for reactivity
   */
  isCollapsed = computed(() => this._internalCollapsed());

  /**
   * Computed panel width style
   */
  panelWidth = computed(() => `${this.widthRatio * 100}vw`);

  /**
   * Computed panel height style
   */
  panelHeight = computed(() => `${this.heightRatio * 100}vh`);

  /**
   * Computed transition style
   */
  transitionStyle = computed(() => 
    `transform ${this.animationDuration}ms ${this.animationEasing}`
  );

  /**
   * Computed arrow icon based on side and state
   * 
   * Arrow Orientation Logic:
   * - Collapsed + Left side: chevron_right (points inward/right to expand)
   * - Collapsed + Right side: chevron_left (points inward/left to expand)
   * - Expanded + Left side: chevron_left (points outward/left to collapse)
   * - Expanded + Right side: chevron_right (points outward/right to collapse)
   */
  arrowIcon = computed(() => {
    const collapsed = this.isCollapsed();
    
    if (this.side === 'left') {
      return collapsed ? 'chevron_right' : 'chevron_left';
    } else {
      return collapsed ? 'chevron_left' : 'chevron_right';
    }
  });

  // ============================================================================
  // Lifecycle
  // ============================================================================

  constructor() {
    // Sync effect: emit events when state changes
    effect(() => {
      const collapsed = this.isCollapsed();
      // Effect runs, but we only emit events on actual toggle actions
    });
  }

  ngOnInit(): void {
    // Initialize internal state
    if (this.collapsed !== undefined) {
      // Controlled mode: sync from input
      this._internalCollapsed.set(this.collapsed);
    } else {
      // Uncontrolled mode: start collapsed
      this._internalCollapsed.set(true);
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    // Sync internal state when controlled input changes
    if (changes['collapsed'] && this.collapsed !== undefined) {
      console.log(`[${this.id}] ngOnChanges - collapsed input changed to:`, this.collapsed);
      this._internalCollapsed.set(this.collapsed);
    }
  }

  // ============================================================================
  // Public API
  // ============================================================================

  /**
   * Toggle panel between collapsed and expanded
   */
  toggle(): void {
    console.log(`[${this.id}] Toggle called. Current state:`, this.isCollapsed());
    const newState = !this.isCollapsed();
    console.log(`[${this.id}] New state will be:`, newState);
    this.setCollapsed(newState);
  }

  /**
   * Expand the panel
   */
  expand(): void {
    if (this.isCollapsed()) {
      this.setCollapsed(false);
    }
  }

  /**
   * Collapse the panel
   */
  collapse(): void {
    if (!this.isCollapsed()) {
      this.setCollapsed(true);
    }
  }

  // ============================================================================
  // Internal Methods
  // ============================================================================

  /**
   * Set collapsed state and emit appropriate events
   */
  private setCollapsed(collapsed: boolean): void {
    const wasCollapsed = this.isCollapsed();
    console.log(`[${this.id}] setCollapsed called. Was: ${wasCollapsed}, New: ${collapsed}, Controlled: ${this.collapsed !== undefined}`);
    
    // In controlled mode, emit event for parent to update
    // In uncontrolled mode, update internal state directly
    if (this.collapsed !== undefined) {
      // Controlled mode: emit change event
      // Parent will update input, which triggers ngOnChanges, which updates internal state
      console.log(`[${this.id}] Controlled mode - emitting collapsedChange`);
      this.collapsedChange.emit(collapsed);
    } else {
      // Uncontrolled mode: update internal state directly
      console.log(`[${this.id}] Uncontrolled mode - updating internal state`);
      this._internalCollapsed.set(collapsed);
      this.collapsedChange.emit(collapsed);
    }

    // Emit opened/closed events
    if (wasCollapsed && !collapsed) {
      this.opened.emit();
    } else if (!wasCollapsed && collapsed) {
      this.closed.emit();
    }

    console.log(`[${this.id}] State after setCollapsed:`, this.isCollapsed());
  }

  /**
   * Handle title strip click
   */
  onTitleStripClick(): void {
    if (this.toggleOnTitleClick) {
      this.toggle();
    }
  }
}
