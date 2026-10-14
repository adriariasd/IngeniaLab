# Guía de uso del repositorio

Este documento establece cómo trabajar con Git y GitHub en el proyecto **IngeniaLab** del equipo Byte Force. Todos los integrantes deben seguir estas reglas para mantener el repositorio ordenado, revisar los cambios y evitar conflictos.

## 1. Estructura del repositorio

| Carpeta / archivo | Contenido                                                                 |
| ----------------- | ------------------------------------------------------------------------- |
| `ingenialab/`     | Proyecto Django (código, plantillas, datos semilla y `requirements.txt`). |
| `docs/`           | Documentación entregable (Manual de Usuario, Guía de Operación, etc.).    |
| `README.md`       | Descripción general del repositorio.                                      |

Los comandos de Django de esta guía se ejecutan desde la carpeta `ingenialab/`.

## 2. Ramas del repositorio

| Rama          | Propósito                                                              | Uso                                                                   |
| ------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `main`        | Versión estable del proyecto, la que se entrega al cierre de cada iteración. | Solo recibe cambios desde la rama de iteración mediante un Pull Request. |
| `it-N`        | Rama de integración de la iteración en curso (por ejemplo, `it-2`).    | Rama base para iniciar el trabajo y destino de los Pull Requests.     |
| Ramas de tarea | Trabajo de una sola tarea (funcionalidad, corrección, documento).     | Se crean desde `it-N` y se eliminan después de integrarse.            |

**Regla principal:** no se suben cambios directamente a `main` ni a la rama de iteración. Todo cambio entra mediante un Pull Request revisado.

Al iniciar una nueva iteración, el responsable del repositorio crea la rama `it-N` a partir de `main` y avisa al equipo.

## 3. Crear una rama para cada tarea

Antes de trabajar en una tarea, crea una rama propia a partir de la rama de iteración vigente:

```bash
git checkout it-2
git pull origin it-2
git checkout -b feature/entrevistas-reinicio
```

Qué hace cada comando:

1. `git checkout it-2`: cambia a la rama de la iteración.
2. `git pull origin it-2`: actualiza tu copia local con los cambios del remoto.
3. `git checkout -b feature/entrevistas-reinicio`: crea una rama nueva y cambia a ella.

### Nombres de rama

Usa el formato `tipo/descripcion`, en minúsculas y con palabras separadas por guiones:

| Prefijo     | Uso                                         | Ejemplo                            |
| ----------- | ------------------------------------------- | ---------------------------------- |
| `feature/`  | Funcionalidad nueva.                        | `feature/cu-01-chat-entrevista`    |
| `fix/`      | Corrección de un error.                     | `fix/puntaje-entrevista`           |
| `docs/`     | Documentación (`docs/`, README, manuales).  | `docs/manual-usuario-v1-1`         |
| `refactor/` | Reorganización de código sin cambiar comportamiento. | `refactor/servicios-inspeccion` |
| `test/`     | Pruebas automatizadas.                      | `test/modeling-validator`          |

Si la tarea corresponde a un caso de uso o requisito del SRS, inclúyelo en el nombre (por ejemplo, `cu-01`). Cada rama debe corresponder a una sola tarea.

## 4. No subir cambios directamente a `main`

La rama `main` representa el estado estable y entregable del proyecto. Está prohibido hacer `push` directamente a ella:

```bash
# No hagas esto
git push origin main
```

Lo mismo aplica a la rama de iteración (`it-N`): los cambios llegan a ella solo mediante Pull Requests.

## 5. Enviar los cambios mediante un Pull Request

Cuando termines tu tarea, guarda tus cambios en commits y sube la rama:

```bash
git push origin feature/entrevistas-reinicio
```

Después, abre un Pull Request en GitHub:

1. Abre el repositorio en GitHub.
2. Crea un Pull Request desde tu rama de tarea.
3. Selecciona tu rama como origen y la rama de iteración (`it-N`) como destino.
4. Describe qué cambiaste, por qué, y cómo probarlo.
5. Solicita la revisión de otro integrante del equipo.
6. Atiende los comentarios y corrige los problemas señalados.
7. Con al menos **una aprobación**, el autor del Pull Request lo integra con **Merge pull request** y elimina la rama de tarea.

**Importante:** comprueba que la rama de destino sea `it-N`, no `main`.

