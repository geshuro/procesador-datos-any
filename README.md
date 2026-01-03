# 🏥 Procesador de Datos Médicos

Este proyecto convierte archivos Excel médicos a CSV con filtros avanzados y reglas de calidad de datos. El sistema lee la configuración desde un archivo YAML y aplica múltiples tipos de filtros según las necesidades específicas.

## 🚀 Instalación y Uso

### Requisitos
- Python 3.7+
- pandas
- pyyaml
- openpyxl

### Instalación de dependencias
```bash
pip install pandas pyyaml openpyxl
```

### Ejecución
```bash
python src/data_processor.py
```

## 📁 Estructura del Proyecto

```
procesador-datos-any/
├── config.yaml                    # Archivo de configuración principal
├── config_sin_filtros.yaml        # Configuración sin filtros (backup)
├── _config.yaml                   # Configuración alternativa
├── README.md                      # Este archivo
├── files/                         # Carpeta de archivos de datos
│   ├── input.xlsx                 # Archivo Excel de entrada
│   └── final_*.csv                # Archivos CSV de salida (generados con timestamp)
└── src/
    └── data_processor.py          # Script principal de procesamiento
```

## 📊 Formato del Archivo de Entrada (archivofinal.xlsx)

### Estructura de Columnas Requeridas

El archivo Excel debe contener las siguientes columnas con los nombres exactos:

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `Numero_Documento_Paciente` | Numérico | Número de identificación único del paciente | `12345678` |
| `Genero` | Texto | Género del paciente (M/F) | `M`, `F` |
| `Edad_Reg` | Numérico | Edad registrada del paciente | `45` |
| `Codigo_Item` | Texto | Código médico del item/diagnóstico | `Z019`, `E785`, `99199.22` |
| `Tipo_Diagnostico` | Texto | Tipo de diagnóstico (D/R) | `D`, `R` |
| `Valor_Lab` | Texto | Valor de laboratorio | `N`, `A`, `P`, `B`, `IMC`, `S`, `D` |
| `Id_Correlativo` | Numérico | ID correlativo para ordenamiento | `1`, `2`, `3` |
| `Perimetro_Abdominal` | Numérico | Perímetro abdominal en centímetros | `95.5` |
| `Fecha_Atencion` | Fecha | Fecha de atención del paciente | `2024-01-15` |
| `Nombre_Establecimiento` | Texto | Nombre del establecimiento de salud | `Hospital Central` |

### Ejemplo de Datos

```csv
Numero_Documento_Paciente,Genero,Edad_Reg,Codigo_Item,Tipo_Diagnostico,Valor_Lab,Id_Correlativo,Perimetro_Abdominal,Fecha_Atencion,Nombre_Establecimiento
12345678,M,45,Z019,D,N,1,95.5,2024-01-15,Hospital Central
12345678,M,45,E785,D,A,2,95.5,2024-01-15,Hospital Central
87654321,F,32,Z019,D,IMC,1,88.0,2024-01-16,Clínica Norte
87654321,F,32,Z006,D,IMC,2,88.0,2024-01-16,Clínica Norte
11111111,M,28,99199.22,R,140,1,102.3,2024-01-17,Centro Médico
11111111,M,28,99199.22,R,85,2,102.3,2024-01-17,Centro Médico
22222222,F,55,Z019,D,IMC,1,92.1,2024-01-18,Hospital Sur
22222222,F,55,E669,D,IMC,2,92.1,2024-01-18,Hospital Sur
33333333,M,67,Z019,D,N,1,110.5,2024-01-19,Policlínico Este
33333333,M,67,99209.04,D,N,2,110.5,2024-01-19,Policlínico Este
```

### Códigos Médicos Comunes

#### Códigos de Valoración Clínica
- `Z019`: Consulta médica general
- `Z006`: Consulta de seguimiento
- `99209.04`: Consulta médica específica

#### Códigos de Factores de Riesgo

