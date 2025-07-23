from flask import Flask, render_template, request, jsonify, url_for
from recoleccion_tiktok import buscar_videos_tiktok
from recoleccion_facebook import extraer_publicaciones_facebook
from recoleccion_reddit import extraer_publicaciones_reddit
from preprocesamiento import procesar_lista_dataset_multiproceso
from predicciones import bolsa_palabras
from predicciones import realzar_preddiccione
import pandas as pd
from flask_cors import CORS
import time


app = Flask(__name__)

CORS(app)

# Definimos el ENDPOINT del servidor Flask
@app.route('/procesar_enfermedad', methods=['POST'])
def procesar_enfermedad():
    data = request.get_json() # Obtenemos los datos del POST

    print("Datos recibidos:", data)  # Imprimimos los datos recibidos para depuración
    
    enfermedad = data['enfermedad'] # Obtenemos el valor de enfermedad del POST
    anio = data['anio']
    max_publi = data['max_publi']

    print("Enfermedad:", enfermedad)  # Imprimimos el valor de enfermedad para depuración
    print("Año:", anio)  # Imprimimos el año para depuración    

    publish_time = 180  # Valor por defecto: 180 días
    
        
    # ********************* Procesamos los datos de titkok *************************

    resultados_tiktok = buscar_videos_tiktok(enfermedad, publish_time) 


    # ********************* Procesamos los datos de reddit **************************
    
    resultados_reddit = extraer_publicaciones_reddit(enfermedad, anio, max_publi)
    
    # ********************* Procesamos los datos de facebook *************************
    
    resultados_facebook = extraer_publicaciones_facebook(
        num_publicaciones=max_publi,
        enfermedad=enfermedad,
        num_comentarios=10,
        anio_publicacion=anio
    )

    # 1) TikTok
    start = time.perf_counter()
    datos_procesados_tiktok = procesar_lista_dataset_multiproceso(resultados_tiktok)
    elapsed = time.perf_counter() - start
    print(f"Procesamiento de texto TikTok: {elapsed:.2f} s")

    # 2) Reddit
    start = time.perf_counter()
    datos_procesados_reddit = procesar_lista_dataset_multiproceso(resultados_reddit)
    elapsed = time.perf_counter() - start
    print(f"Procesamiento de texto Reddit:  {elapsed:.2f} s")


    # 3) Facebook
    #resultados_facebook = pd.read_csv('src/webscraping/api/data/publicaciones_facebook.csv')
    start = time.perf_counter()
    datos_procesados_facebook = procesar_lista_dataset_multiproceso(resultados_facebook)
    elapsed = time.perf_counter() - start
    print(f"Procesamiento de texto Facebook: {elapsed:.2f} s")


    # unimos los datos procesados en un solo DataFrame
    df_total_publicaciones = pd.concat([datos_procesados_reddit, datos_procesados_tiktok, datos_procesados_facebook], ignore_index=True)

    df_total_publicaciones.to_csv('src/webscraping/api/data/total_publicaciones.csv', index=False, encoding="utf-8-sig")

    # Bolsa de palabras
    bolsa_palabras_commentarios = bolsa_palabras(df_total_publicaciones)

    # Predicciones
    graficar_emociones = realzar_preddiccione(df_total_publicaciones, enfermedad)

    
    estadisticas_img = url_for('static', filename='estadisticas.png', _external=True)
    bolsa_palabras_img = url_for('static', filename='bolsa_palabras.png', _external=True)

    return jsonify({
        'estadisticas_img': estadisticas_img,
        'bolsa_palabras_img': bolsa_palabras_img,
        'texto': graficar_emociones
    })
    


# Iniciar servidor Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')    

