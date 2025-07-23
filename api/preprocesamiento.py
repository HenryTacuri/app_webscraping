import pandas as pd
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from multiprocessing import Pool, cpu_count
import re


def limpiar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().replace("\\n", " ")
    texto = re.sub(r"http\S+|www\.\S+", "", texto)
    texto = re.sub(r"[@#]\w+", "", texto)
    texto = re.sub(r"[^\w\sñáéíóúü]", "", texto)
    texto = re.sub(r"\d+", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


nlp = None

def init_worker():

    global nlp
    # Solo tokenización + lematización, sin parser ni NER
    nlp = spacy.load("es_core_news_sm", disable=["parser", "ner"])
    # Aseguramos stopwords descargadas (solo en el main process)
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)

def worker(row_stopwords):

    row, stop_words = row_stopwords

    # Post
    post_text = limpiar_texto(row.get("user_postText", ""))
    tokens_post = [
        t for t in word_tokenize(post_text)
        if t not in stop_words and len(t) > 2
    ]
    lemma_post = [
        tok.lemma_ for tok in nlp(" ".join(tokens_post))
        if tok.is_alpha
    ] if tokens_post else []

    # Comentario
    comment_text = limpiar_texto(row.get("user_commentText", ""))
    tokens_comment = [
        t for t in word_tokenize(comment_text)
        if t not in stop_words and len(t) > 2
    ]
    lemma_comment = [
        tok.lemma_ for tok in nlp(" ".join(tokens_comment))
        if tok.is_alpha
    ] if tokens_comment else []

    return {
        "enfermedad":    row.get("enfermedad", ""),
        "user_post":     row.get("user_post", ""),
        "lemma_post":    lemma_post,
        "user_comment":  row.get("user_comment", ""),
        "lemma_comment": lemma_comment
    }

def procesar_lista_dataset_multiproceso(lista_rows):

    # Si recibe DataFrame, lo convertimos a lista de dicts
    if isinstance(lista_rows, pd.DataFrame):
        lista_rows = lista_rows.to_dict(orient="records")

    # Preparamos stopwords (se copiarán a cada worker)
    stop_words = set(stopwords.words("spanish"))

    # Empaquetamos args igual que antes
    args = [(row, stop_words) for row in lista_rows]

    # Número de procesos
    n_proc = min(cpu_count(), max(2, len(args) // 10))

    # Creamos el Pool con init_worker
    with Pool(processes=n_proc, initializer=init_worker) as pool:
        resultados = pool.map(worker, args)

    return pd.DataFrame(resultados)