**Obesidad y Sobrepeso:**
- `E669`: Obesidad no especificada
- `E6691`: Obesidad tipo 1 (debida a exceso de calorías)
- `E6692`: Obesidad tipo 2 (inducida por medicamentos)
- `E6693`: Obesidad tipo 3 (obesidad extrema)
- `E6690`: Sobrepeso (obesidad debida a exceso de calorías)
- `E65X`: Obesidad localizada

**Trastornos Metabólicos:**
- `E785`: Hiperlipidemia no especificada (dislipidemia)
- `E780`: Hipercolesterolemia pura
- `E781`: Hipergliceridemia pura
- `E782`: Hiperlipidemia mixta

**Códigos de Seguimiento:**
- `Z017`: Examen de laboratorio
- `99401.13`: Consejería sobre estilo de vida

#### Códigos Específicos
- `99199.22`: Código específico para filtros especiales

### Valores de Laboratorio

| Valor | Descripción |
|-------|-------------|
| `N` | Normal |
| `A` | Anormal |
| `P` | Positivo |
| `B` | Bajo |
| `IMC` | Índice de Masa Corporal |
| `S` | Sistólica (presión arterial) |
| `D` | Diastólica (presión arterial) |

### Reglas de Validación

1. **Numero_Documento_Paciente**: Debe ser numérico y no nulo
2. **Genero**: Solo valores `M` (Masculino) o `F` (Femenino)
3. **Edad_Reg**: Entre 0 y 120 años
4. **Tipo_Diagnostico**: Solo valores `D` (Diagnóstico) o `R` (Resultado)
5. **Fecha_Atencion**: Formato de fecha válido
6. **Perimetro_Abdominal**: Numérico (puede ser nulo)

### Consideraciones Importantes

- **Un paciente puede tener múltiples registros** con diferentes códigos de item
- **Los códigos de item pueden repetirse** para el mismo paciente
- **El perímetro abdominal es opcional** y puede estar vacío
- **Las fechas deben estar en formato estándar** (YYYY-MM-DD)
- **El archivo debe estar en formato Excel** (.xlsx o .xls)

## ⚙️ Configuración

El archivo `config.yaml` contiene toda la configuración del sistema:

### Configuración Básica
```yaml
configuracion:
  tipo_diagnostico: "D"                    # Filtro por tipo de diagnóstico
  archivo_entrada: "files/input.xlsx"
  archivo_salida: "files/final_{timestamp}.csv"
  generar_nombre_unico: true               # Generar nombre único con timestamp
```

### Filtros de Códigos de Item
```yaml
codigos_item:
  obligatorios:                           # Códigos que DEBEN estar presentes
    - Z019
    - E785
  opcionales:                             # Códigos que pueden estar presentes
    - E660

filtrado_codigos:
  modo: "todos"                           # "todos" o "cualquiera"
```

### Filtros de Valores de Laboratorio
```yaml
valores_laboratorio: []                   # Lista de valores a filtrar
```

### Filtro Específico (Presión Arterial)
```yaml
filtro_especifico:
  activo: false                           # true/false
  tipo_diagnostico: ["D", "R"]           # Tipos de diagnóstico
  codigo_item_especifico: "99199.22"     # Código específico
  valor_lab_especifico: ["N", "A"]       # Valores de laboratorio específicos
  fecha_atencion_rango: ["2025-01-01", "2025-06-30"]  # Rango de fechas (opcional)
  tipo_presion_arterial_activo: false    # Activar filtro de presión arterial
  tipo_presion_arterial: ["S", "D"]      # S=Sistólica, D=Diastólica
```

### Filtro de Perímetro Abdominal
```yaml
filtro_perimetro:
  activo: false                           # true/false
  codigos_requeridos:                     # Códigos requeridos
    - "Z019"
    - "99209.04"
  clasificacion_perimetro:                # Umbrales por género
    genero_femenino:
      normal: 88                          # ≤ 88cm es normal
      anormal: 88                         # > 88cm es anormal
    genero_masculino:
      normal: 102                         # ≤ 102cm es normal
      anormal: 102                        # > 102cm es anormal
  fecha_atencion_activo: false            # Agrupar por fecha de atención
  modo_filtrado: "todos"                  # "todos" o "cualquiera"
```

