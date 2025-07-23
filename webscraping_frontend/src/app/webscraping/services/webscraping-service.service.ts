import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class WebscrapingServiceService {

  private BASE_URL = 'http://localhost:5000';

  constructor(private http: HttpClient) { }

  getPredicciones(formData: any) {

    return this.http.post<any>(`${this.BASE_URL}/procesar_enfermedad`, formData);
  }

}
