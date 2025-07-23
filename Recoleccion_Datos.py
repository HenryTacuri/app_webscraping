from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains

import time
import random
import json
import ast
import pandas as pd
import re

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import spacy
from langdetect import detect

from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

import praw

#nltk.download('punkt')
#nltk.download('punkt_tab')
#nltk.download('stopwords')


# -------------------------------------------- Extracción del inforamación de Facebook ---------------------------------------------------


def datos_facebook():
        
    '''
    # --- Configuración básica ---
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    EMAIL = "
    PASSWORD = ""
    service = Service("C:/Users/HP VICTUS/Documents/Henry/vision_env/src/webscraping/chromedriver-win64/chromedriver.exe")
    browser = webdriver.Chrome(service=service, options=option)
    wait = WebDriverWait(browser, 30)

    # --- Login ---
    browser.get("https://es-la.facebook.com/")
    time.sleep(random.uniform(2, 4))  # Tiempo humano para "cargar la página"

    email_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
    # Simular tecleo humano lento
    for c in EMAIL:
        email_field.send_keys(c)
        time.sleep(random.uniform(0.09, 0.25))

    time.sleep(random.uniform(0.4, 1.2))

    pass_field = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
    for c in PASSWORD:
        pass_field.send_keys(c)
        time.sleep(random.uniform(0.09, 0.22))

    # Mueve el mouse al botón de login y haz clic (en vez de solo enviar RETURN)
    login_btn = browser.find_element(By.NAME, 'login')
    actions = ActionChains(browser)
    actions.move_to_element(login_btn).pause(random.uniform(0.5, 1.2)).click().perform()
    time.sleep(random.uniform(5, 8))

    # --- Buscar publicaciones sobre "ecuador" ---
    #browser.get('https://www.facebook.com/search/posts?q=Cancer%20Cerebral')
    #time.sleep(6)

    enfermedades = [
        "Cáncer cerebral", "Cáncer de estómago", "Cáncer al pulmón", 
        "Cáncer al hígado", "Dolor de estómago", "Enfermedad del asma",
        "Enfermedad de neumonía", "Enfermedad de laringitis", 
        "Enfermedad de bronquitis", "Fibrosis pulmonar",
        "Enfermedad de gastritis", "Enfermedad de gastroenteritis",
        "Cálculos biliares", "Alzheimer", "Enfermedad de la diabetes",
        "Insuficiencia cardiaca", "Enfermedad de hipertensión arterial"
    ]

    MAX_PUBLICACIONES_POR_ENFERMEDAD = 10  # Cambia a lo que desees

    data_facebooK = {}

    for enfermedad in enfermedades:
        print(f"\nBuscando publicaciones sobre: {enfermedad}")
        browser.get(f'https://www.facebook.com/search/posts?q={enfermedad}')
        time.sleep(6)

        publicaciones = []
        processed_posts = set()
        publicaciones_extraidas = 0

        MAX_SCROLLS = 30
        SCROLL_AMOUNT = 800  # píxeles por scroll
        DELAY_BETWEEN_SCROLLS = 2  # segundos

        for s in range(MAX_SCROLLS):
            print(f"[SCROLL {s+1}] Bajando página…")
            browser.execute_script(f"window.scrollBy(0, {SCROLL_AMOUNT});")
            time.sleep(DELAY_BETWEEN_SCROLLS)

            buttons = browser.find_elements(By.XPATH, "//div[@role='button' and @aria-label='Dejar un comentario']")
            print(f"  Encontrados {len(buttons)} botones para comentar.")

            for idx, btn in enumerate(buttons):
                # Obtener un ID de la publicación para evitar repetir
                try:
                    parent = btn.find_element(By.XPATH, "./ancestor::div[contains(@role, 'article')]")
                    post_id = parent.get_attribute("data-ft") or parent.get_attribute("id") or f"{enfermedad}_{idx}"
                except Exception:
                    post_id = f"{enfermedad}_{idx}"

                if post_id in processed_posts:
                    continue
                processed_posts.add(post_id)

                try:
                    # Desplazar hacia el botón y clic
                    browser.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                    time.sleep(1)
                    try:
                        btn.click()
                    except Exception:
                        browser.execute_script("arguments[0].click();", btn)
                    time.sleep(2)

                    # Esperar diálogo
                    try:
                        dialog = WebDriverWait(browser, 8).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                        )
                    except Exception:
                        print("No se pudo abrir el diálogo de comentarios")
                        continue

                    # Extraer usuario
                    usuario = "Desconocido"
                    try:
                        user_link = dialog.find_element(By.XPATH,
                            ".//a[contains(@aria-label, ', ver historia') or contains(@aria-label, ', ver perfil')]"
                        )
                        usuario = user_link.text.strip()
                        if not usuario:
                            span = user_link.find_element(By.XPATH, ".//span")
                            usuario = span.text.strip()
                    except Exception:
                        try:
                            usuario = dialog.find_element(By.XPATH, ".//strong/span").text.strip()
                        except Exception:
                            pass

                    # Extraer texto principal
                    try:
                        preview = dialog.find_element(
                            By.XPATH,
                            ".//div[@data-ad-preview='message']"
                        )
                        paragraphs = preview.find_elements(By.XPATH, ".//div[@dir='auto']")
                        full_text = "\n".join(
                            p.get_attribute("textContent").strip()
                            for p in paragraphs
                            if p.get_attribute("textContent").strip()
                        )
                    except Exception:
                        full_text = ""

                    print(f"\n---- Publicación {publicaciones_extraidas+1} ----")
                    print(f"Usuario: {usuario}")
                    print(full_text)

                    # Scroll y expandir comentarios
                    try:
                        scroll_areas = dialog.find_elements(By.XPATH, ".//div[contains(@class, 'x1i10hfl') and @role='dialog']//div[contains(@class,'scrollable') or contains(@class, 'x6s0dn4')]")
                        scroll_area = scroll_areas[0] if scroll_areas else dialog

                        num_scrolls = 10
                        for _ in range(num_scrolls):
                            browser.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 600;", scroll_area)
                            time.sleep(0.3)
                            # Ver más comentarios
                            try:
                                ver_mas = dialog.find_elements(By.XPATH, ".//span[contains(text(),'Ver más comentarios')]")
                                for btn2 in ver_mas:
                                    browser.execute_script("arguments[0].scrollIntoView({block:'center'});", btn2)
                                    btn2.click()
                                    time.sleep(0.2)
                            except Exception:
                                pass
                            # Ver las X respuestas
                            try:
                                ver_res = dialog.find_elements(By.XPATH, ".//span[contains(text(),'Ver las') and contains(text(),'respuestas')]")
                                for btn2 in ver_res:
                                    browser.execute_script("arguments[0].scrollIntoView({block:'center'});", btn2)
                                    btn2.click()
                                    time.sleep(0.2)
                            except Exception:
                                pass
                        time.sleep(0.7)
                    except Exception as e:
                        print("⚠️ Error al hacer scroll/expandir comentarios:", e)

                    # Extraer comentarios
                    comentarios = []
                    try:
                        comentarios_divs = dialog.find_elements(
                            By.XPATH,
                            ".//div[contains(@class, 'x1y1aw1k')]"
                        )
                        for div in comentarios_divs:
                            try:
                                nombre_usuario = "Desconocido"
                                try:
                                    nombre_elem = div.find_element(By.XPATH, ".//a[contains(@href,'facebook.com/')]/span")
                                    nombre_usuario = nombre_elem.text.strip()
                                except Exception:
                                    pass
                                spans = div.find_elements(By.XPATH, ".//span[@dir='auto']")
                                comentario = " ".join([s.text.strip() for s in spans if s.text.strip()])
                                if comentario:
                                    comentarios.append({"usuario": nombre_usuario, "comentario": comentario})
                            except Exception:
                                continue
                    except Exception as e:
                        print("⚠️ Error extrayendo comentarios:", e)

                    print("Comentarios extraídos:")
                    for c in comentarios:
                        print("-", c)

                    publicaciones.append({
                        "usuario": usuario,
                        "texto": full_text,
                        "comentarios": comentarios
                    })
                    publicaciones_extraidas += 1

                    # Cerrar diálogo
                    try:
                        close_btn = dialog.find_element(
                            By.XPATH,
                            ".//div[@aria-label='Cerrar' or @aria-label='Close']"
                        )
                        close_btn.click()
                    except Exception:
                        try:
                            dialog.send_keys(Keys.ESCAPE)
                        except Exception:
                            pass
                    time.sleep(1)

                except Exception as e:
                    print(f"  No se pudo abrir/comentar post {idx}: {e}")
                    # Intentar cerrar el diálogo si quedó abierto
                    try:
                        dialog = browser.find_element(By.XPATH, "//div[@role='dialog']")
                        dialog.send_keys(Keys.ESCAPE)
                    except Exception:
                        pass
                    time.sleep(1)
                    continue

                if publicaciones_extraidas >= MAX_PUBLICACIONES_POR_ENFERMEDAD:
                    print(f"Se alcanzó el máximo de {MAX_PUBLICACIONES_POR_ENFERMEDAD} publicaciones para '{enfermedad}'.")
                    break

            if publicaciones_extraidas >= MAX_PUBLICACIONES_POR_ENFERMEDAD:
                break

        # Guardar publicaciones de esta enfermedad
        data_facebooK[enfermedad] = publicaciones

    # Cerrar navegador
    browser.quit()


    # Guardar en JSON
    with open("publicaciones_facebook.json", "w", encoding="utf-8") as f:
        json.dump(data_facebooK, f, ensure_ascii=False, indent=4)

    print("\n✅ Datos guardados correctamente en publicaciones_facebook.json")
    '''

    # -------------------------------------------- De JSON a CSV ---------------------------------------------------

    with open("publicaciones_facebook.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for enfermedad, publicaciones in data.items():
        for pub in publicaciones:
            user_post = pub.get("usuario", "")
            text_post = pub.get("texto", "")
            comentarios = pub.get("comentarios", [])
            if not comentarios:
                rows.append({
                    "enfermedad": enfermedad,   # <<---- Aquí se agrega el campo
                    "user_comment": "",
                    "comment_text": "",
                    "user_post": user_post,
                    "text_post": text_post
                })
            else:
                for comentario in comentarios:
                    user_comment = comentario.get("usuario", "")
                    comment_text = comentario.get("comentario", "")
                    # Limpiar el usuario si aparece al inicio del comentario
                    if comment_text.lower().startswith(user_comment.lower()):
                        limpio = comment_text[len(user_comment):].lstrip(": ").lstrip()
                    else:
                        limpio = comment_text.replace(user_comment, "", 1).lstrip(":, ").lstrip()
                    rows.append({
                        "enfermedad": enfermedad,  # <<---- Aquí se agrega el campo
                        "user_comment": user_comment,
                        "comment_text": limpio,
                        "user_post": user_post,
                        "text_post": text_post
                    })

    df = pd.DataFrame(rows, columns=["enfermedad", "user_comment", "comment_text", "user_post", "text_post"])
    df.to_csv("publicaciones_facebook.csv", index=False, encoding="utf-8")
    print("✅ Listo, el dataset se guardó como publicaciones_facebook.csv")



    # -------------------------------------------- Preprocesamiento del texto ---------------------------------------------------


    # 1. Cargar tu CSV
    df = pd.read_csv("publicaciones_facebook.csv", encoding="utf-8")

    # 2. Definir función de limpieza
    def limpiar_texto(texto):
        if not isinstance(texto, str):
            return ""
        texto = texto.lower()
        texto = texto.replace("\\n", " ")
        texto = re.sub(r"http\S+|www\.\S+", "", texto)
        texto = re.sub(r"[@#]\w+", "", texto)
        texto = re.sub(r"[^\w\sñáéíóúü]", "", texto)
        texto = re.sub(r"\d+", "", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    # 3. Limpiar los textos
    df['comment_text_clean'] = df['comment_text'].apply(limpiar_texto)
    df['text_post_clean'] = df['text_post'].apply(limpiar_texto)

    # 4. Tokenizar
    df['tokens_comment'] = df['comment_text_clean'].apply(word_tokenize)
    df['tokens_post'] = df['text_post_clean'].apply(word_tokenize)

    # 5. Eliminar stopwords
    stop_words = set(stopwords.words('spanish'))
    df['tokens_comment_no_stop'] = df['tokens_comment'].apply(lambda tokens: [t for t in tokens if t not in stop_words])
    df['tokens_post_no_stop'] = df['tokens_post'].apply(lambda tokens: [t for t in tokens if t not in stop_words])

    # 6. Lemmatización
    nlp = spacy.load("es_core_news_sm")

    def lemmatizar(tokens):
        doc = nlp(" ".join(tokens))
        return [token.lemma_ for token in doc]

    df['lemma_comment'] = df['tokens_comment_no_stop'].apply(lemmatizar)
    df['lemma_post'] = df['tokens_post_no_stop'].apply(lemmatizar)

    # 7. Guardar resultados
    df_filtrado = df[['enfermedad',
                    'user_comment', 'comment_text', 'comment_text_clean', 'lemma_comment',
                    'user_post', 'text_post', 'text_post_clean', 'lemma_post']]


    # Quitar filas con NaN en las columnas de comentario
    df_filtrado = df_filtrado.dropna(subset=['comment_text', 'comment_text_clean'])

    #Quitar filas donde esos campos son strings vacíos o solo espacios
    df_filtrado = df_filtrado[
        (df_filtrado['comment_text'].str.strip() != '') &
        (df_filtrado['comment_text_clean'].str.strip() != '')
    ]


    # Guardar los archivos limpios
    df_filtrado.to_json("dataset_limpio_facebook.json", orient="records", force_ascii=False, indent=4)
    df_filtrado.to_csv("dataset_limpio_facebook.csv", index=False, encoding="utf-8-sig")

    print("✅ ¡Preprocesamiento completado y datasets guardados!")


# -------------------------------------------- Extracción del inforamación de Tiktok ---------------------------------------------------

def datos_tiktok():
    import requests
    import json
    import time

    # Título del video TikTok
    video_text = "Tips para el acné hormonal"

    MAX_COMENTARIOS = 200
    COMENTARIOS_POR_PAGINA = 50
    ESPERA_ENTRE_PETICIONES = 3

    url = "https://tiktok-scraper7.p.rapidapi.com/comment/list"
    headers = {
        "x-rapidapi-key": "42751bf4cbmsh998c65f354e4266p1cfd9ejsn856ccbb8dd73",
        "x-rapidapi-host": "tiktok-scraper7.p.rapidapi.com"
    }

    querystring = {
        "url": "https://www.tiktok.com/@animuslab/video/7381683979642047750",
        "count": str(COMENTARIOS_POR_PAGINA),
        "cursor": "0"
    }

    all_filtered_comments = []
    cursor = 0

    while len(all_filtered_comments) < MAX_COMENTARIOS:
        querystring["cursor"] = str(cursor)
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code != 200:
            print(f"Error {response.status_code}: No se pudo obtener los comentarios.")
            break
        
        data = response.json()
        try:
            comments = data["data"]["comments"]
        except KeyError:
            print("No se encontraron comentarios o formato inesperado.")
            break
        
        for c in comments:
            filtered = {
                "video_id": c.get("video_id"),
                "comment_id": c.get("id"),
                "comment_text": c.get("text"),
                "user_nickname": c.get("user", {}).get("nickname", "Desconocido"),
                "video_text": video_text
            }
            all_filtered_comments.append(filtered)
            
            if len(all_filtered_comments) >= MAX_COMENTARIOS:
                break

        print(f"Total acumulado: {len(all_filtered_comments)} comentarios")    

        if not data["data"].get("has_more"):
            print("No hay más comentarios disponibles.")
            break
        
        cursor = data["data"]["cursor"]
        time.sleep(ESPERA_ENTRE_PETICIONES)

    # Guardar en JSON
    with open("comentarios_tiktok.json", "w", encoding="utf-8") as f:
        json.dump(all_filtered_comments, f, ensure_ascii=False, indent=4)

    print("✅ Comentarios TikTok guardados exitosamente en 'comentarios_tiktok.json'")


def procesar_tiktok():
    import pandas as pd
    import re
    import nltk
    import spacy
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords

    # Leer los comentarios desde el JSON generado por datos_tiktok()
    with open("comentarios_tiktok.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # ---------------- LIMPIEZA ----------------
    def limpiar_texto(texto):
        if not isinstance(texto, str):
            return ""
        texto = texto.lower()
        texto = texto.replace("\\n", " ")
        texto = re.sub(r"http\S+|www\.\S+", "", texto)
        texto = re.sub(r"[@#]\w+", "", texto)
        texto = re.sub(r"[^\w\sñáéíóúü]", "", texto)
        texto = re.sub(r"\d+", "", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    df['comment_text_clean'] = df['comment_text'].apply(limpiar_texto)

    # tokenizacion
    df['tokens'] = df['comment_text_clean'].apply(word_tokenize)

    # stopwords
    stop_words = set(stopwords.words('spanish'))
    df['tokens_no_stop'] = df['tokens'].apply(lambda tokens: [t for t in tokens if t not in stop_words])

    # lematizacion
    nlp = spacy.load("es_core_news_sm")
    def lemmatizar(tokens):
        doc = nlp(" ".join(tokens))
        return [token.lemma_ for token in doc]

    df['tokens_lemma'] = df['tokens_no_stop'].apply(lemmatizar)

    # filtro filas vacias
    df_filtrado = df[[
        "video_text", "user_nickname", "comment_text", "comment_text_clean", "tokens_lemma"
    ]]

    df_filtrado = df_filtrado.dropna(subset=["comment_text", "comment_text_clean"])
    df_filtrado = df_filtrado[
        (df_filtrado["comment_text"].str.strip() != "") &
        (df_filtrado["comment_text_clean"].str.strip() != "")
    ]

    # guardataset
    df_filtrado.to_csv("dataset_limpio_tiktok.csv", index=False, encoding="utf-8-sig")
    df_filtrado.to_json("dataset_limpio_tiktok.json", orient="records", force_ascii=False, indent=4)

    print("✅ TikTok preprocesado y guardado en CSV y JSON")


# -------------------------------------------- Extracción del inforamación de Reddit ---------------------------------------------------

# === Configuración de Reddit API ===
reddit = praw.Reddit(
    client_id='jcEiqRik6wRwxQbof6_mGQ',
    client_secret='D4GOeGKuxsKPCOwPwXbbAGY0eiu1jQ',
    user_agent='buscador_medico'
)

# Lista de enfermedades y palabras indeseadas
palabras_clave = [
    "trastorno mental", "afección", "síndrome", "diagnóstico médico",
    "cáncer", "asma", "diabetes", "hipertensión", "epilepsia", "alzheimer",
    "ansiedad", "depresión", "migraña", "esclerosis múltiple", "artritis", "fibromialgia",
    "infección", "covid", "VIH", "hepatitis", "acné severo", "obesidad", "anemia",
    "esquizofrenia", "autismo", "dermatitis", "alergia", "gastritis"
]
palabras_irrelevantes = [
    "fumada", "locura", "poderes", "cruz", "hormigueo", "jajaja",
    "visión", "palmas", "epico"
]

# Función de extracción
def extract_reddit_json(output_path="reddit_enfermedades.json", limit_per_keyword=30, delay=2):
    resultados = []
    for palabra in palabras_clave:
        print(f"Buscando publicaciones con: {palabra}")
        posts = reddit.subreddit("all").search(palabra, limit=limit_per_keyword, sort="new")
        for post in posts:
            author = post.author.name if post.author else "[deleted]"
            text = post.title + "\n" + (post.selftext or "")
            try:
                if detect(text) != "es":
                    continue
            except:
                continue
            if not any(p in text.lower() for p in palabras_clave):
                continue
            try:
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    if comment.author is None or comment.author.name == "AutoModerator":
                        continue
                    c_text = comment.body
                    if any(p in c_text.lower() for p in palabras_irrelevantes):
                        continue
                    resultados.append({
                        "enfermedad_detectada": palabra,
                        "post_author": author,
                        "post_text": text,
                        "comment_author": comment.author.name,
                        "comment_text": c_text
                    })
            except Exception as e:
                print(f"Error procesando comentarios: {e}")
        time.sleep(delay)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"Extracción completada. Guardado en {output_path}")



# Tokenización y lematización
def process_reddit_json(input_path="reddit_enfermedades.json", csv_output="dataset_limpio_reddit.csv", json_output="datasetEnfermedades_limpio.json"):
    
    # Funciones de limpieza y procesamiento
    def limpiar_texto(texto):
        texto = texto.lower().replace("\n", " ")
        texto = re.sub(r"http\S+|www\.\S+", "", texto)
        texto = re.sub(r"[@#]\w+", "", texto)
        texto = re.sub(r"[^\w\sñáéíóúü]", "", texto)
        texto = re.sub(r"\d+", "", texto)
        return re.sub(r"\s+", " ", texto).strip()


    # Cargar datos
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # Limpieza de texto
    df['post_limpio'] = df['post_text'].apply(limpiar_texto)
    df['coment_limpio'] = df['comment_text'].apply(limpiar_texto)

    # Descargar recursos NLTK
    stop_words = set(stopwords.words('spanish'))

    # Tokenización
    df['post_tokens'] = df['post_limpio'].apply(word_tokenize)
    df['coment_tokens'] = df['coment_limpio'].apply(word_tokenize)

    # Remover stopwords
    df['post_tokens_sinstopwords'] = df['post_tokens'].apply(lambda toks: [t for t in toks if t not in stop_words and len(t)>2])
    df['coment_tokens_sinStopwords'] = df['coment_tokens'].apply(lambda toks: [t for t in toks if t not in stop_words and len(t)>2])

    # Lematización
    nlp = spacy.load("es_core_news_sm")
    def lemmatizar(tokens):
        if not tokens:
            return []
        doc = nlp(" ".join(tokens))
        return [tok.lemma_ for tok in doc if tok.is_alpha]
    df['post_tokens_lemma'] = df['post_tokens_sinstopwords'].apply(lemmatizar)
    df['coment_tokens_lemma'] = df['coment_tokens_sinStopwords'].apply(lemmatizar)

    # Exportar JSON con listas reales
    df[['enfermedad_detectada','post_author','post_limpio','post_tokens_lemma',
        'comment_author','coment_limpio','coment_tokens_lemma']].to_json(json_output, orient="records", force_ascii=False, indent=4)
    # Preparar CSV (tokens a string)
    df_fil = df[['enfermedad_detectada','post_author','post_limpio',
                 'post_tokens_lemma','comment_author','coment_limpio','coment_tokens_lemma']].copy()
    df_fil['post_tokens_lemma'] = df_fil['post_tokens_lemma'].apply(lambda x: " ".join(x) if isinstance(x,list) else "")
    df_fil['coment_tokens_lemma'] = df_fil['coment_tokens_lemma'].apply(lambda x: " ".join(x) if isinstance(x,list) else "")
    df_fil.to_csv(csv_output, index=False, encoding='utf-8-sig')
    print(f"Procesamiento completado. CSV: {csv_output}, JSON: {json_output}")

    # Nube de palabras
    '''corpus = pd.concat([df['post_tokens_lemma'].explode(), df['coment_tokens_lemma'].explode()]).dropna().tolist()
    conteo = Counter(corpus)
    print("20 palabras más comunes:", conteo.most_common(20))
    wc_text = " ".join(corpus)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(wc_text)
    plt.figure(figsize=(12,6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Nube de palabras de publicaciones y comentarios')
    plt.show()'''



if __name__ == "__main__":

    datos_facebook()


    extract_reddit_json()
    process_reddit_json()


    datos_tiktok()
    procesar_tiktok()

    
    print("Bolsa de palabras")

    df_facebook = pd.read_csv('dataset_limpio_facebook.csv')
    df_tiktok = pd.read_csv('dataset_limpio_tiktok.csv')
    df_reddit = pd.read_csv('dataset_limpio_reddit.csv')

    comentariosFacebook = df_facebook['lemma_comment'].apply(ast.literal_eval)

    comentariosFacebook = comentariosFacebook.explode().dropna().tolist()


    comentariosReddit = df_reddit['coment_tokens_lemma'].str.split()

    comentariosReddit = comentariosReddit.explode().dropna().tolist()


    comentariosTiktok = df_tiktok['tokens_lemma'].apply(ast.literal_eval)

    comentariosTiktok = comentariosTiktok.explode().dropna().tolist()


    comentarios = comentariosTiktok + comentariosFacebook + comentariosReddit

    conteo_palabras = Counter(comentarios)
    top100 = conteo_palabras.most_common(100)

    # Ahora lo guardamos en un archivo .txt
    with open('top100_palabras.txt', 'w', encoding='utf-8') as f:
        for palabra, frecuencia in top100:
            # Cada línea: palabra, tabulación, frecuencia
            f.write(f"{palabra}\t{frecuencia}\n")

    print("Top 100 Palabras - Bolsa de palabras guardada en top100_palabras.tx")


    # Crear nube de palabras
    texto_para_wordcloud = " ".join(comentarios)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto_para_wordcloud)

    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Nube de palabras de los comentarios")
    plt.savefig('nube_palabras.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Top 100 Palabras - Nube de palabras guarda en nube_palabras.png")




