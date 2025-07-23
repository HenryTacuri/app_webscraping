
**Integrantes:**

* Franklin Guapisaca
* Juan Quizhpi
* Henry Tacuri

### **🚀 Ejecución del Proyecto**

Para ejecutar correctamente el proyecto, se deben seguir los pasos detallados a continuación:

---

### **🔧 Instalación de dependencias para la aplicación Angular (Frontend)**

1. Abrir una terminal en la carpeta del proyecto llamada `webscraping_frontend`.

2. Ejecutar el siguiente comando para instalar todas las dependencias necesarias:

   ```bash
   npm install
   ```

---

### **⚙️ Preparación del Backend en Python**

1. Crear un entorno virtual de Python.

2. Ubicar la carpeta del backend llamada `api` y copiarla dentro de una nueva carpeta llamada `src` (la cual debe ser creada).

3. Abrir una terminal en la raíz del entorno virtual de Python.

4. Copiar el archivo requirements.txt a la raíz del entorno de Python.

5. Instalar las dependencias ejecutando el siguiente comando dentro del entorno:

   ```bash
   pip install -r requirements.txt
   ```

6. Dentro de la carpeta del backend (`src/api`), copiar la carpeta `bert_emociones_finetuned`. Esta carpeta es generada previamente en un cuaderno de Jupyter (Modelo.ipynb) y contiene todo el proceso de entrenamiento del modelo de IA. Dentro de ella se encuentra el modelo BERT ya entrenado y listo para ser utilizado.

---

### **🟢 Inicio del Frontend y Backend**

1. En una terminal ubicada en la carpeta del frontend, ejecutar el siguiente comando para iniciar la aplicación Angular:

   ```bash
   ng serve -o
   ```

2. En otra terminal, activar el entorno virtual de Python y ejecutar el backend con el siguiente comando:

   ```bash
   python src/api/api_recoleccion_datos.py
   ```

---


### **Recolección de datos para entrenar el modelo de IA**

Para ejecutar la recolección de datos realizada en la práctica anterior ejecutamos el archivo de python ```Recoleccion_Datos.py```.

Una vez ejecutado el archivo como resultado obtendremos 3 datasets que ya están procesados y listos para utilizar en el modelo de IA, estos datasets son: ```dataset_limpio_facebook``` - ```dataset_limpio_tiktok``` - ```dataset_limpio_reddit```.


Por último se unen todos los datasets