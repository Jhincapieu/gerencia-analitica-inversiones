
# Herramienta Analítica - Gerencia de Inversiones Bancolombia

Este proyecto fue desarrollado como parte del reto técnico para la gerencia analítica de inversiones de Valores Bancolombia. La herramienta permite visualizar información clave del portafolio de inversión de los clientes, facilitando el análisis por cliente, banca y perfil de riesgo.

## 📊 Funcionalidades

- Evolución del ABA promedio con opción de proyección a 6 meses.
- Composición del portafolio por cliente (macroactivo y activo).
- Composición por banca y por perfil de riesgo.
- Filtros interactivos para fechas, clientes y segmentos.

## 🛠️ Tecnologías utilizadas

- Python
- Dash y Plotly
- PostgreSQL
- Pandas y scikit-learn

## 🧪 Instrucciones para ejecutar

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/gerencia-analitica-inversiones.git
   cd gerencia-analitica-inversiones
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Asegúrate de tener PostgreSQL ejecutando localmente, y de haber creado las tablas y cargado los datos según los scripts del archivo `prueba.py`.

4. Ejecuta la aplicación:
   ```bash
   python app/prueba.py
   ```

5. Abre tu navegador en `http://127.0.0.1:8050` para interactuar con el dashboard.

## 🎥 Video demostrativo

Puedes encontrar el video demo en este mismo repositorio como `video_demo.mp4`.

## ⚠️ Notas importantes

- **No se incluyen los archivos .csv originales** por solicitud expresa de la prueba.
- La aplicación está diseñada para ejecutarse localmente con conexión a una base de datos PostgreSQL configurada por el usuario.

---

## 📁 Estructura del proyecto

```
gerencia-analitica-inversiones/
│
├── app/
│   └── prueba.py
├── requirements.txt
├── README.md
├── video_demo.mp4
└── .gitignore
```
