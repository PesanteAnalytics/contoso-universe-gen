# 🚀 Plan de Publicación Comunitaria — Contoso Universe Generator

> **Fecha**: 2026-03-12 (actualizado)
> **Versión actual**: v0.2.0
> **Objetivo**: Evaluar si CUG está listo para hacerse público, y definir el plan de acción con prioridades

---

## 📊 Veredicto: ¿Está Listo?

### 🟡 CASI LISTO — Necesita trabajo focalizado antes de publicar

CUG tiene una base técnica **sólida y funcional**, pero tiene gaps significativos que una comunidad open-source notará inmediatamente. Publicar en su estado actual arriesga una primera impresión mediocre que es difícil de revertir.

**Estimación de esfuerzo**: ~2-3 días de trabajo enfocado para Fases A+B+C.

---

## ✅ Lo que YA está excelente (Fortalezas para la comunidad)

| #   | Fortaleza                            | Evidencia                                                               |
| --- | ------------------------------------ | ----------------------------------------------------------------------- |
| 1   | **Motor funcional y estable**        | 14 tests pasan, v0.2.0                                                  |
| 2   | **7 formatos de salida**             | Parquet, CSV, DuckDB, Delta, JSON, Excel, SQL Server — más que DG V2    |
| 3   | **8 idiomas**                        | EN, ES, PT, FR, DE, ZH, JA, AR — feature killer vs DG V2                |
| 4   | **YAML plugin system**               | 4 categorías builtin + sistema extensible sin tocar código              |
| 5   | **Documentación interna exhaustiva** | MANUAL.md (443 líneas), 10 docs técnicos, SKILL.md (570 líneas)         |
| 6   | **Legal impecable**                  | MIT License + NOTICE.md explícito sobre independencia de DG V2          |
| 7   | **Validación FK**                    | `--verify` + `--strict` — calidad de datos garantizada                  |
| 8   | **Stack moderno**                    | Polars + DuckDB + Faker + Pydantic v2 + Typer + Rich                    |
| 9   | **Configuración flexible**           | TOML + CLI flags + CUG-CONFIG.md (agent-driven)                         |
| 10  | **CLI profesional**                  | `cug generate`, `cug formats`, `cug categories`, `cug info`, `cug init` |

---

## 🔴 Bloqueadores Críticos (Must-Fix antes de publicar)

### B1: README.md insuficiente para open-source

> [!CAUTION]
> El README actual tiene 96 líneas. Describe features pero **no cuenta la historia** del proyecto. Para la comunidad, el README ES el proyecto.

**Lo que tiene:**
- Features table ✅
- Quick start ✅
- Output schema básico ✅
- Badges (Python, Polars, DuckDB) ✅

**Lo que falta:**
- Descripción clara del problema que resuelve y por qué existe ("Why CUG?")
- Screenshots o GIFs del output (terminal Rich → primera impresión visual)
- Tabla comparativa con Contoso DG V2 (existe en `docs/planning/contoso_comparison_strategy.md` pero NO está en README)
- Ejemplo de output real (star schema diagram, tabla de datos)
- Sección de contribución (link a un futuro `CONTRIBUTING.md`)
- Badge de tests/CI (no hay CI configurado aún)
- Link a documentación completa (`docs/`)
- Tono: cambiar `"God-level"` por algo profesional pero memorable

### B2: No existe `CONTRIBUTING.md`

Un proyecto público sin guía de contribución señala "no queremos PRs". Necesita:

- Cómo configurar el entorno de desarrollo (`uv pip install -e ".[dev]"`)
- Cómo correr los tests (`pytest tests/ -v`)
- Cómo crear category plugins (enlace a `docs/category-plugins.md`)
- Code style (ruff config ya existe en `pyproject.toml`)
- Proceso de PR / Issues

### B3: No hay CI/CD (GitHub Actions)

Sin CI, cualquier PR puede romper el proyecto sin que nadie lo detecte. Mínimo:

- Tests en push/PR a `main`
- Linting (`ruff check cug/`)
- Badge de estado en README

### B4: Cobertura de tests insuficiente

**14 tests en un solo archivo (`test_smoke.py`)** es muy poco para la complejidad del proyecto. Falta cobertura en áreas críticas:

