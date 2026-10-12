# Guía paso a paso: correr el sistema en Visual Studio Code

Esta guía está pensada para alguien que nunca ha corrido un programa. Ve paso por paso, sin saltarte ninguno.
Cuando veas un cuadro gris con texto, eso es un **comando**: lo copias, lo pegas en la terminal y presionas **Enter**.

---

## Paso 0. ¿Qué vamos a hacer?

El sistema tiene dos partes:

- **El cerebro (backend):** un programa en Python que guarda la información y habla con la IA.
- **La cara (frontend):** la página web donde escribes los procedimientos.

Vamos a encender el cerebro, y él solito nos mostrará la página web.

---

## Paso 1. Instalar los programas necesarios (sólo la primera vez)

Necesitas 3 programas. Si ya los tienes, pasa al Paso 2.

### 1.1 Python
1. Entra a https://www.python.org/downloads/
2. Presiona el botón amarillo **Download Python 3.12** (o la versión más nueva que aparezca).
3. Abre el archivo que se descargó.
4. ⚠️ **MUY IMPORTANTE (Windows):** antes de presionar "Install Now", marca la casilla de abajo que dice
   **"Add python.exe to PATH"**. Si no la marcas, nada funcionará.
5. Presiona **Install Now** y espera a que termine.

### 1.2 Git
1. Entra a https://git-scm.com/downloads
2. Descarga la versión para tu computadora e instálala.
3. En todas las pantallas del instalador puedes presionar **Next** sin cambiar nada.

### 1.3 Visual Studio Code
1. Entra a https://code.visualstudio.com/
2. Descárgalo e instálalo (también presiona **Next** en todo).

---

## Paso 2. Abrir Visual Studio Code y prepararlo

1. Abre **Visual Studio Code** (lo llamaremos "VS Code").
2. Del lado izquierdo hay una barra con iconos. Haz clic en el icono de **cuadritos** (se llama *Extensions* / Extensiones).
3. En el buscador escribe **Python** e instala la que dice **Python — Microsoft** (botón azul *Install*).

---

## Paso 3. Descargar el proyecto a tu computadora

1. En VS Code ve al menú de arriba: **Terminal → New Terminal** (Terminal → Nueva terminal).
   Abajo aparecerá una ventanita negra o blanca: esa es **la terminal**. Ahí se escriben los comandos.
2. Copia y pega este comando para ir a tu carpeta de Documentos:

   ```
   cd ~/Documents
   ```

3. Ahora descarga el proyecto:

   ```
   git clone https://github.com/Oliver-Cruz/Manuales-MOP.git
   ```

   Si te pide iniciar sesión en GitHub, hazlo con tu usuario.

4. Abre la carpeta del proyecto en VS Code: menú **File → Open Folder…** (Archivo → Abrir carpeta),
   busca **Documentos → Manuales-MOP** y presiona **Seleccionar carpeta**.
   Si VS Code pregunta *"¿Confías en los autores?"*, responde **Yes, I trust the authors**.

> 💡 Mientras el Pull Request no esté aprobado, el código vive en una rama aparte. Para verlo escribe en la terminal:
> ```
> git checkout claude/procedure-audit-system-ianj1z
> ```
> Cuando el PR ya esté aprobado (merge), no necesitas este paso.

---

## Paso 4. Entrar a la carpeta del "cerebro"

1. Abre otra vez la terminal (**Terminal → New Terminal**).
2. Escribe:

   ```
   cd backend
   ```

   Ahora estás "dentro" de la carpeta `backend`.

---

## Paso 5. Crear una "cajita" para el proyecto (entorno virtual)

Piensa en el entorno virtual como una **lonchera**: guarda sólo las cosas que este proyecto necesita, sin revolverlas con las de otros.

**En Windows:**
```
python -m venv .venv
```

**En Mac:**
```
python3 -m venv .venv
```

Ahora hay que **abrir la lonchera** (activarla):

**En Windows:**
```
.venv\Scripts\activate
```

**En Mac:**
```
source .venv/bin/activate
```

✅ Sabrás que funcionó porque al inicio de la línea de la terminal aparece **(.venv)**.

