import praw
import json
import time
import os
from langdetect import detect
from datetime import datetime
from multiprocessing import Pool, cpu_count

# Palabras irrelevantes
palabras_irrelevantes = [
    "fumada", "locura", "poderes", "cruz", "hormigueo", "jajaja", "visión", "palmas", "epico"
]

# Configurar conexión a Reddit
def configurar_reddit():
    return praw.Reddit(
        client_id='cC7pvAry_jG8EGab6ZGg-Q',            # ← Coloca tu client_id real
        client_secret='keGRAhP7zMqouiwTGPnvrA6PoxuoUw',          # ← Coloca tu client_secret real
        user_agent='buscador_medico'
    )

# Función para buscar publicaciones de una enfermedad
def buscar_enfermedad(params):
    palabra, anio_filtrado, max_resultados = params
    reddit = configurar_reddit()
    resultados = []

    print(f"[PID {os.getpid()}] Buscando: {palabra}")
    time.sleep(2)

    try:
        posts = reddit.subreddit("all").search(palabra, limit=200, sort="new")
    except Exception as e:
        print(f"[{palabra}] Error al buscar publicaciones: {type(e).__name__} - {e}")
        return resultados

    for post in posts:
        if len(resultados) >= max_resultados:
            break

        fecha_post = datetime.utcfromtimestamp(post.created_utc)
        if fecha_post.year != anio_filtrado:
            continue

        post_author = post.author.name if post.author else "[deleted]"
        post_text = post.title + "\n" + (post.selftext or "")

        try:
            if detect(post_text) != "es":
                continue
        except:
            continue

        try:
            post.comments.replace_more(limit=0)
            for comment in post.comments.list():
                if len(resultados) >= max_resultados:
                    break

                if comment.author is None or comment.author.name == "AutoModerator":
                    continue

                comment_text = comment.body

                if any(p in comment_text.lower() for p in palabras_irrelevantes):
                    continue

                resultados.append({
                    "enfermedad": palabra,
                    "user_post": post_author,
                    "user_postText": post_text,
                    "user_comment": comment.author.name,
                    "user_commentText": comment_text
                })

        except Exception as e:
            print(f"[{palabra}] Error al procesar comentarios: {type(e).__name__} - {e}")

    return resultados


# Función principal que puedes importar y llamar desde otro archivo
def extraer_publicaciones_reddit(enfermedad, anio, publicaciones):

    print(enfermedad, anio, publicaciones)
    start = time.time()

    print(f"\nRecolectando datos de '{enfermedad}' para el año {anio} (máximo {publicaciones} publicaciones)...")

    # Ejecutar búsqueda en paralelo (aunque sea solo una enfermedad, por estructura)
    with Pool(processes=1) as pool:
        resultados = pool.map(buscar_enfermedad, [(enfermedad, anio, publicaciones)])

    resultados_json = resultados[0][:publicaciones]  


    print(f"\nExtracción completada con {len(resultados_json)} resultados.")
    print(f"Tiempo total: {round(time.time() - start, 2)} segundos\n")


    return resultados_json