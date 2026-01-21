import { Directive, ElementRef, Input, AfterViewInit, OnDestroy } from '@angular/core';

/**
 * AutoFocusDirective
 * 
 * Automatically focuses an element when it becomes visible or when a condition is met.
 * Useful for improving form UX by focusing the first input field.
 * 
 * Requirements: 8.5 - Provide accessible UI elements following ARIA guidelines
 * 
 * Usage:
 *   <input appAutoFocus />
 *   <input [appAutoFocus]="shouldFocus" />
 *   <input appAutoFocus [autoFocusDelay]="100" />
 */
@Directive({
  selector: '[appAutoFocus]',
  standalone: true
})
export class AutoFocusDirective implements AfterViewInit, OnDestroy {
  private timeoutId?: number;

  /**
   * Whether to apply autofocus. Can be a boolean or undefined.
   * If undefined or true, autofocus will be applied.
   */
  @Input() appAutoFocus: boolean | '' = true;

  /**
   * Delay in milliseconds before focusing the element.
   * Useful for waiting for animations or other async operations.
   */
  @Input() autoFocusDelay: number = 0;

  constructor(private elementRef: ElementRef<HTMLElement>) {}

  ngAfterViewInit(): void {
    // Check if autofocus should be applied
    const shouldFocus = this.appAutoFocus === '' || this.appAutoFocus === true;

    if (shouldFocus) {
      if (this.autoFocusDelay > 0) {
        this.timeoutId = window.setTimeout(() => {
          this.focus();
        }, this.autoFocusDelay);
      } else {
        // Use setTimeout with 0 to ensure DOM is fully rendered
        this.timeoutId = window.setTimeout(() => {
          this.focus();
        }, 0);
      }
    }
  }

  ngOnDestroy(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
  }

  private focus(): void {
    const element = this.elementRef.nativeElement;
    
    // Check if element is focusable
    if (element && typeof element.focus === 'function') {
      try {
        element.focus();
        
        // For input elements, also select the text if present
        if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
          if (element.value) {
            element.select();
          }
        }
      } catch (error) {
        console.warn('AutoFocusDirective: Unable to focus element', error);
      }
    }
  }
}
