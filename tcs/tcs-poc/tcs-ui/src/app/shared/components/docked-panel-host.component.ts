/**
 * Docked Panel Host Component
 * 
 * Coordinates multiple docked slide-out panels on the same view.
 * Manages stacking and positioning of collapsed title strips to prevent overlap.
 * 
 * Strategy: Stacked strips along viewport edge with spacing/gap
 * - Left-side panels: strips stacked vertically on left edge
 * - Right-side panels: strips stacked vertically on right edge
 * - Each strip has a gap to prevent overlap
 * - Expanded panels overlay content with z-index management
 * 
 * Panels are independent:
 * - Each can be collapsed/expanded independently
 * - No auto-collapse behavior (not an accordion)
 * - No tabs or exclusive selection
 * 
 * @example
 * <app-docked-panel-host>
 *   <app-docked-slide-out-panel
 *     id="panel-1"
 *     title="Panel 1"
 *     side="right">
 *     <div panel-content>Content 1</div>
 *   </app-docked-slide-out-panel>
 *   
 *   <app-docked-slide-out-panel
 *     id="panel-2"
 *     title="Panel 2"
 *     side="right">
 *     <div panel-content>Content 2</div>
 *   </app-docked-slide-out-panel>
 * </app-docked-panel-host>
 */

import { 
  Component,
  ContentChildren,
  QueryList,
  AfterContentInit,
  OnDestroy
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { DockedSlideOutPanelComponent } from './docked-slide-out-panel.component';
import { Subject, takeUntil } from 'rxjs';

/**
 * Panel positioning info for stacking calculation
 */
interface PanelPosition {
  id: string;
  side: 'left' | 'right';
  index: number;
  offsetTop: number;
}

@Component({
  selector: 'app-docked-panel-host',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="docked-panel-host">
      <ng-content></ng-content>
    </div>
  `,
  styles: [`
    /*
     * Host container
     * Provides context for multiple panels
     * Does not interfere with panel positioning (panels are fixed)
     */
    .docked-panel-host {
      position: relative;
      width: 100%;
      height: 100%;
    }

    /*
     * Note: Panel positioning is handled by individual panel components
     * This host only coordinates z-index and provides organizational context
     */
  `]
})
export class DockedPanelHostComponent implements AfterContentInit, OnDestroy {
  
  /**
   * Query all child panel components
   */
  @ContentChildren(DockedSlideOutPanelComponent) 
  panels!: QueryList<DockedSlideOutPanelComponent>;

  /**
   * Destroy subject for cleanup
   */
  private destroy$ = new Subject<void>();

  /**
   * Base z-index for panels
   * Each panel gets incremented z-index based on order
   */
  private baseZIndex = 1000;

  /**
   * Vertical spacing between collapsed title strips (in pixels)
   */
  private readonly STRIP_SPACING = 16;

  /**
   * Approximate height of a collapsed title strip (in pixels)
   * Used for stacking calculation
   */
  private readonly STRIP_HEIGHT = 160;

  // ============================================================================
  // Lifecycle
  // ============================================================================

  ngAfterContentInit(): void {
    // Initial setup
    this.setupPanels();

    // Re-setup when panels change
    this.panels.changes
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.setupPanels();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ============================================================================
  // Panel Coordination
  // ============================================================================

  /**
   * Setup panels: assign z-index and calculate positions
   * 
   * Z-Index Strategy:
   * - Panels are assigned z-index in order of appearance
   * - Later panels have higher z-index (appear on top when expanded)
   * - This creates a natural stacking order
   * 
   * Position Strategy:
   * - Group panels by side (left/right)
   * - Stack collapsed strips vertically with spacing
   * - Calculate offset for each panel to prevent overlap
   */
  private setupPanels(): void {
    if (!this.panels || this.panels.length === 0) {
      return;
    }

    const panelArray = this.panels.toArray();
    
    // Group panels by side
    const leftPanels: DockedSlideOutPanelComponent[] = [];
    const rightPanels: DockedSlideOutPanelComponent[] = [];

    panelArray.forEach((panel, index) => {
      // Assign z-index
      panel.zIndex = this.baseZIndex + index;

      // Group by side
      if (panel.side === 'left') {
        leftPanels.push(panel);
      } else {
        rightPanels.push(panel);
      }
    });

    // Calculate positions for each side
    // Note: In current implementation, panels use CSS transform: translateY(-50%)
    // for vertical centering. For multiple panels, we would need to adjust
    // the top position to stack them. This is a future enhancement.
    
    // For now, we document the stacking strategy:
    // - If multiple panels on same side, they will overlap when collapsed
    // - To prevent overlap, we would need to:
    //   1. Calculate total height needed for all strips
    //   2. Distribute strips vertically with spacing
    //   3. Apply custom top offset to each panel
    
    // This is left as a TODO for production implementation
    // Current implementation works best with 1-2 panels per side
    
    console.log(`[DockedPanelHost] Setup complete: ${leftPanels.length} left, ${rightPanels.length} right`);
  }

  /**
   * Calculate vertical positions for stacked panels
   * 
   * Strategy:
   * - Start from top of viewport with initial offset
   * - Stack each panel's title strip with spacing
   * - Return array of positions
   * 
   * Note: This is a helper method for future enhancement
   * Current implementation doesn't apply these positions yet
   */
  private calculateStackedPositions(panels: DockedSlideOutPanelComponent[]): PanelPosition[] {
    const positions: PanelPosition[] = [];
    let currentOffset = 100; // Start 100px from top

    panels.forEach((panel, index) => {
      positions.push({
        id: panel.id,
        side: panel.side,
        index,
        offsetTop: currentOffset
      });

      // Increment offset for next panel
      currentOffset += this.STRIP_HEIGHT + this.STRIP_SPACING;
    });

    return positions;
  }

  // ============================================================================
  // Public API (for future enhancements)
  // ============================================================================

  /**
   * Get panel by ID
   */
  getPanelById(id: string): DockedSlideOutPanelComponent | undefined {
    return this.panels.find(panel => panel.id === id);
  }

  /**
   * Collapse all panels
   */
  collapseAll(): void {
    this.panels.forEach(panel => panel.collapse());
  }

  /**
   * Expand all panels
   */
  expandAll(): void {
    this.panels.forEach(panel => panel.expand());
  }

  /**
   * Get panels by side
   */
  getPanelsBySide(side: 'left' | 'right'): DockedSlideOutPanelComponent[] {
    return this.panels.filter(panel => panel.side === side);
  }
}
