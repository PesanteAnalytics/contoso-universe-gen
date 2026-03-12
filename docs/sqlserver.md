# SQL Server

> Guía completa para usar CUG con SQL Server: prerequisitos, autenticación, mapeo de tipos y troubleshooting.

---

## Prerequisitos

### SQL Server

CUG es compatible con:

- **SQL Server Express** 2017+ (ideal para desarrollo local)
- **SQL Server Developer** 2017+
- **SQL Server Standard/Enterprise** 2017+
- **Azure SQL Database**
- **Azure SQL Managed Instance**

### Driver ODBC

CUG necesita un driver ODBC para conectarse a SQL Server. Se auto-detecta el mejor disponible.

**Drivers soportados (en orden de preferencia):**

| Driver | Notas |
|--------|-------|
| ODBC Driver 18 for SQL Server | Más reciente. Requiere SSL/TLS (manejado automáticamente) |
| ODBC Driver 17 for SQL Server | Ampliamente disponible. Recomendado |
| SQL Server Native Client 11.0 | Legacy, funcional |

### Verificar drivers instalados

```python
import pyodbc
print(pyodbc.drivers())
# Output ejemplo: ['ODBC Driver 17 for SQL Server', 'SQL Server']
```

### Instalar ODBC Driver (si falta)

Descargar desde: [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

## Autenticación

CUG soporta tres métodos de autenticación:

### Windows Authentication (recomendado para desarrollo)

```toml
[output.format_options]
sqlserver_server  = "localhost\\SQLEXPRESS"
sqlserver_trusted = true    # default
```

```bash
cug generate -f sqlserver --sqlserver-name "localhost\SQLEXPRESS"
```

Usa las credenciales del usuario de Windows actual. No necesita usuario/contraseña.

### SQL Authentication

```toml
[output.format_options]
sqlserver_server   = "mi-servidor.database.windows.net"
sqlserver_trusted  = false
sqlserver_username = "mi_usuario"
sqlserver_password = "mi_password"
```

Para servidores remotos o Azure SQL.

### Connection String Completa

```toml
[output.format_options]
sqlserver_connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=ContosoRetail;Trusted_Connection=yes"
```

Sobreescribe todas las demás opciones de conexión. Útil para configuraciones avanzadas.

---

## Opciones de Configuración

### En el archivo TOML

```toml
[output.format_options]
sqlserver_server            = "localhost\\SQLEXPRESS"  # Instancia SQL Server
sqlserver_database          = "ContosoRetail"          # Base de datos destino
sqlserver_schema            = "dbo"                     # Esquema destino
sqlserver_driver            = "ODBC Driver 17 for SQL Server"  # Auto-detectado si se omite
sqlserver_trusted           = true                      # Windows Auth (default)
sqlserver_username          = ""                        # Solo para SQL Auth
sqlserver_password          = ""                        # Solo para SQL Auth
sqlserver_if_exists         = "replace"                 # replace | append | fail
sqlserver_batch_size        = 5000                      # Filas por INSERT batch
sqlserver_connection_string = ""                        # ODBC string completa (override)
```

### Via CLI

| Flag CLI | Equivalente TOML | Default |
|----------|-----------------|---------|
| `--sqlserver-name` | `sqlserver_server` | `localhost` |
| `--sqlserver-db` | `sqlserver_database` | `ContosoRetail` |
| `--sqlserver-schema` | `sqlserver_schema` | `dbo` |
| `--sqlserver-mode` | `sqlserver_if_exists` | `replace` |

---

## Comportamiento del Writer

El writer de SQL Server ejecuta los siguientes pasos:

1. **Crea la base de datos** automáticamente si no existe (conecta a `master` primero)
2. **Crea/reemplaza tablas** con tipos correctamente mapeados
3. **Inserta datos en batch** usando `pyodbc.fast_executemany` para alto rendimiento
4. **Fallback automático** a inserción fila por fila si `fast_executemany` falla en alguna tabla

### Modos `if_exists`

| Modo | Descripción |
|------|-------------|
| `replace` | Elimina la tabla existente y la recrea (default) |
| `append` | Agrega filas a la tabla existente |
| `fail` | Error si la tabla ya existe |

---

## Mapeo de Tipos: Polars → SQL Server

| Tipo Polars | Tipo SQL Server | Notas |
|-------------|----------------|-------|
| `Int8` | `TINYINT` | |
| `Int16` | `SMALLINT` | |
| `Int32` | `INT` | |
| `Int64` | `BIGINT` | |
| `UInt8` | `SMALLINT` | SQL Server no tiene unsigned → se promueve |
| `UInt16` | `INT` | SQL Server no tiene unsigned → se promueve |
| `UInt32` | `BIGINT` | SQL Server no tiene unsigned → se promueve |
| `UInt64` | `BIGINT` | SQL Server no tiene unsigned → se promueve |
| `Float32` | `REAL` | |
| `Float64` | `FLOAT` | |
| `String` | `NVARCHAR(400)` | Unicode, 400 caracteres máximo |
| `Categorical` | `NVARCHAR(200)` | |
| `Boolean` | `BIT` | Se convierte a `1`/`0` internamente |
| `Date` | `DATE` | |
| `Datetime` | `DATETIME2` | |
| `Time` | `TIME` | |
| `Duration` | `BIGINT` | Almacenado como microsegundos |
| `Binary` | `VARBINARY(MAX)` | |
| `Decimal` | `DECIMAL(19,4)` | |
| `Null` | `NVARCHAR(1) NULL` | Columnas donde todos los valores son `None` |

---

## Ejemplos

### Caso 1: SQL Server Express local (el más común)

```bash
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail
```

### Caso 2: Parquet + SQL Server simultáneamente

```bash
cug generate -n 50000 -f parquet,sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoDemo
```

### Caso 3: Schema personalizado

```bash
cug generate -n 100000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db MiBase \
  --sqlserver-schema staging
```

### Caso 4: Append a tabla existente

```bash
cug generate -n 50000 -f sqlserver \
  --sqlserver-name "localhost\SQLEXPRESS" \
  --sqlserver-db ContosoRetail \
  --sqlserver-mode append
```

---

## Troubleshooting

### ❌ Error: `DataError` con `fast_executemany`

**Síntoma:** Error al insertar datos en alguna tabla con `fast_executemany`.

**Solución:** CUG lo maneja automáticamente. Si `fast_executemany` falla en un batch, hace fallback a inserción fila por fila. Verás un warning en la consola pero la generación continuará.

**Causa raíz:** Tipos mixtos o edge cases en ciertas columnas que `fast_executemany` no maneja bien.

---

### ❌ Caracteres corruptos (CJK/Unicode) en columnas de texto

**Síntoma:** Los caracteres chinos (中文), japoneses (日本語) o árabes (العربية) aparecen como `?` o caracteres basura en SQL Server.

**Causa:** Configuración manual de encoding en la conexión.

**Solución:** **No** configurar `conn.setencoding(encoding="utf-8")` manualmente. SQL Server usa UTF-16LE internamente y `pyodbc` en Windows lo maneja correctamente por defecto. Forzar UTF-8 **corrompe** los datos `NVARCHAR`.

> [!CAUTION]
> **Nunca** usar `conn.setencoding(encoding="utf-8")` con pyodbc en Windows. Es la causa #1 de corrupción de datos Unicode en SQL Server.

---

### ❌ Error de conexión con ODBC Driver 18

**Síntoma:** `[Microsoft][ODBC Driver 18 for SQL Server]SSL Provider: The target principal name is incorrect`

**Causa:** El Driver 18 requiere certificado SSL válido por defecto.

**Solución:** CUG agrega automáticamente `TrustServerCertificate=yes` cuando detecta el Driver 18. Si usas `sqlserver_connection_string`, agrégalo manualmente:

```
...;TrustServerCertificate=yes
```

---

### ❌ Boolean → BIT casting

**Síntoma:** Error al insertar valores `True`/`False` en columnas `BIT`.

**Solución:** CUG convierte automáticamente `True` → `1` y `False` → `0` antes de la inserción. Esto es requerido por `pyodbc.fast_executemany`.

---

### ❌ Small integers (Int8/UInt8) con ODBC

**Síntoma:** Error de tipo al insertar valores `Int8` o `UInt8`.

**Solución:** CUG convierte automáticamente estos tipos a `int` nativo de Python antes de la inserción. `pyodbc` no maneja bien los enteros de NumPy/Polars de tamaño pequeño.

---

### ❌ No se puede crear la base de datos automáticamente

**Síntoma:** `Could not auto-create database: ...`

**Causa:** El usuario no tiene permisos `CREATE DATABASE` en la instancia.

**Solución:** Crear la base de datos manualmente:

```sql
CREATE DATABASE ContosoRetail;
```

CUG imprimirá un warning pero continuará intentando conectarse a la base de datos.

---

### ❌ `ImportError: No module named 'pyodbc'`

**Solución:**

```bash
pip install pyodbc
```

Si falla en Windows, instalar [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

---

## Entorno del Usuario (referencia)

Esta es la configuración de SQL Server en la máquina del desarrollador:

| Elemento | Valor |
|----------|-------|
| **Server** | `localhost\SQLEXPRESS` |
| **Versión** | SQL Server Express 2019 |
| **Auth** | Windows Authentication |
| **ODBC Driver** | ODBC Driver 17 for SQL Server |
| **Python** | 3.12+ con entorno `uv` |

---

← [Esquema de Datos](esquema-datos.md) | [Recetas Rápidas →](recetas.md)