| Área            | Tests existentes                         | Tests faltantes                                                |
| --------------- | ---------------------------------------- | -------------------------------------------------------------- |
| Config loading  | 2 (load + override)                      | TOML parsing con formatos específicos, validación de errores   |
| Generators      | 5 (date, currency, customer, product, store) | Edge cases: 0 órdenes, 1 orden, valores límite                |
| Writers         | 2 (delta null cast, duckdb views)        | CSV writer, parquet writer, JSON writer, Excel writer          |
| Engine          | 2 (seeder, temporal)                     | Weights, full orchestration, integridad FK                     |
| CLI             | 0                                        | `--help`, formato inválido, config inexistente                 |
| i18n            | 3 (locale count, en locale, fallback)    | Cada idioma end-to-end, traducciones en categorías             |
| Sales generator | 0                                        | **Test más crítico**: ventas con diferentes escalas            |

### B5: Bug conocido — Escalado desproporcional en volúmenes bajos

> [!WARNING]
> En la sesión de diagnóstico (conversación `cfaf9902`) se identificó que pedir 100 órdenes genera ~50,000 clientes y ~36,888 exchange rates. Esto es un bug visible que cualquier usuario va a encontrar inmediatamente.

**Estado del fix**: Se aplicó auto-scale para `pool_size` y Poisson sampling, pero necesita **verificación cuantitativa** con al menos 3 escalas (100, 1000, 10000 órdenes) para confirmar que las proporciones son razonables.

### B6: Versión inconsistente entre código y documentación

> [!WARNING]
> `pyproject.toml` dice `version = "0.2.0"` y `cug/__init__.py` dice `__version__ = "0.2.0"`, pero documentación interna y planes previos referencian "v0.2.2". Esto debe unificarse antes de publicar.

---

## 🟡 Mejoras Importantes (Should-Fix antes de publicar)

### M1: `pyproject.toml` — Metadata para PyPI

Falta metadata estándar para publicación profesional:

- `[project.urls]` (Homepage, Repository, Documentation, Bug Tracker)
- `description` más profesional (quitar "God-level")
- Classifiers adicionales (`Topic :: Scientific/Engineering`, `Intended Audience :: Developers`)

### M2: Archivos privados que NO deben publicarse

Los siguientes archivos son internos del equipo PAL o generados por agentes:

| Archivo / Directorio                | Razón de exclusión                    | Acción              |
| ----------------------------------- | ------------------------------------- | ------------------- |
| `.agents/`                          | Políticas y planes de agente PAL      | `.gitignore`        |
| `.agent/skills/`                    | SKILL.md específico del agente        | Evaluar showcase    |
| `CUG-CONFIG.md`                     | Workflow de agente, no usuario final  | Evaluar showcase    |
| `configs/_session.toml`             | Archivo temporal de sesión            | `.gitignore`        |
| `configs/contoso-workspace.code-workspace` | Local IDE config               | `.gitignore`        |
| `analysis/eda.py`                   | Script interno                        | Excluir o mover     |
| `build_dashboard_data.py`           | Script interno en raíz del proyecto   | Excluir o mover     |
| `err.txt`, `out.txt`               | Logs temporales (ya en .gitignore)    | Eliminar archivos   |
| `docs/planning/`                    | Planes internos, no docs de usuario   | Excluir del release |

### M3: `.gitignore` incompleto

Falta ignorar:
- `.agents/` — planes y políticas PAL
- `.agent/` — skills del agente
- `configs/_session.toml` — sesión temporal
- `configs/*.code-workspace` — configuración local IDE

### M4: Schema inconsistencia entre docs y código

El `test_smoke.py` usa columnas como `GivenName`, `Surname`, `Company` y `Price`, mientras que `docs/planning/schema_comparison_v2_vs_cug.md` documenta `FirstName`, `LastName` y `UnitPrice`/`UnitCost`. Hay que verificar cuáles son los nombres reales en los generators y alinear la documentación.

### M5: El `docs/planning/cug_master_plan.md` está desactualizado

Todas las tareas de Fase 1, 2 y 3 siguen marcadas como `[ ]` a pesar de que la mayoría se completaron. Opciones:
- **Opción A**: Actualizar con checkboxes reales
- **Opción B**: Archivar como `_archive/cug_master_plan_v1.md` y sacarlo del docs público

### M6: README bilingüe

