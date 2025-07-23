import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { WebscrapingServiceService } from '../../services/webscraping-service.service';

@Component({
  selector: 'app-predicciones',
  templateUrl: './predicciones.component.html',
  styleUrl: './predicciones.component.css'
})
export class PrediccionesComponent {

  private fb = inject(FormBuilder);
  private webscrapingService = inject(WebscrapingServiceService);

  public estadisticas: string = '';
  public bolsa_palabras: string = '';
  public explicacion_predicciones: string = '';
  public viewLoader: boolean = false;

  public enfermedades = [
    "Cáncer cerebral", "Cáncer de estómago", "Cáncer al pulmón",
    "Cáncer al hígado", "Dolor de estómago", "Enfermedad del asma",
    "Enfermedad de neumonía", "Enfermedad de laringitis",
    "Enfermedad de bronquitis", "Fibrosis pulmonar",
    "Enfermedad de gastritis", "Enfermedad de gastroenteritis",
    "Cálculos biliares", "Alzheimer", "Enfermedad de la diabetes",
    "Insuficiencia cardiaca", "Enfermedad de hipertensión arterial"
  ];

  public myForm: FormGroup = this.fb.group({
    enfermedad: ['', [Validators.required]],
    anio: [2015, [Validators.required, Validators.min(2015), Validators.max(2025)]],
    max_publi: [1, [Validators.required, Validators.min(1)]]
  });

  prededir() {

    if (this.myForm.invalid) return;

    this.viewLoader = true;
    const formData = this.myForm.value;

    /*this.webscrapingService.getPredicciones(formData).subscribe(resp => {
      console.log(resp);
      this.estadisticas = resp.estadisticas_img;
      this.bolsa_palabras = resp.bolsa_palabras_img;
      this.explicacion_predicciones = resp.texto;
      this.viewLoader = false;
    });*/


  }

  nuevaBusquea() {
    this.viewLoader = false;
    this.bolsa_palabras = '';
    this.estadisticas = '';
    this.explicacion_predicciones = ''
  }

}