### Filtro de Valoración Clínica Sin Factores de Riesgo
```yaml
filtro_valoracion_clinica:
  activo: false                           # true/false
  codigos_requeridos:                     # Códigos requeridos
    - "Z019"
    - "Z006"
  valor_lab_especifico: ["IMC"]           # Valores de laboratorio específicos (opcional)
  fecha_atencion_activo: false            # Agrupar por fecha de atención
  modo_filtrado: "todos"                  # "todos" o "cualquiera"
```

## 🔧 Funcionalidades

### 1. Filtro Básico por Tipo de Diagnóstico
- Filtra registros con `Tipo_Diagnostico = 'D'` por defecto
- Configurable en el archivo YAML

### 2. Filtro por Códigos de Item
- **Códigos Obligatorios**: Pacientes que DEBEN tener todos estos códigos
- **Códigos Opcionales**: Códigos adicionales que pueden estar presentes
- **Modos de Filtrado**:
  - `"todos"`: Pacientes con TODOS los códigos obligatorios
  - `"cualquiera"`: Pacientes con CUALQUIERA de los códigos obligatorios

### 3. Filtro por Valores de Laboratorio
- Filtra por valores específicos en la columna `Valor_Lab`
- Si no se especifican, considera todos los valores

### 4. Filtro Específico (Presión Arterial)
- Combina múltiples criterios:
  - Tipo de diagnóstico (D o R)
  - Código de item específico (99199.22)
  - Valores de laboratorio (N o A)
  - Rango de fechas de atención (opcional)
  - **Filtro de Presión Arterial**:
    - Clasifica presión como Sistólica (S) o Diastólica (D)
    - Calcula valores NORMAL/ANORMAL:
      - Sistólica: ≥140 es ANORMAL
      - Diastólica: ≥90 es ANORMAL
    - Genera columnas adicionales: `tipo_presion`, `valor_presion`, `valor_presion_total`

### 5. Filtro de Perímetro Abdominal
- Filtra por códigos específicos (Z019, 99209.04)
- Clasifica el perímetro abdominal según género:
  - **Femenino**: Normal ≤88cm, Anormal >88cm
  - **Masculino**: Normal ≤102cm, Anormal >102cm
- Agrega columna `Clasificacion_Perimetro`
- Opción de agrupar por fecha de atención

### 6. Filtro de Valoración Clínica Sin Factores de Riesgo
- Filtra por códigos específicos (Z019, Z006)
- Identifica pacientes con valoración clínica sin factores de riesgo
- Modo configurable: "todos" o "cualquiera"
- Filtro opcional por `Valor_Lab` específico (ej: IMC)
- Opción de agrupar por fecha de atención

### 7. Filtro de Valoración Clínica Con Factores de Riesgo 🆕
- Filtra pacientes con:
  - **Códigos requeridos**: Códigos básicos (ej: Z019)
  - **Factores de riesgo**: Al menos uno de los códigos de riesgo
- Códigos de factores de riesgo incluyen:
  - E65X, E669, E6691, E6692, E6693, E6690 (obesidad)
  - E785 (dislipidemia)
  - Z006 (seguimiento)
- Filtro opcional por `Valor_Lab` específico (ej: IMC)
- Opción de agrupar por fecha de atención

## 📊 Reglas de Calidad de Datos

### Validaciones Aplicadas
1. **Completitud**: Elimina registros con `Numero_Documento_Paciente` nulo
2. **Formato Numérico**: Convierte `Numero_Documento_Paciente` a entero
3. **Rango de Edad**: Valida edad entre 0-120 años
4. **Género**: Valida valores M/F
5. **Formato de Fecha**: Valida fechas de atención
6. **Consistencia**: Verifica códigos y valores según configuración

### Columnas Mantenidas
- `Numero_Documento_Paciente`
- `Genero`
- `Edad_Reg`
- `Codigo_Item`
- `Tipo_Diagnostico`
- `Valor_Lab`
- `Id_Correlativo`
- `Perimetro_Abdominal`
- `Fecha_Atencion`
- `Nombre_Establecimiento`

### Columnas Generadas Dinámicamente

