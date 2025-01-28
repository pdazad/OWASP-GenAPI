# OWASP-GENAPI

OWASP-GENAPI es una API diseñada para procesar consultas en lenguaje natural relacionadas con los riesgos de seguridad definidos en el OWASP Top 10. Este proyecto utiliza un modelo de lenguaje Bloom fine-tuned alojado en Hugging Face ([pdazad/fine_tuned_bloom_owasp](https://huggingface.co/pdazad/fine_tuned_bloom_owasp)), con recuperación de contexto basada en FAISS y un pipeline eficiente implementado bajo principios de arquitectura limpia.

---

## Estructura del Proyecto

El proyecto está organizado siguiendo los principios de **Clean Architecture**, segmentando responsabilidades en diferentes capas para facilitar el mantenimiento y la escalabilidad.

```plaintext
OWASP-GENAPI/
├── api/
│   ├── main.py                 # Punto de entrada principal para la API (FastAPI/Nest.js).
│
├── application/
│   ├── use_cases/
│   │   ├── handle_inference_use_case.py  # Lógica de aplicación para manejar inferencias.
│
├── config/
│   ├── settings.py             # Configuraciones globales del proyecto.
│
├── data/
│   ├── model/
│   │   ├── indice_faiss.index
│   │   ├── owasp_cleaned_dataset.json
│   │   ├── OWASP/              # Datos de OWASP preprocesados.
│
├── domain/
│   ├── entities/
│   │   ├── query_entity.py     # Entidad para modelar las consultas de inferencia.
│   │   ├── response_entity.py  # Entidad para modelar las respuestas generadas.
│   ├── interfaces/
│       ├── inference_service_interface.py # Interfaz para el servicio de inferencia.
│
├── infrastructure/
│   ├── helpers/
│   │   ├── context_utils.py    # Truncamiento y manejo de contexto con TF-IDF.
│   │   ├── faiss_helper.py     # Funciones para búsqueda en FAISS.
│   │   ├── response_formatter.py # Formateo de respuestas del modelo.
│   ├── repository/
│       ├── inference_service_impl.py  # Implementación del servicio de inferencia.
│
├── scripts/
│   ├── model/
│   │   ├── inference.py        # Inferencia usando el modelo fine-tuned.
│   │   ├── train_model.ipynb   # Notebook de fine-tuning de BLOOM-560m.
│   ├── reports/
│       ├── clean_qa_dataset.py
│       ├── evaluate_models.ipynb
│
├── .env                        # Configuración de variables de entorno.
├── Dockerfile                  # Definición del contenedor Docker.
├── docker-compose.yml          # Configuración para Docker Compose.
├── README.md                   # Documentación del proyecto.
├── requirements.txt            # Dependencias del proyecto.
└── test_main.http              # Pruebas para endpoints de la API.
```

---

## Tecnologías Utilizadas

- **Hugging Face Transformers**: Modelo Bloom fine-tuned para generación de texto.
- **FAISS**: Recuperación eficiente de contexto basado en embeddings.
- **FastAPI/Nest.js**: Framework para construir la API.
- **Docker**: Contenedorización del proyecto para despliegue.
- **Python**: Lógica central del modelo y helpers.
- **Google Cloud Run**: Para despliegue en la nube.

---

## Instalación y Configuración

### Requisitos Previos

- Docker y Docker Compose instalados.
- Python 3.8+.
- Cuenta en Hugging Face para acceder al modelo.

### Configuración

1. Clonar el repositorio:

    ```bash
    git clone https://github.com/user/owasp-genapi.git
    cd owasp-genapi
    ```

2. Crear un entorno virtual:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. Instalar dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4. Configurar variables de entorno en el archivo `.env`:

    ```plaintext
    MODEL_PATH=pdazad/fine_tuned_bloom_owasp
    INDEX_PATH=./data/model/indice_faiss.index
    PROCESSED_DATA_PATH=./data/model/owasp_cleaned_dataset.json
    EMBEDDING_MODEL_NAME=all-MiniLM-L12-v2
    TOP_K=3
    ```

### Construcción del Contenedor Docker

1. Construir el contenedor:

    ```bash
    docker build -t owasp-api-gateway .
    ```

2. Ejecutar con Docker Compose:

    ```bash
    docker-compose up
    ```

---

## Descripción de Componentes

### 1. **API (FastAPI/Nest.js)**

- Define los endpoints principales.
- Maneja peticiones y respuestas HTTP.
- Punto de entrada: `api/main.py`.

### 2. **Capa de Aplicación**

- Contiene casos de uso como `handle_inference_use_case.py`.
- Orquesta la lógica principal de las consultas de inferencia.

### 3. **Dominio**

- Modela entidades principales como `QueryEntity` y `ResponseEntity`.
- Define interfaces claras en `inference_service_interface.py`.

### 4. **Infraestructura**

- Helpers para:
  - Manejo de contexto con `context_utils.py`.
  - Recuperación eficiente con `faiss_helper.py`.
  - Formateo de respuestas con `response_formatter.py`.
- Implementación del servicio en `inference_service_impl.py`.

### 5. **Modelo e Inferencia**

- Scripts relacionados con el entrenamiento (`train_model.ipynb`) y la inferencia (`inference.py`).
- Índice FAISS y datasets enriquecidos en `data/model`.

---

### Modelo e Inferencia

#### Fine-Tuning del Modelo
El modelo utilizado en este proyecto está basado en **BLOOM-560m**, un modelo generativo desarrollado por Hugging Face. Este modelo fue ajustado específicamente para responder preguntas relacionadas con los riesgos de seguridad del OWASP Top 10.

- **Entrenamiento:**
  - Se unieron datos de preguntas y respuestas (QA) con un conjunto de datos procesados y enriquecidos sobre OWASP.
  - Los datos fueron limpiados y procesados para eliminar etiquetas innecesarias y mantener el contenido relevante.
  - Se generaron embeddings usando el modelo `all-MiniLM-L12-v2` de **Sentence Transformers** para indexarlos con FAISS, lo que facilita la búsqueda de contexto relevante para cada pregunta.

- **Optimización:**
  - Se emplearon técnicas como Fine-Tuning con **Hugging Face Transformers** y **DataCollator** para ajustar el modelo.
  - Los mejores hiperparámetros se determinaron mediante validación con métricas como `eval_loss`.

#### Inferencia
El modelo inferencial se integra con un índice FAISS para recuperar documentos relevantes. El flujo de inferencia sigue estos pasos:

1. **Consulta en lenguaje natural:**
   El usuario proporciona una pregunta, por ejemplo: `¿Qué es el control de acceso roto?`.

2. **Búsqueda de contexto:**
   - La consulta se transforma en embeddings usando el modelo `all-MiniLM-L12-v2`.
   - Se busca en el índice FAISS para recuperar los documentos más relevantes.
   - Se optimiza el contexto usando TF-IDF, asegurando que las secciones más relevantes se incluyan dentro del límite de 512 tokens.

3. **Generación de Respuestas:**
   - El modelo genera una respuesta a partir de la consulta y el contexto proporcionado.
   - La respuesta es procesada para eliminar contenido irrelevante y truncada hasta el último punto completo para garantizar claridad.

#### Evaluación
El rendimiento del modelo se evaluó con preguntas de prueba y métricas de calidad como **ROUGE-L** para medir la similitud entre las respuestas generadas y las esperadas.

---

## Ejecución del Proyecto

### 1. **Iniciar la API**

```bash
docker-compose up
```

La API estará disponible en: `http://localhost:8000`.

### 2. **Endpoint Principal**

**POST /predict**

- **Entrada:**

    ```json
    {
        "query": "¿Qué es el control de acceso roto?"
    }
    ```

- **Salida:**

    ```json
    {
        "response": "El control de acceso roto ocurre cuando...",
        "time": "(Tiempo de ejecución para generar la respuesta en segundos)"
    }
    ```

---

## Contribuciones

1. Realizar un fork del repositorio.
2. Crear una rama para tu feature:

    ```bash
    git checkout -b feature/nueva-funcionalidad
    ```

3. Realizar un pull request con los cambios.

---

## Créditos

Este proyecto utiliza modelos finetuned de Hugging Face: [pdazad/fine_tuned_bloom_owasp](https://huggingface.co/pdazad/fine_tuned_bloom_owasp).