El README actual está en inglés, el MANUAL y los 10 docs técnicos están en español. Para maximizar alcance:
- README en **inglés** (idioma principal para descubrimiento en GitHub)
- Agregar link al MANUAL y docs en español como **valor diferenciador**

---

## 🟢 Nice-to-Have (Post-publicación)

| #   | Mejora                                                   | Prioridad |
| --- | -------------------------------------------------------- | --------- |
| N1  | Publicación en PyPI (`pip install contoso-universe-gen`) | Media     |
| N2  | Blog post comparativo CUG vs DG V2                       | Media     |
| N3  | Video demo                                               | Baja      |
| N4  | Header localization (Fase 6 del skill plan)              | Baja      |
| N5  | Constantes configurables (Fase 7 del skill plan)         | Baja      |
| N6  | Prophet + FRED macro-calibration (ROADMAP v0.3)          | Futura    |
| N7  | MCP Server para CUG                                      | Futura    |

---

## ⚖️ Matriz de Riesgo

| Riesgo                                         | Impacto | Probabilidad | Mitigación                              |
| ---------------------------------------------- | ------- | ------------ | --------------------------------------- |
| Primera impresión mediocre por README pobre     | 🔴 Alto | 🔴 Alta      | B1: Reescribir README premium           |
| Bug de escalado visible en 5 minutos de uso    | 🔴 Alto | 🟡 Media     | B5: Verificar fix cuantitivamente       |
| PRs sin CI rompen main                         | 🟡 Med  | 🔴 Alta      | B3: GitHub Actions antes de publicar    |
| Archivos privados (.agents/) expuestos         | 🟡 Med  | 🟡 Media     | M2/M3: Actualizar .gitignore            |
| Schema docs contradicen código                 | 🟡 Med  | 🔴 Alta      | M4: Auditar nombres reales vs docs      |

---

## 📋 Plan de Acción — Orden de Ejecución

### Fase A: Higiene y Limpieza (~2 horas)

> Pre-release — BLOQUEADOR. Sin esto no se puede publicar.

- [ ] **A1**: Actualizar `.gitignore` para excluir `.agents/`, `.agent/`, `configs/_session.toml`, `configs/*.code-workspace`
- [ ] **A2**: Eliminar archivos temporales (`err.txt`, `out.txt`) — ya están en .gitignore pero existen en disco
- [ ] **A3**: Verificar y resolver el bug de escalado (B5) — test con 100, 1000, 10000 órdenes
- [ ] **A4**: Unificar versión (B6) — decidir si es v0.2.0 o v0.2.x y sincronizar `pyproject.toml` + `__init__.py`
- [ ] **A5**: Verificar que los nombres de columna en código coincidan con la documentación (M4)
- [ ] **A6**: Decidir destino de `docs/planning/cug_master_plan.md` — actualizar o archivar (M5)
- [ ] **A7**: Decidir qué archivos son públicos vs privados (M2) — crear lista definitiva

### Fase B: Documentación para la Comunidad (~4 horas)

> BLOQUEADOR. El README y CONTRIBUTING son la cara del proyecto.

- [ ] **B1**: Reescribir `README.md` — versión premium open-source:
  - Motivación / "Why CUG?" — el problema que resuelve
  - Feature highlights con emojis (mantener estilo actual pero expandir)
  - Tabla comparativa vs DG V2 (extraer de `docs/planning/contoso_comparison_strategy.md`)
  - Screenshot del terminal con Rich output
  - Quick start claro (3 comandos — mantener el actual, es bueno)
  - Links a docs y MANUAL
  - Schema visual (star schema diagram en mermaid o ASCII)
  - Badges: licencia, Python version, tests, ruff
  - Cambiar tagline de "God-level" a algo profesional pero memorable
- [ ] **B2**: Crear `CONTRIBUTING.md`:
  - Setup de entorno (`uv pip install -e ".[dev]"`)
  - Cómo correr tests (`pytest tests/ -v`)
  - Code style (ruff) — enlace a `pyproject.toml`
  - Guía para crear YAML plugins (enlace a `docs/category-plugins.md`)
  - Proceso de Issues y PRs
- [ ] **B3**: Actualizar `pyproject.toml` (M1):
  - Agregar `[project.urls]` con Homepage, Repository, Issues
  - Mejorar `description`
  - Agregar classifiers relevantes