Dependiendo del filtro activo, se pueden generar columnas adicionales:

| Filtro | Columnas Generadas | Descripción |
|--------|-------------------|-------------|
| **Perímetro Abdominal** | `Clasificacion_Perimetro` | NORMAL/ANORMAL según género y umbrales |
| **Presión Arterial** | `tipo_presion` | S (Sistólica) o D (Diastólica) |
| | `valor_presion` | NORMAL/ANORMAL según tipo y valor |
| | `valor_presion_total` | NORMAL/ANORMAL consolidado por paciente-fecha |

## 📋 Archivo de Configuración YAML

### Estructura del `config.yaml`:

```yaml
# Códigos de item médicos a filtrar
codigos_item:
  obligatorios:  # Códigos que DEBEN estar presentes
    - Z019
    - E785
  opcionales:    # Códigos que pueden estar presentes (no son requeridos)
    - E660

# Valores de laboratorio a filtrar (opcional)
valores_laboratorio: []

# Modo de filtrado para códigos de item
filtrado_codigos:
  modo: "todos"  # "todos" = pacientes con TODOS los códigos obligatorios
                 # "cualquiera" = pacientes con CUALQUIERA de los códigos obligatorios

# Filtro específico adicional 🆕
filtro_especifico:
  activo: true  # true = aplicar filtro específico, false = no aplicar
  tipo_diagnostico: ["D", "R"]  # Puede ser D o R
  codigo_item_especifico: "99199.22"  # Código específico a filtrar
  valor_lab_especifico: ["N", "A"]  # Valores específicos de laboratorio (N o A)

# Configuración adicional
configuracion:
  tipo_diagnostico: "D"
  archivo_entrada: "files/input.xlsx"
  archivo_salida: "files/final_{timestamp}.csv"  # Nombre único con timestamp
  generar_nombre_unico: true  # Generar nombre único para cada ejecución
  
# Columnas a mantener en el dataset final
columnas:
  - Numero_Documento_Paciente
  - Genero
  - Edad_Reg
  - Codigo_Item
  - Tipo_Diagnostico
  - Valor_Lab
  - Id_Correlativo
  - Perimetro_Abdominal
  - Fecha_Atencion
  - Nombre_Establecimiento

# Reglas de validación
validaciones:
  edad_minima: 0
  edad_maxima: 120
  generos_validos: ["M", "F"]

# ========================================
# FILTRO DE VALORACIÓN CLÍNICA CON FACTORES DE RIESGO 🆕
# ========================================
filtro_valoracion_clinica_con_riesgo:
  activo: false  # true = aplicar filtro, false = no aplicar
  codigos_requeridos:  # Códigos que DEBEN estar presentes
    - "Z019"
  codigos_factores_riesgo:  # Al menos uno debe estar presente
    - "E65X"   # Obesidad localizada
    - "E669"   # Obesidad
    - "E6691"  # Obesidad tipo 1
    - "E6692"  # Obesidad tipo 2
    - "E6693"  # Obesidad tipo 3
    - "E6690"  # Sobrepeso
  valor_lab_especifico: ["IMC"]  # Valores específicos de laboratorio (opcional)
  fecha_atencion_activo: false   # Agrupar por fecha de atención
  modo_filtrado: "todos"  # "todos" = pacientes con TODOS los códigos requeridos
```

## 📈 Ejemplos de Uso

### Ejemplo 1: Filtro Básico con Códigos Obligatorios (Dislipidemia)
```yaml
codigos_item:
  obligatorios: [Z019]
  opcionales: [E780, E781, E782, E785]
filtrado_codigos:
  modo: "todos"
# Asegurar que todos los filtros especiales están inactivos
filtro_especifico:
  activo: false
filtro_perimetro:
  activo: false
filtro_valoracion_clinica:
  activo: false
filtro_valoracion_clinica_con_riesgo:
  activo: false
```
**Caso de Uso**: Identificar pacientes con valoración clínica (Z019) y al menos un diagnóstico de dislipidemia  
**Resultado**: Registros de pacientes con consultas médicas y trastornos de lípidos

