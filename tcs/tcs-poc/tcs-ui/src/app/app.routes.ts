import { Routes } from '@angular/router';
import { unsavedChangesGuard } from './core/guards/unsaved-changes.guard';

/**
 * Application routes with lazy loading
 * 
 * Routes:
 * - / : Home page with navigation links
 * - /trades : Trade list view
 * - /trades/new : Create new trade
 * - /trades/:id : View/edit trade details
 * - /** : Catch-all redirects to home
 */
export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/home/home.component')
      .then(m => m.HomeComponent),
    title: 'Trade Management System'
  },
  {
    path: 'demo/panels',
    loadComponent: () => import('./features/ui-demo/ui-demo.component')
      .then(m => m.UiDemoComponent),
    title: 'UI Capabilities Demo'
  },
  {
    path: 'trades',
    loadComponent: () => import('./features/trade-list/trade-list.component')
      .then(m => m.TradeListComponent),
    title: 'Trade List'
  },
  {
    path: 'trades/new',
    loadComponent: () => import('./features/trade-create/trade-create.component')
      .then(m => m.TradeCreateComponent),
    title: 'Create Trade'
  },
  {
    path: 'trades/:id',
    loadComponent: () => import('./features/trade-detail/trade-detail.component')
      .then(m => m.TradeDetailComponent),
    canDeactivate: [unsavedChangesGuard],
    title: 'Trade Detail'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
