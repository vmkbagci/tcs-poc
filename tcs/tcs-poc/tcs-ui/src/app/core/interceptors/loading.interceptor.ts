import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { finalize } from 'rxjs';
import { LoadingService } from '../services/loading.service';

/**
 * HTTP Interceptor for managing loading state
 * Shows loading indicator when requests are in progress
 * Hides loading indicator when requests complete or fail
 * 
 * @param req - The outgoing HTTP request
 * @param next - The next handler in the interceptor chain
 * @returns Observable of the HTTP response with loading state management
 */
export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  const loadingService = inject(LoadingService);

  // Show loading indicator
  loadingService.show();

  // Hide loading indicator when request completes (success or error)
  return next(req).pipe(
    finalize(() => loadingService.hide())
  );
};
