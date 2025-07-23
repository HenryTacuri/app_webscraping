import http.client # Importamos http.client para realizar peticiones HTTP
import json # Importamos json para manejar datos en formato JSON
import urllib.parse # Importamos urllib.parse para codificar URLs
import time # Importamos time para manejar tiempos de espera
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import jsonify


# Configuración general
HEADERS = {
    'x-rapidapi-key': "0caaf657damsh2c71a04c9c55bdap1ff046jsn9744079b4d84",
    'x-rapidapi-host': "tiktok-scraper7.p.rapidapi.com"
}

#Definimos constantes para la configuración de la captura de comentarios
MAX_COMENTARIOS_POR_VIDEO = 50 # Máximo de comentarios por video
CANTIDAD_VIDEOS = 20  # Número de videos por búsqueda
ESPERA_ENTRE_VIDEOS = 2 # Tiempo de espera entre capturas de videos
ESPERA_ENTRE_PAGINAS = 1 # Tiempo de espera entre páginas de comentarios

#Función para buscar videos por tema y tiempo de publicación
def buscar_videos_httpclient(tema, publish_time):
    tema_encoded = urllib.parse.quote(tema) # Codificamos el tema para la URL
    conn = http.client.HTTPSConnection("tiktok-scraper7.p.rapidapi.com") # Creamos una conexion HTTPS
    endpoint = f"/feed/search?keywords={tema_encoded}&region=es&count={CANTIDAD_VIDEOS}&cursor=0&publish_time={publish_time}&sort_type=0" # Definimos el endpoint de la API TikTok scraper
    conn.request("GET", endpoint, headers=HEADERS) # Realizamos la peticion a la API 
    res = conn.getresponse() # Obtenemos la respuesta de la API
    data = res.read() # Leemos los datos de la respuesta
    conn.close() # Cerramos la conexión
    
    try:
        json_data = json.loads(data.decode("utf-8")) # Decodificamos los datos JSON
        videos = json_data.get("data", {}).get("videos", []) # Obtenemos la lista de videos
        urls = [] # Lista para almacenar las URLs de los videos
        for v in videos:
            vid = v.get("video_id") # Obtenemos el ID del video
            user = v.get("author", {}).get("unique_id", "unknownuser") # Obtenemos el nombre de usuario del autor
            if vid:
                urls.append(f"https://www.tiktok.com/@{user}/video/{vid}") # Formamos la URL del video y la agregamos a la lista
        return urls # Retornamos la lista de URLs
    except Exception:
        return [] # En caso de error, retornamos una lista vacía
    
# Extraer nombre de usuario desde URL
def extraer_usuario_publicacion(url_video):
    try:
        partes = url_video.split('/') # Dividimos la URL por '/'
        return partes[3].lstrip('@') # Retornamos el nombre de usuario
    except:
        return "Desconocido" # En caso de error, retornamos "Desconocido"
    

# Función para obtener comentarios de un video
def obtener_comentarios_video(url_video, enfermedad):
    comentarios = [] # Lista para almacenar los comentarios
    cursor = 0 # Cursor para paginación
    total = 0 # Contador total de comentarios
    usuario_pub = extraer_usuario_publicacion(url_video) # Extraemos el nombre de usuario del video
    
    while total < MAX_COMENTARIOS_POR_VIDEO: # Mientras no se alcance el máximo de comentarios
        params = urllib.parse.urlencode({
            "url": url_video, # URL del video
            "count": str(MAX_COMENTARIOS_POR_VIDEO), # Máximo de comentarios a obtener
            "cursor": str(cursor) # Cursor para paginación
        })
        conn = http.client.HTTPSConnection("tiktok-scraper7.p.rapidapi.com") # Creamos una conexión HTTPS
        conn.request("GET", f"/comment/list?{params}", headers=HEADERS) # Realizamos la petición a la API
        res = conn.getresponse() # Obtenemos la respuesta
        data = res.read() # Leemos los datos de la respuesta
        conn.close() # Cerramos la conexión
        
        if res.status != 200: # Si la respuesta no es exitosa
            break # Salimos del bucle
        
        try:
            json_data = json.loads(data.decode("utf-8")) # Decodificamos los datos JSON
            coms = json_data.get("data", {}).get("comments", []) # Obtenemos los comentarios
        except:
            break # En caso de error, salimos del bucle
        
        for c in coms:
            comentarios.append({
                "user_post": usuario_pub, # Agregamos el nombre de usuario del video
                "user_postText": "Desconocido", # Texto de la publicación
                "user_comment": c.get("user", {}).get("nickname", "Desconocido"), # Nombre de usuario del comentario
                "user_commentText": c.get("text", ""), # Texto del comentario
                "enfermedad": enfermedad # Enfermedad asociada al comentario
            })
            total += 1 # Incrementamos el contador total de comentarios
            if total >= MAX_COMENTARIOS_POR_VIDEO:
                break # Si alcanzamos el máximo de comentarios se sale del bucle
            
        if not json_data.get("data", {}).get("has_more", False):
            break # Si no hay más comentarios, salimos del bucle
        cursor = json_data["data"].get("cursor", 0) # Actualizamos el cursor para la siguiente página
        time.sleep(ESPERA_ENTRE_PAGINAS) # Esperamos un tiempo antes de la siguiente petición
            
    time.sleep(ESPERA_ENTRE_VIDEOS) # Esperamos un tiempo antes de procesar el siguiente video
    return comentarios # Retornamos la lista de comentarios obtenidos



def buscar_videos_tiktok(enfermedad, publish_time):

    print(f" Procesando enfermedad: {enfermedad} | Tiempo publicación: {publish_time} " ) # Imprimimos el estado del procesamiento
    videos = buscar_videos_httpclient(enfermedad, publish_time) # Buscamos los videos relacionados con la enfermedad

    if not videos:
        return jsonify({"error": f"No se encontraron videos para '{enfermedad}'"}), 404 # Retornamos un error si no se encontraron videos

    resultados_tiktok = [] # Lista para almacenar los resultados de los comentarios

    tiempo_inicio = time.time() # Medimos el tiempo de ejecución de la captura de comentarios con hilos

    with ThreadPoolExecutor(max_workers=5) as executor: # Creamos un ThreadPoolExecutor para manejar concurrencia

        features = [executor.submit(obtener_comentarios_video, v, enfermedad) for v in videos] # Enviamos las tareas al executor

        for f in as_completed(features): # Iteramos sobre las tareas completadas
            try:
                resultados_tiktok.extend(f.result()) # Extendemos la lista de resultados con los comentarios obtenidos
            except Exception as e:
                print("Error en hilo:", e) # Imprimimos cualquier error que ocurra en los hilos

    tiempo_fin = time.time() # Tomamos el tiempo justo después de que terminan los hilos
    duracion = tiempo_fin - tiempo_inicio # Calculamos la duración total

    print(f"Tiempo de captura de comentarios (con hilos): {duracion:.2f} segundos") # Tiempo de la operación

    return resultados_tiktok