### Ejemplo 2: Filtro de Perímetro Abdominal
```yaml
filtro_perimetro:
  activo: true
  codigos_requeridos: [Z019, 99209.04]
  clasificacion_perimetro:
    genero_femenino:
      normal: 88
      anormal: 88
    genero_masculino:
      normal: 102
      anormal: 102
  fecha_atencion_activo: true
  modo_filtrado: "todos"
# Otros filtros deben estar en false
filtro_especifico:
  activo: false
```
**Caso de Uso**: Evaluar riesgo cardiovascular por perímetro abdominal  
**Resultado**: Registros con columna `Clasificacion_Perimetro` (NORMAL/ANORMAL) según género  
**Nota**: Solo pacientes con AMBOS códigos Z019 y 99209.04 en la misma fecha

### Ejemplo 3: Filtro de Valoración Clínica Sin Factores de Riesgo
```yaml
filtro_valoracion_clinica:
  activo: true
  codigos_requeridos: [Z019, Z006]
  valor_lab_especifico: [IMC]
  fecha_atencion_activo: true
  modo_filtrado: "todos"
# Otros filtros deben estar en false
filtro_perimetro:
  activo: false
filtro_especifico:
  activo: false
```
**Caso de Uso**: Pacientes con seguimiento de IMC pero sin diagnósticos de riesgo  
**Resultado**: 776 registros de 334 pacientes con valoración clínica (Z019) y seguimiento (Z006) con medición de IMC  
**Nota**: Útil para monitoreo preventivo de población sana

### Ejemplo 4: Filtro Específico - Presión Arterial (Enero-Junio 2025)
```yaml
filtro_especifico:
  activo: true
  tipo_diagnostico: [D, R]
  codigo_item_especifico: "99199.22"
  valor_lab_especifico: [N, A]  # Opcional, puede omitirse
  fecha_atencion_rango: ["2025-01-01", "2025-06-30"]
  tipo_presion_arterial_activo: true
  tipo_presion_arterial: [S, D]
# Otros filtros deben estar en false
filtrado_codigos:
  modo: "todos"
```
**Caso de Uso**: Monitoreo de presión arterial en el primer semestre 2025  
**Resultado**: Registros con columnas adicionales:
- `tipo_presion`: S (Sistólica) o D (Diastólica)
- `valor_presion`: NORMAL (S<140, D<90) o ANORMAL (S≥140, D≥90)
- `valor_presion_total`: Clasificación consolidada por paciente-fecha  
**Nota**: Utiliza `Id_Correlativo` para determinar el tipo (mínimo=Sistólica, resto=Diastólica)

### Ejemplo 5: Filtro de Valoración Clínica Con Factores de Riesgo (Obesidad)
```yaml
filtro_valoracion_clinica_con_riesgo:
  activo: true
  codigos_requeridos: [Z019]
  codigos_factores_riesgo: [E669, E6691, E6692, E6693, E6690]
  valor_lab_especifico: [IMC]
  fecha_atencion_activo: true
  modo_filtrado: "todos"
# Otros filtros deben estar en false
filtro_especifico:
  activo: false
```
**Caso de Uso**: Pacientes con diagnóstico de obesidad y medición de IMC  
**Resultado**: Pacientes que tienen:
- Código Z019 (valoración clínica) Y
- Al menos UN código de obesidad (E669, E6691, E6692, E6693, E6690) Y
- Valor de laboratorio = IMC  
- Todos los códigos en la misma fecha
**Nota**: Útil para programas de control de obesidad

### Ejemplo 6: Sobrepeso (E6690)
```yaml
codigos_item:
  obligatorios: [Z019, E6690]
filtrado_codigos:
  modo: "todos"
# Todos los filtros especiales en false
filtro_especifico:
  activo: false
filtro_perimetro:
  activo: false
filtro_valoracion_clinica:
  activo: false
filtro_valoracion_clinica_con_riesgo:
  activo: false
```
**Caso de Uso**: Identificar pacientes con diagnóstico específico de sobrepeso  
**Resultado**: Pacientes con valoración clínica Y diagnóstico de sobrepeso

