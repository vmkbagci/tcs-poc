import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { catchError, throwError } from 'rxjs';

/**
 * HTTP Interceptor for global error handling
 * Maps HTTP errors to user-friendly messages and displays them via MatSnackBar
 * 
 * @param req - The outgoing HTTP request
 * @param next - The next handler in the interceptor chain
 * @returns Observable of the HTTP response with error handling
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const snackBar = inject(MatSnackBar);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'An unexpected error occurred';

      if (error.error instanceof ErrorEvent) {
        // Client-side or network error
        errorMessage = `Network Error: ${error.error.message}`;
      } else {
        // Server-side error
        errorMessage = getServerErrorMessage(error);
      }

      // Display error notification to user
      snackBar.open(errorMessage, 'Close', {
        duration: 5000,
        horizontalPosition: 'center',
        verticalPosition: 'top',
        panelClass: ['error-snackbar']
      });

      // Re-throw the error so components can handle it if needed
      return throwError(() => error);
    })
  );
};

/**
 * Maps HTTP status codes and error responses to user-friendly messages
 * 
 * @param error - The HTTP error response
 * @returns User-friendly error message
 */
function getServerErrorMessage(error: HttpErrorResponse): string {
  // Check if the error response has a custom message
  if (error.error?.message) {
    return error.error.message;
  }

  if (error.error?.errors && Array.isArray(error.error.errors)) {
    // Handle validation errors array
    return error.error.errors.join(', ');
  }

  // Map common HTTP status codes to user-friendly messages
  switch (error.status) {
    case 0:
      return 'Connection failed. Please check your network connection.';
    case 400:
      return 'Invalid request. Please check your input and try again.';
    case 401:
      return 'Unauthorized. Please log in and try again.';
    case 403:
      return 'Access denied. You do not have permission to perform this action.';
    case 404:
      return 'Resource not found. The requested item does not exist.';
    case 408:
      return 'Request timeout. Please try again.';
    case 409:
      return 'Conflict. The resource has been modified by another user.';
    case 422:
      return 'Validation failed. Please check your input.';
    case 429:
      return 'Too many requests. Please wait a moment and try again.';
    case 500:
      return 'Server error. Please try again later.';
    case 502:
      return 'Bad gateway. The server is temporarily unavailable.';
    case 503:
      return 'Service unavailable. Please try again later.';
    case 504:
      return 'Gateway timeout. The server took too long to respond.';
    default:
      return `Error ${error.status}: ${error.message || 'An error occurred'}`;
  }
}
