# 🚀 TurboLauncher: RAG Document Intelligence

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-000000?style=for-the-badge&logo=pinecone)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

**TurboLauncher** es un motor de búsqueda y respuesta inteligente basado en **RAG (Retrieval-Augmented Generation)**. Permite a los usuarios cargar archivos PDF, procesarlos para extraer su conocimiento y realizar consultas en lenguaje natural, obteniendo respuestas precisas y contextualmente relevantes basadas exclusivamente en sus documentos personales.

---

## 🐳 Despliegue con Docker Compose (Recomendado)

La forma más rápida y robusta de levantar el proyecto es utilizando **Docker**. Esto garantiza que todas las dependencias (Python, librerías de PDF, seguridad) se configuren automáticamente en un entorno aislado.



### 1. Requisitos
* Tener instalado [Docker Desktop](https://www.docker.com/products/docker-desktop/).
* Un archivo `.env` en la raíz con tus credenciales.

### 2. Archivo `docker-compose.yml`
Asegúrate de tener un archivo llamado `docker-compose.yml` con la siguiente configuración:

| Parámetro | Descripción |
| :--- | :--- |
| **Persistencia** | Los datos de usuarios (`iachatbot.db`) y los PDFs se guardan en tu PC. |
| **Aislamiento** | La API corre en el puerto 8000 dentro y fuera del contenedor. |
| **Auto-restart** | El servicio se reinicia automáticamente si falla. |

### 3. Comandos para iniciar
Desde la terminal en la carpeta del proyecto:

```bash
# Construir la imagen y levantar el servicio en segundo plano
docker compose up -d --build

# Ver el estado del contenedor
docker ps

# Ver los logs en tiempo real (para depuración)
docker logs -f turbolauncher-app

--

## ✨ Características Principales

* 🔐 **Seguridad Avanzada**: Implementación de autenticación OAuth2 con tokens JWT y hashing de contraseñas mediante Bcrypt.
* 📄 **Procesamiento de PDF**: Extracción automatizada de texto y limpieza de caracteres especiales.
* 🧠 **Embeddings de Nueva Generación**: Uso del modelo `text-embedding-3-small` de OpenAI con 1024 dimensiones para una representación semántica superior.
* ⚡ **Búsqueda Vectorial**: Almacenamiento e indexación en **Pinecone** para una recuperación de información en milisegundos.
* 🤖 **GPT-4o Integration**: Generación de respuestas utilizando el modelo más reciente de OpenAI, limitándose estrictamente al contexto proporcionado.
* 👤 **Privacidad Multi-usuario**: Filtros de búsqueda basados en metadatos para asegurar que cada usuario acceda solo a su propia información.

---

## 🛠️ Stack Tecnológico

| Herramienta | Función |
| :--- | :--- |
| **FastAPI** | Framework principal para la construcción de la API REST. |
| **OpenAI API** | Generación de embeddings vectoriales y respuestas con GPT-4o. |
| **Pinecone** | Base de datos vectorial para el almacenamiento de chunks. |
| **SQLite** | Gestión persistente de cuentas de usuario y credenciales. |
| **LangChain** | Segmentación inteligente de texto (RecursiveCharacterTextSplitter). |
| **Jose/JWT** | Firma y validación de tokens de acceso seguros. |

---

## 🏗️ Flujo de Trabajo (Arquitectura)

1.  **Registro/Login**: El usuario se autentica para obtener un token de acceso.
2.  **Carga de PDF**: Se sube un archivo, el cual se divide en fragmentos (chunks) con solapamiento para no perder contexto.
3.  **Vectorización**: Cada fragmento se convierte en un vector numérico mediante la API de OpenAI.
4.  **Indexación**: Los vectores se suben a Pinecone junto con metadatos (ID de usuario, página, nombre del archivo).
5.  **Consulta RAG**: Al preguntar, el sistema busca los 5 fragmentos más similares en Pinecone y los envía a GPT-4o como contexto para generar la respuesta.

---

## 📂 Estructura del Código

* `main.py`: Orquestador de la aplicación y definición de rutas (endpoints).
* `auth.py`: Lógica de seguridad, creación y validación de tokens.
* `pdf_processing.py`: Herramientas de extracción, limpieza y chunking de documentos.
* `db_pinecone.py`: Conector y cliente para la base de datos vectorial.
* `database.py`: Gestión de la base de datos local SQLite.
* `openai_utils.py`: Funciones para interactuar con los modelos de OpenAI.

---

## 🚀 Configuración Inicial

### Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto con las siguientes claves:
```env
OPENAI_API_KEY="sk-..."
PINECONE_API_KEY="tu_api_key_de_pinecone"