### Fase C: Calidad y CI/CD Community-Grade (~4 horas)

> BLOQUEADOR. Sin CI y tests decentes, no es un proyecto serio.
> El CI/CD vive en el **repo público** desde el día 1. El repo privado actual es tu workspace de desarrollo.

#### Estrategia de repos

```
[Repo privado actual]                    [Repo público nuevo - CSalcedoDataBI]
PAL-TEMPORAL-REPORSITORIOS/              contoso-universe-gen/
contoso-universe-gen                         ├── .github/workflows/ci.yml
  (workspace de desarrollo)                  ├── .github/workflows/release.yml
       │                                     ├── .github/dependabot.yml
       └──── push limpio ──────────────→     ├── Branch protection: main
             (sin .agents/, planning,        └── (solo archivos públicos)
              _session.toml, etc.)
```

#### C1: Workflow `ci.yml` — Tests + Lint (en cada push/PR)

```yaml
# Triggers: push a main, cualquier PR
# Matrix: Python 3.12 + 3.13
# Steps: checkout → setup uv → install deps → ruff check → ruff format --check → pytest -v
```

- [ ] **C1.1**: Crear `.github/workflows/ci.yml`
- [ ] **C1.2**: Verificar que pasa en ambas versiones de Python

#### C2: Workflow `release.yml` — Publicación automática a PyPI

```yaml
# Triggers: push de tag v*
# Steps: build wheel con hatch → publish a PyPI → crear GitHub Release con changelog
```

- [ ] **C2.1**: Crear `.github/workflows/release.yml`
- [ ] **C2.2**: Configurar secreto `PYPI_TOKEN` en repo settings (cuando se decida publicar en PyPI)

#### C3: Dependabot + Branch Protection

| Feature                     | Impacto                          | Esfuerzo |
| --------------------------- | -------------------------------- | -------- |
| Badge de CI en README       | 🔴 Alto — señal de confianza #1 | 5 min    |
| Matrix multi-Python         | 🟡 Medio — muestra seriedad     | Incluido |
| Ruff lint + format check    | 🟡 Medio — code quality visible | Incluido |
| Dependabot (`dependabot.yml`) | 🟢 Gratis — auto-PRs seguridad | 5 min    |
| Branch protection en main   | 🟡 Medio — require CI pass      | 2 min    |
| CodeQL analysis (security)  | 🟢 Badge extra, gratis OSS      | 10 min   |

- [ ] **C3.1**: Crear `.github/dependabot.yml` (auto-PRs para actualizaciones de dependencias)
- [ ] **C3.2**: Configurar branch protection en `main` (require CI pass antes de merge)
- [ ] **C3.3**: Agregar badge de CI al README

#### C4: Expandir test suite

Priorizar por impacto:

1. Test end-to-end (100 órdenes → verificar que genera todas las tablas con FKs válidos)
2. Test de cada writer activo (CSV, Parquet, JSON mínimo)
3. Test de CLI `--help` funcional
4. Test de i18n para al menos 3 idiomas (en, es, ja)
5. Test del bug de escalado (verificar proporciones razonables)

- [ ] **C4.1**: Crear `tests/test_e2e.py`
- [ ] **C4.2**: Crear `tests/test_writers.py`
- [ ] **C4.3**: Crear `tests/test_cli.py`
- [ ] **C4.4**: Crear `tests/test_scaling.py`

#### C5: Workflow `docs.yml` (opcional — post-release)

```yaml
# Para cuando se implemente mkdocs o similar
# Build y deploy docs a GitHub Pages
```

- [ ] **C5.1**: Evaluar si mkdocs es necesario pre-release o post-release

### Fase D: Release Público (~1 hora)

- [ ] **D1**: Crear tag `v1.0.0-rc1` o `v0.3.0` (según decisión del usuario)
- [ ] **D2**: Crear GitHub Release con changelog
- [ ] **D3**: Hacer el repo público
- [ ] **D4**: Post en LinkedIn/Twitter anunciando el proyecto

### Fase E: Post-Release — Visibilidad

- [ ] **E1**: Blog post comparativo en csacedodatabi.com
- [ ] **E2**: Publicar en PyPI
- [ ] **E3**: Video demo
- [ ] **E4**: Compartir en comunidades Power BI (LinkedIn, Reddit, Power BI Community)

