import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { WebscrapingRoutingModule } from './webscraping-routing.module';
import { PrediccionesComponent } from './pages/predicciones/predicciones.component';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    PrediccionesComponent,
  ],
  imports: [
    CommonModule,
    WebscrapingRoutingModule,
    HttpClientModule,
    ReactiveFormsModule
  ]
})
export class WebscrapingModule { }