Si hay conflictos, resuélvelos en tu rama de tarea (ver sección 8) antes de solicitar nuevamente la revisión.

### Cierre de iteración: de `it-N` a `main`

Al terminar la iteración, el responsable del repositorio:

1. Abre un Pull Request de `it-N` hacia `main`.
2. Verifica que las pruebas pasen y que el proyecto arranque.
3. Lo integra con la aprobación del equipo.
4. Crea una etiqueta de versión, por ejemplo:

```bash
git checkout main
git pull origin main
git tag -a v1.0 -m "Cierre de iteración 2"
git push origin v1.0
```

**Evita revertir Pull Requests directamente en `main`.** Si algo se integró por error, corrígelo en la rama de iteración. Un revert en `main` hace que esos cambios no vuelvan a entrar cuando se integre `it-N` más adelante.

## 6. Flujo de trabajo

```text
main
  |
  v
Crear rama de iteración it-N (al inicio de la iteración)
  |
  v
Crear rama de tarea desde it-N
  |
  v
Realizar cambios y crear commits
  |
  v
Subir la rama a GitHub
  |
  v
Abrir un Pull Request hacia it-N
  |
  v
Revisión y aprobación
  |
  v
Integrar en it-N y eliminar la rama de tarea
  |
  v
Al cierre de la iteración: Pull Request de it-N a main + etiqueta de versión
```

## 7. Convención para los mensajes de commit

Los mensajes de commit deben explicar con claridad qué cambio se realizó. Evita mensajes vagos como `cambios`, `fix`, `update` o `asdf`.

### Formato

```text
Verbo en infinitivo + descripción del cambio
```

Reglas:

- Empieza con un verbo en infinitivo y mayúscula inicial: `Agregar`, `Corregir`, `Actualizar`, `Crear`, `Eliminar`, `Refactorizar`, `Documentar`.
- Describe el cambio concreto.
- No uses punto final.
- Procura que la primera línea tenga menos de 72 caracteres.
- Si necesitas explicar más, deja una línea en blanco y agrega el detalle en el cuerpo del commit.
- Si aplica, menciona el caso de uso o requisito entre paréntesis.

### Ejemplos correctos

```text
Agregar reinicio de entrevista con confirmación (CU-01)
Corregir cálculo de puntaje máximo en entrevistas
Actualizar Django a 5.1.7
Crear pruebas para ModelingValidator
Documentar variable INGENIALAB_MODULES en el README
```

### Ejemplos incorrectos

```text
cambios
fix
Implementa lógica de entrevistas.
avance del proyecto
```

## 8. Lista de verificación antes de abrir un Pull Request

- [ ] Mi rama está actualizada con los cambios recientes de `it-N`.
- [ ] El proyecto arranca sin errores con `python manage.py runserver`.
- [ ] Las pruebas pasan con `python manage.py test apps`.
- [ ] Si modifiqué modelos, incluí las migraciones (`python manage.py makemigrations`).
- [ ] Revisé `git status` y no incluyo archivos locales, secretos ni generados (`.venv/`, `db.sqlite3`, `var/`, `vendor/*.jar`).
- [ ] Mis commits tienen mensajes claros y siguen la convención.
- [ ] El Pull Request tiene como destino `it-N`, no `main`.
- [ ] La descripción del Pull Request explica los cambios y cómo probarlos.

Comandos útiles (desde `ingenialab/`):

```bash
git status
.venv/bin/python manage.py test apps
.venv/bin/python manage.py runserver
```

Para actualizar tu rama de tarea con los cambios recientes de la iteración, ejecuta desde tu rama:

```bash
git fetch origin
git merge origin/it-2
```

Si aparecen conflictos, resuélvelos, vuelve a correr las pruebas y haz commit del resultado antes de continuar.

## 9. Resumen de reglas

1. Crea una rama por tarea a partir de la rama de iteración vigente (`it-N`).
2. Nombra las ramas como `tipo/descripcion`, en minúsculas.
3. Escribe commits claros con un verbo en infinitivo.
4. Sube tu rama y abre un Pull Request hacia `it-N`.
5. Integra solo con al menos una aprobación y elimina la rama después.
6. Nunca hagas `push` directo a `main` ni a `it-N`.
7. `main` solo recibe la rama de iteración al cierre, con una etiqueta de versión.

Si surge una situación no contemplada en esta guía, consulta al responsable del repositorio antes de modificar el flujo de trabajo.
