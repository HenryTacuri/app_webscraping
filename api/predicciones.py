
import ast
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from transformers import BertTokenizerFast, BertForSequenceClassification
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from openai import OpenAI

client = OpenAI(api_key='')


tokenizer = None
model = None
emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'negative', 'neutral', 'positive', 'surprise', 'trust']

resumen = None



class EmocionDataset(Dataset):

    global tokenizer

    def __init__(self, texts, tokenizer, max_len=128):
        self.enc = tokenizer(
            list(texts),
            padding="max_length",
            truncation=True,
            max_length=max_len,
            return_tensors="pt"
        )
    def __len__(self):
        return len(self.enc['input_ids'])
    def __getitem__(self, i):
        return {k: v[i] for k, v in self.enc.items()}
    

def parse_lemma(x):
    if isinstance(x, list):
        return x
    if pd.isna(x):
        return []
    try:
        return ast.literal_eval(x)
    except Exception:
        return []
    

def cargar_modelo():

    global tokenizer, model

    model_dir = "src/webscraping/api/data/bert_emociones_finetuned"
    tokenizer = BertTokenizerFast.from_pretrained(model_dir)
    model = BertForSequenceClassification.from_pretrained(model_dir)


def graficar_emociones(df_total_publicaciones):

    global resumen

    resumen = (
        df_total_publicaciones.groupby("enfermedad")["pred_emocion"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
    )

    colores = {
        "anger": "#e74c3c", "fear": "#8e44ad", "negative": "#34495e",
        "neutral": "#95a5a6", "positive": "#2ecc71", "surprise": "#f1c40f", "trust": "#3498db"
    }

    resumen = resumen[[c for c in colores.keys() if c in resumen.columns]]


    resumen.plot(
        kind='barh', stacked=True, figsize=(10, 6),
        color=[colores.get(col, "#7f8c8d") for col in resumen.columns]
    )

    plt.title("Distribución de emociones por enfermedad", fontsize=14)
    plt.xlabel("Proporción")
    plt.ylabel("Enfermedad")
    plt.legend(title="Emoción", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.savefig('src/webscraping/api/static/estadisticas.png', dpi=300, bbox_inches='tight')
    plt.close()


def realzar_preddiccione(df_total_publicaciones, enfermedad):

    cargar_modelo()

    global tokenizer, model, emotions


    df_total_publicaciones['lemma_comment'] = df_total_publicaciones['lemma_comment'].apply(parse_lemma)
    df_total_publicaciones['text'] = df_total_publicaciones['lemma_comment'].apply(lambda x: " ".join(x).strip())
    df_total_publicaciones = df_total_publicaciones[df_total_publicaciones['text'].str.strip() != ""]
    df_total_publicaciones = df_total_publicaciones.dropna(subset=['text', 'enfermedad'])


    test_ds = EmocionDataset(df_total_publicaciones['text'].values, tokenizer)
    loader = DataLoader(test_ds, batch_size=32)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()

    preds = []

    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            logits = outputs.logits
            batch_preds = torch.argmax(logits, dim=1).cpu().numpy()
            preds.extend(batch_preds)

    # Asigna emociones predichas
    df_total_publicaciones['pred_emocion'] = [emotions[i] for i in preds]

    graficar_emociones(df_total_publicaciones)


    global resumen

    dist = resumen.loc[enfermedad].to_dict()
    explicacion = explicar_distribucion(dist, enfermedad)

    return explicacion


def explicar_distribucion(emociones_dict, enfermedad):
    prompt = (
        f"Se ha realizado un análisis de emociones en comentarios sobre la enfermedad '{enfermedad}'. "
        f"La distribución es la siguiente: {emociones_dict}. "
        "Redacta en español un breve análisis del estado emocional general de las personas y posibles razones."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].message.content



def bolsa_palabras(df_total_publicaciones):

    # Aplica la conversión solo cuando es necesario
    comentarios_limpios = df_total_publicaciones['lemma_comment'].apply(parse_lemma)

    # Concatena todas las palabras en una sola lista
    total_comentarios = comentarios_limpios.explode().dropna().tolist()

    texto_para_wordcloud = " ".join(total_comentarios)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto_para_wordcloud)

    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Nube de palabras de los comentarios")
    plt.savefig('src/webscraping/api/static/bolsa_palabras.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Top 100 Palabras - Nube de palabras guarda en nube_palabras.png")

    return True