### Ejemplo 7: Consejería de Estilo de Vida
```yaml
filtro_valoracion_clinica_con_riesgo:
  activo: true
  codigos_requeridos: [99401.13, Z019]
  codigos_factores_riesgo: [E669, E6691, E6692, E6693, E6690, E785, Z006]
  valor_lab_especifico: [IMC]
  fecha_atencion_activo: true
  modo_filtrado: "todos"
# Otros filtros en false
```
**Caso de Uso**: Pacientes que recibieron consejería sobre estilo de vida por factores de riesgo  
**Resultado**: Pacientes con código de consejería (99401.13) + valoración clínica (Z019) + al menos un factor de riesgo

## 📋 Salida del Sistema

### Archivos Generados
- **Nombre único**: `final_{timestamp}.csv` (ej: `final_20250102_143025.csv`)
- **Formato**: CSV con encoding UTF-8
- **Ordenamiento**: Por `Numero_Documento_Paciente` y `Fecha_Atencion`
- **Ubicación**: Carpeta `files/`

### Información Proporcionada
- Estadísticas detalladas de cada paso del procesamiento
- Distribución de códigos y valores
- Conteo de pacientes únicos
- Rango de fechas
- Porcentaje de reducción de registros
- Clasificaciones especiales (perímetro, presión arterial) según filtro activo

### Logs Detallados
```
📊 Registros originales: 44,029
📊 Registros con Tipo_Diagnostico = 'D': 41,825
📊 Registros después de limpieza: 38,237
📊 Registros finales: 776
👥 Pacientes únicos: 334
📈 Reducción total: 98.24%

📊 Distribución de códigos:
  Z019: 334 registros
  Z006: 442 registros

📅 Rango de fechas de atención:
   Fecha mínima: 2024-01-01
   Fecha máxima: 2024-12-31
```

## 🔄 Modos de Filtrado

### Modo "todos"
- Pacientes que tienen **TODOS** los códigos requeridos
- Más restrictivo, menos pacientes

### Modo "cualquiera"
- Pacientes que tienen **CUALQUIERA** de los códigos requeridos
- Menos restrictivo, más pacientes

## ⚠️ Consideraciones

1. **Prioridad de Filtros**: Los filtros se aplican en orden de especificidad (solo uno activo a la vez):
   - Filtro Específico (Presión Arterial) - Mayor prioridad
   - Filtro de Perímetro Abdominal
   - Filtro de Valoración Clínica Sin Riesgo
   - Filtro de Valoración Clínica Con Riesgo
   - Filtros Básicos (Códigos + Valores Lab) - Menor prioridad
2. **Exclusividad**: Solo se debe activar UN filtro a la vez (configurar `activo: true` en uno solo)
3. **Validación**: El sistema valida la configuración antes de procesar
4. **Backup**: Se mantiene una copia de configuración sin filtros (`config_sin_filtros.yaml`)
5. **Nombres Únicos**: Cada ejecución genera un archivo con timestamp único
6. **Agrupación por Fecha**: Cuando `fecha_atencion_activo: true`, los códigos se verifican por paciente Y fecha
7. **Columnas Dinámicas**: Algunas columnas solo se generan si el filtro correspondiente está activo

## 🔬 Detalles Técnicos

### Cómo Funciona el Filtro de Presión Arterial

El filtro de presión arterial es uno de los más complejos y utiliza varias columnas para determinar la clasificación:

1. **Identificación del Tipo de Presión**:
   - Utiliza `Id_Correlativo` para determinar el orden de las mediciones
   - El **menor** `Id_Correlativo` por paciente-fecha = **Sistólica (S)**
   - Los demás `Id_Correlativo` = **Diastólica (D)**

2. **Clasificación de Valores**:
   - **Sistólica ANORMAL**: `Valor_Lab` ≥ 140
   - **Sistólica NORMAL**: `Valor_Lab` < 140
   - **Diastólica ANORMAL**: `Valor_Lab` ≥ 90
   - **Diastólica NORMAL**: `Valor_Lab` < 90

