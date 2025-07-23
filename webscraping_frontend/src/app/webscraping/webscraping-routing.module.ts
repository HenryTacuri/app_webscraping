import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PrediccionesComponent } from './pages/predicciones/predicciones.component';

const routes: Routes = [
  {
    path: '',
    children: [
      {path: 'webscraping', component: PrediccionesComponent},
      {path: '**', redirectTo: 'webscraping'},
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class WebscrapingRoutingModule { }