---

## 🔍 Decisiones que Necesitan tu Input

> [!IMPORTANT]
> Antes de ejecutar, necesito tu decisión en estos 4 puntos. Incluyo mi recomendación para cada uno.

### 1. Archivos privados del agente

**¿Qué hacer con `.agents/`, `.agent/`, `CUG-CONFIG.md`, `docs/planning/`?**

| Opción | Descripción | Mi recomendación |
| ------ | ----------- | ---------------- |
| **A** | Limpiar todo — excluir del repo público | |
| **B** | Mantener todo — son parte del storytelling "AI-agent driven" | |
| **C** ⭐ | **Híbrido** — mantener `CUG-CONFIG.md` + SKILL.md como showcase, pero excluir `.agents/` (planes internos PAL) y `docs/planning/` (comparativas internas) | **Recomendado**: muestra la innovación sin exponer workflow interno |

### 2. Versión de release

| Opción | Versión | Señal |
| ------ | ------- | ----- |
| **A** | `v1.0.0` | "Esto es estable, confía en ello" |
| **B** ⭐ | `v0.3.0` | **Recomendado**: honesto sobre evolución activa. v1.0 cuando se estabilicen todos los writers + escalado esté 100% verificado |

### 3. Organización GitHub

| Opción | Org | Señal |
| ------ | --- | ----- |
| **A** ⭐ | `CSalcedoDataBI` | **Recomendado**: refuerza marca personal y es consistente con la website y otros repos públicos |
| **B** | `Support1-PAL` | Señala proyecto empresarial, pero PAL es interno |

### 4. Idioma del README

| Opción | Idioma | Señal |
| ------ | ------ | ----- |
| **A** | Solo español | Limita descubrimiento masivo |
| **B** ⭐ | **Solo inglés** + links a docs en español | **Recomendado**: maximiza alcance global, los docs en español son valor diferenciador |
| **C** | Bilingüe | Hace el README muy largo, diluye impacto |

---

## Verificación del Plan

### Tests Automatizados (existentes)

```bash
cd d:\PAL-TEMPORAL-REPORSITORIOS\contoso-universe-gen
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
# Resultado esperado: 14 passed (todos verdes)
```

### Tests Nuevos (a crear en Fase C)

```bash
# Test end-to-end con 100 órdenes
.venv\Scripts\python.exe -m pytest tests/test_e2e.py -v -k "test_generate_100_orders"

# Test de writers
.venv\Scripts\python.exe -m pytest tests/test_writers.py -v

# Test de CLI
.venv\Scripts\python.exe -m pytest tests/test_cli.py -v

# Test de escalado (verificar proporciones)
.venv\Scripts\python.exe -m pytest tests/test_scaling.py -v
```

### Verificación Manual (Pre-Release)

1. **Generar dataset de prueba**: `cug generate -n 500 -f parquet,csv` → verificar que output tiene archivos para las 7 tablas
2. **Verificar README renderizado**: Abrir en GitHub preview, verificar que badges, tablas y links funcionan
3. **Verificar CI**: Push a branch, confirmar que GitHub Actions corre y pasa
4. **Verificar CONTRIBUTING.md**: Seguir las instrucciones como si fueras un nuevo contribuidor
5. **Verificar escalado**: `cug generate -n 100 -f csv` → confirmar que customers es ~proportional, no 50,000

---

## 📜 Checklist de Pre-Publicación

> Marcar cada ítem antes de hacer el repo público.

- [ ] README reescrito y renderizado correctamente en GitHub preview
- [ ] CONTRIBUTING.md creado y verificado paso a paso
- [ ] CI/CD configurado y corriendo verde
- [ ] Tests expandidos ≥ 25 (mínimo aceptable)
- [ ] Bug de escalado B5 verificado con 3 escalas
- [ ] Versión unificada en `pyproject.toml` + `__init__.py`
- [ ] `.gitignore` actualizado para archivos privados
- [ ] Archivos temporales eliminados
- [ ] `pyproject.toml` con metadata completa
- [ ] Schema docs alineado con código real
- [ ] No quedan referencias internas PAL en archivos públicos
- [ ] License y NOTICE verificados

---

> **Estado**: Plan revisado y mejorado, pendiente de decisiones del usuario
> **Última actualización**: 2026-03-12T16:45