3. **Columnas Generadas**:
   - `tipo_presion`: S o D
   - `valor_presion`: NORMAL o ANORMAL (individual)
   - `valor_presion_total`: NORMAL o ANORMAL (consolidado por paciente-fecha)
     - Si **cualquier** valor es ANORMAL → `valor_presion_total` = ANORMAL
     - Si **todos** son NORMAL → `valor_presion_total` = NORMAL

4. **Ejemplo**:
```
Paciente: 12345, Fecha: 2025-01-15
  Id_Correlativo=1, Valor_Lab=145 → tipo_presion=S, valor_presion=ANORMAL
  Id_Correlativo=2, Valor_Lab=85  → tipo_presion=D, valor_presion=NORMAL
  → valor_presion_total=ANORMAL (porque Sistólica es ANORMAL)
```

### Agrupación por Fecha de Atención

Cuando `fecha_atencion_activo: true`, el sistema agrupa los códigos por paciente Y fecha:

**Sin agrupación por fecha** (`fecha_atencion_activo: false`):
- Busca pacientes que tengan TODOS los códigos requeridos en CUALQUIER fecha
- Más flexible, considera todo el historial

**Con agrupación por fecha** (`fecha_atencion_activo: true`):
- Busca pacientes que tengan TODOS los códigos requeridos en la MISMA fecha
- Más restrictivo, asegura que los códigos fueron registrados juntos
- Útil para análisis de consultas específicas

**Ejemplo**:
```
Códigos requeridos: [Z019, Z006]
fecha_atencion_activo: false → Paciente válido si tiene Z019 cualquier día Y Z006 cualquier día
fecha_atencion_activo: true  → Paciente válido si tiene Z019 Y Z006 el MISMO día
```

## 🛠️ Solución de Problemas

### Error: Archivo de configuración no encontrado
- Verificar que `config.yaml` existe en el directorio raíz
- Verificar permisos de lectura
```bash
ls -la config.yaml
```

### Error: Archivo Excel no encontrado
- Verificar que `files/input.xlsx` existe (o el nombre configurado en `config.yaml`)
- Verificar permisos de lectura
- Asegurarse de que la carpeta `files/` existe
```bash
ls -la files/
```

### Warning: SettingWithCopyWarning
- Es un warning de pandas, no afecta la funcionalidad
- Se puede ignorar o usar `.copy()` para evitar

### Error: Columnas faltantes
- Verificar que las columnas especificadas existen en el Excel
- Revisar nombres exactos de columnas (case-sensitive)
- Las columnas requeridas son:
  - `Numero_Documento_Paciente`
  - `Genero`
  - `Edad_Reg`
  - `Codigo_Item`
  - `Tipo_Diagnostico`
  - `Valor_Lab`
  - `Id_Correlativo` (solo si se usa filtro de presión arterial)
  - `Perimetro_Abdominal`
  - `Fecha_Atencion`
  - `Nombre_Establecimiento`

### Error: No se generan registros
- Verificar que los códigos especificados existen en los datos
- Revisar el modo de filtrado (todos vs cualquiera)
- Verificar que `activo: true` está en UN SOLO filtro
- Revisar los logs para ver dónde se pierden los registros

### Múltiples filtros activos
- **IMPORTANTE**: Solo un filtro especial puede estar activo a la vez
- Si varios filtros tienen `activo: true`, solo se aplicará el primero en prioridad:
  1. `filtro_especifico`
  2. `filtro_perimetro`
  3. `filtro_valoracion_clinica`
  4. `filtro_valoracion_clinica_con_riesgo`
  5. Filtros básicos (codigos_item + valores_laboratorio)

## ❓ Preguntas Frecuentes (FAQ)

### ¿Cómo sé qué filtro usar?

Depende de tu caso de uso:
- **Filtros básicos** (codigos_item): Cuando solo necesitas filtrar por códigos médicos específicos
- **filtro_especifico**: Para análisis de presión arterial (código 99199.22)
- **filtro_perimetro**: Para análisis de riesgo cardiovascular por perímetro abdominal
- **filtro_valoracion_clinica**: Para pacientes con seguimiento pero SIN factores de riesgo
- **filtro_valoracion_clinica_con_riesgo**: Para pacientes con diagnósticos de obesidad/dislipidemia

