import { CanDeactivateFn } from '@angular/router';
import { inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

/**
 * Interface for components that have unsaved changes
 * Components using this guard must implement this interface
 */
export interface ComponentWithUnsavedChanges {
  /**
   * Check if the component has unsaved changes
   * @returns true if there are unsaved changes, false otherwise
   */
  hasUnsavedChanges(): boolean;
}

/**
 * Functional route guard to prevent navigation when there are unsaved changes
 * Shows a confirmation dialog to the user before allowing navigation
 * 
 * @param component - The component being deactivated
 * @returns true to allow navigation, false to prevent it
 */
export const unsavedChangesGuard: CanDeactivateFn<ComponentWithUnsavedChanges> = (
  component
): boolean | Observable<boolean> => {
  // If no unsaved changes, allow navigation
  if (!component.hasUnsavedChanges()) {
    return true;
  }

  // Use native browser confirm dialog
  // In a production app, you might want to use a Material Dialog instead
  return confirm(
    'You have unsaved changes. Are you sure you want to leave? Your changes will be lost.'
  );
};

/**
 * Alternative guard using Material Dialog for a better UX
 * This can be used instead of the basic confirm dialog
 */
export const unsavedChangesDialogGuard: CanDeactivateFn<ComponentWithUnsavedChanges> = (
  component
): boolean | Observable<boolean> => {
  // If no unsaved changes, allow navigation
  if (!component.hasUnsavedChanges()) {
    return true;
  }

  const dialog = inject(MatDialog);

  // Open confirmation dialog
  const dialogRef = dialog.open(UnsavedChangesDialogComponent, {
    width: '400px',
    disableClose: true,
    data: {
      title: 'Unsaved Changes',
      message: 'You have unsaved changes. Are you sure you want to leave? Your changes will be lost.',
      confirmText: 'Leave',
      cancelText: 'Stay'
    }
  });

  return dialogRef.afterClosed().pipe(
    map(result => result === true)
  );
};

/**
 * Simple confirmation dialog component for unsaved changes
 * This is a minimal implementation - can be enhanced with better styling
 */
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';

export interface UnsavedChangesDialogData {
  title: string;
  message: string;
  confirmText: string;
  cancelText: string;
}

@Component({
  selector: 'app-unsaved-changes-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>{{ data.title }}</h2>
    <mat-dialog-content>
      <p>{{ data.message }}</p>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="onCancel()">{{ data.cancelText }}</button>
      <button mat-raised-button color="warn" (click)="onConfirm()">{{ data.confirmText }}</button>
    </mat-dialog-actions>
  `,
  styles: [`
    mat-dialog-content {
      padding: 20px 0;
    }
    mat-dialog-actions {
      padding: 8px 0;
    }
  `]
})
export class UnsavedChangesDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<UnsavedChangesDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: UnsavedChangesDialogData
  ) {}

  onConfirm(): void {
    this.dialogRef.close(true);
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }
}