> 😟 **¿En Windows te sale un error rojo que dice "la ejecución de scripts está deshabilitada"?**
> Escribe este comando, presiona Enter y vuelve a intentar activar:
> ```
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> Si te pregunta algo, escribe **S** (o **Y**) y Enter.

---

## Paso 6. Meter las herramientas en la lonchera

Escribe:

```
pip install -r requirements.txt
```

Va a descargar varias cosas. Espera a que vuelva a aparecer la línea con **(.venv)** (puede tardar 1–3 minutos).

---

## Paso 7. Darle la "llave" de la IA

La IA (Claude) necesita una **llave secreta** (API key) para funcionar. Es como la contraseña del Wi-Fi.

### 7.1 Conseguir la llave
1. Entra a https://console.anthropic.com/ e inicia sesión (o crea una cuenta).
2. Ve a **API Keys** → **Create Key**.
3. Ponle un nombre (por ejemplo "Manuales MOP") y copia la llave. Empieza con `sk-ant-...`.
   ⚠️ Guárdala bien: sólo se muestra una vez. **No se la compartas a nadie** ni la subas a GitHub.
4. Tu cuenta debe tener saldo/créditos para que la IA conteste.

### 7.2 Guardar la llave en el proyecto
1. Copia el archivo de ejemplo:

   **En Windows:**
   ```
   copy .env.example .env
   ```

   **En Mac:**
   ```
   cp .env.example .env
   ```

2. En el panel izquierdo de VS Code abre la carpeta **backend** y haz clic en el archivo **.env**.
3. Cambia la primera línea para que quede con tu llave:

   ```
   ANTHROPIC_API_KEY=sk-ant-aquí-va-tu-llave-completa
   ```

4. Guarda el archivo con **Ctrl + S** (en Mac **Cmd + S**).

> El archivo `.env` está en la lista de "ignorados", así que **nunca** se sube a GitHub. 👍

---

## Paso 8. ¡Encender el sistema! 🚀

En la terminal (que debe seguir mostrando **(.venv)** y estar en la carpeta `backend`) escribe:

```
uvicorn app.main:app --reload
```

✅ Funcionó si ves algo parecido a:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

⚠️ **No cierres esta terminal**: mientras esté abierta, el sistema está encendido.

---

## Paso 9. Abrir la página y usarla

1. Abre tu navegador (Chrome, Edge…) y entra a: **http://localhost:8000/**
2. Arriba elige el **Área** (Finanzas, Operaciones o Recursos Humanos).
3. Escribe el **Nombre del procedimiento** (y el código si lo tienes).
4. Llena los cuadros de la **izquierda** (Objetivo, Descripción de actividades, etc.).
5. Presiona **Guardar y auditar con IA**.
6. Espera (puede tardar de 30 segundos a un par de minutos). Verás a la **derecha** el feedback de cada sección:
   - 🟢 **Cumple**, 🟡 **Parcial**, 🔴 **No cumple**, ⚪ **Vacía**
   - Qué **le hace falta**, qué **inconsistencias** tiene y una **sugerencia**.
7. Si te gusta la sugerencia, presiona **"Usar sugerencia en el texto ↩"**: se copia al cuadro de la izquierda para que la ajustes.
8. Corrige lo que haga falta y vuelve a presionar **Guardar y auditar con IA**. ¡Repite hasta que todo quede en verde!

Para abrir un procedimiento guardado antes, usa el selector **Procedimiento existente** de arriba.

> 🧪 Extra: en **http://localhost:8000/docs** puedes ver y probar todos los "botones" internos del sistema (la API).

---

## Paso 10. Apagar el sistema

En la terminal donde está corriendo, presiona **Ctrl + C**. Listo, se apagó.

---

## Paso 11. La próxima vez (cuando ya instalaste todo)

Sólo haces esto:

1. Abre VS Code con la carpeta **Manuales-MOP**.
2. **Terminal → New Terminal**
3. Escribe:

   **Windows:**
   ```
   cd backend
   .venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

   **Mac:**
   ```
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload
   ```

4. Abre **http://localhost:8000/** en el navegador.

---

## 🆘 Si algo sale mal

| Lo que ves | Qué significa | Cómo arreglarlo |
|---|---|---|
| `python no se reconoce como un comando` | Python no se instaló bien o falta la casilla "Add to PATH" | Reinstala Python marcando **Add python.exe to PATH** y cierra/abre VS Code |
| `No module named ...` | La lonchera (.venv) no está activada | Repite el Paso 5 (activar) y luego el Paso 6 |
| `uvicorn no se reconoce` | Igual: la lonchera no está activada | Verifica que aparezca **(.venv)** al inicio de la línea |
| `Could not import module "app.main"` | No estás dentro de la carpeta `backend` | Escribe `cd backend` y vuelve a intentar |
| `address already in use` / puerto 8000 ocupado | Ya hay otro sistema encendido | Cierra la otra terminal, o usa `uvicorn app.main:app --reload --port 8001` y entra a http://localhost:8001/ |
| En la página: **"No hay credenciales de Anthropic configuradas"** | Falta la llave | Revisa el Paso 7 y **reinicia** el sistema (Ctrl + C y otra vez `uvicorn ...`) |
| En la página: **"API key de Anthropic inválida"** | La llave está mal copiada | Vuelve a copiarla completa en `.env`, sin espacios ni comillas |
| En la página: **"No se pudo conectar con el backend"** | El sistema está apagado | Haz el Paso 8 |
| La página se ve sin colores | No hay internet (los estilos se descargan de internet) | Conéctate a internet y recarga la página |

> 🔄 ¿Quieres empezar de cero con la base de datos? Apaga el sistema y borra el archivo `backend/manuales_mop.db`. Al encenderlo se crea uno nuevo y vacío.