### ¿Puedo combinar múltiples filtros?

**No**. Solo un filtro especial puede estar activo (`activo: true`) a la vez. El sistema aplicará el primero en orden de prioridad.

### ¿Qué significa "modo: todos" vs "modo: cualquiera"?

- **"todos"**: El paciente DEBE tener TODOS los códigos obligatorios
- **"cualquiera"**: El paciente puede tener CUALQUIERA de los códigos obligatorios

Ejemplo:
```yaml
codigos_item:
  obligatorios: [Z019, E785]
modo: "todos" → Paciente debe tener Z019 Y E785
modo: "cualquiera" → Paciente puede tener Z019 O E785 (o ambos)
```

### ¿Qué es Id_Correlativo y para qué sirve?

`Id_Correlativo` es un número secuencial que indica el orden de los registros. Se utiliza principalmente en el **filtro de presión arterial** para determinar qué registro es Sistólica (el primero, con Id_Correlativo más bajo) y cuál es Diastólica (los siguientes).

### ¿Cuándo usar fecha_atencion_activo: true?

Úsalo cuando quieras que los códigos requeridos estén presentes en la **misma fecha de atención**. Esto es útil para:
- Análisis de consultas específicas
- Asegurar que los diagnósticos fueron registrados juntos
- Validar protocolos de atención

### ¿Por qué no obtengo resultados?

Revisa los logs. Las causas comunes son:
1. Códigos especificados no existen en los datos
2. Modo "todos" muy restrictivo (prueba con "cualquiera")
3. `fecha_atencion_activo: true` demasiado restrictivo
4. Múltiples filtros activos simultáneamente
5. Rango de fechas muy limitado

### ¿Qué son los códigos opcionales?

Los **códigos opcionales** son códigos adicionales que pueden estar presentes pero NO son obligatorios. El sistema filtra:
1. Pacientes con TODOS los códigos obligatorios
2. Y que además tengan AL MENOS UNO de los códigos opcionales

### ¿Cómo interpreto valor_presion_total?

`valor_presion_total` es una clasificación consolidada por paciente-fecha:
- **ANORMAL**: Si la presión Sistólica O Diastólica es anormal
- **NORMAL**: Solo si AMBAS presiones son normales

Esto permite identificar rápidamente pacientes con hipertensión.

### ¿Puedo procesar datos de múltiples años?

Sí, el sistema procesa todos los registros en el archivo Excel. Puedes usar `fecha_atencion_rango` en `filtro_especifico` para limitar a un período específico.

### ¿Qué pasa con los valores nulos?

El sistema:
- **Elimina** registros con `Numero_Documento_Paciente` nulo
- **Valida** fechas y edades
- **Permite** `Perimetro_Abdominal` nulo (se marca como NO_CLASIFICADO)
- **Convierte** valores no numéricos cuando es necesario

## 📞 Soporte

Para problemas o consultas:
1. Revisar los logs detallados del sistema
2. Verificar la configuración en `config.yaml`
3. Asegurar que el archivo Excel tiene el formato esperado
4. Consultar la sección de Solución de Problemas
5. Revisar las FAQ arriba

## 📝 Notas de Versión

### Características Actuales
- ✅ Filtros múltiples con prioridades
- ✅ Análisis de presión arterial con clasificación S/D
- ✅ Clasificación de perímetro abdominal por género
- ✅ Filtros de valoración clínica con/sin factores de riesgo
- ✅ Agrupación por fecha de atención
- ✅ Validaciones de calidad de datos
- ✅ Nombres únicos con timestamp
- ✅ Logs detallados y estadísticas completas

### Próximas Mejoras Sugeridas
- [ ] Interfaz gráfica de usuario
- [ ] Exportación a múltiples formatos
- [ ] Validación automática de configuración YAML
- [ ] Reportes visuales con gráficos
- [ ] Soporte para múltiples archivos de entrada

---

**Desarrollado para procesamiento de datos médicos con filtros avanzados y reglas de calidad** 🏥📊 