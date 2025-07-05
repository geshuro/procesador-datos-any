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
reporte-any/
├── config.yaml                    # Archivo de configuración principal
├── config_sin_filtros.yaml        # Configuración sin filtros (backup)
├── README.md                      # Este archivo
├── files/                         # Carpeta de archivos de datos
│   ├── archivofinal.xlsx          # Archivo Excel de entrada
│   └── final_*.csv                # Archivos CSV de salida (generados)
└── src/
    └── data_processor.py          # Script principal de procesamiento
```

## ⚙️ Configuración

El archivo `config.yaml` contiene toda la configuración del sistema:

### Configuración Básica
```yaml
configuracion:
  tipo_diagnostico: "D"                    # Filtro por tipo de diagnóstico
  archivo_entrada: "files/archivofinal.xlsx"
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

### Filtro Específico
```yaml
filtro_especifico:
  activo: false                           # true/false
  tipo_diagnostico: ["D", "R"]           # Tipos de diagnóstico
  codigo_item_especifico: "99199.22"     # Código específico
  valor_lab_especifico: ["N", "A"]       # Valores de laboratorio específicos
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
  modo_filtrado: "todos"                  # "todos" o "cualquiera"
```

### Filtro de Valoración Clínica Sin Factores de Riesgo
```yaml
filtro_valoracion_clinica:
  activo: false                           # true/false
  codigos_requeridos:                     # Códigos requeridos
    - "Z019"
    - "Z006"
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

### 4. Filtro Específico
- Combina múltiples criterios:
  - Tipo de diagnóstico (D o R)
  - Código de item específico (99199.22)
  - Valores de laboratorio (N o A)

### 5. Filtro de Perímetro Abdominal
- Filtra por códigos específicos (Z019, 99209.04)
- Clasifica el perímetro abdominal según género:
  - **Femenino**: Normal ≤88cm, Anormal >88cm
  - **Masculino**: Normal ≤102cm, Anormal >102cm
- Agrega columna `Clasificacion_Perimetro`

### 6. Filtro de Valoración Clínica Sin Factores de Riesgo
- Filtra por códigos específicos (Z019, Z006)
- Identifica pacientes con valoración clínica sin factores de riesgo
- Modo configurable: "todos" o "cualquiera"

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
- `Perimetro_Abdominal`
- `Fecha_Atencion`

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
  archivo_entrada: "files/archivofinal.xlsx"
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
  - Perimetro_Abdominal
  - Fecha_Atencion

# Reglas de validación
validaciones:
  edad_minima: 0
  edad_maxima: 120
  generos_validos: ["M", "F"]
```

## 📈 Ejemplos de Uso

### Ejemplo 1: Filtro Básico con Códigos Obligatorios
```yaml
codigos_item:
  obligatorios: [Z019, E785]
  opcionales: [E660]
filtrado_codigos:
  modo: "todos"
```
**Resultado**: 53 registros de 26 pacientes con ambos códigos obligatorios

### Ejemplo 2: Filtro de Perímetro Abdominal
```yaml
filtro_perimetro:
  activo: true
  codigos_requeridos: [Z019, 99209.04]
  modo_filtrado: "todos"
```
**Resultado**: Registros con clasificación de perímetro (NORMAL/ANORMAL)

### Ejemplo 3: Filtro de Valoración Clínica
```yaml
filtro_valoracion_clinica:
  activo: true
  codigos_requeridos: [Z019, Z006]
  modo_filtrado: "todos"
```
**Resultado**: 776 registros de 334 pacientes con valoración clínica sin factores de riesgo

### Ejemplo 4: Filtro Específico
```yaml
filtro_especifico:
  activo: true
  tipo_diagnostico: [D, R]
  codigo_item_especifico: "99199.22"
  valor_lab_especifico: [N, A]
```
**Resultado**: Registros que cumplen todos los criterios específicos

## 📋 Salida del Sistema

### Archivos Generados
- **Nombre único**: `final_{timestamp}.csv`
- **Formato**: CSV con encoding UTF-8
- **Ordenamiento**: Por `Numero_Documento_Paciente`

### Información Proporcionada
- Estadísticas detalladas de cada paso del procesamiento
- Distribución de códigos y valores
- Conteo de pacientes únicos
- Rango de fechas
- Porcentaje de reducción de registros

### Logs Detallados
```
📊 Registros originales: 44,029
📊 Registros con Tipo_Diagnostico = 'D': 41,825
📊 Registros después de limpieza: 38,237
📊 Registros finales: 776
👥 Pacientes únicos: 334
📈 Reducción total: 98.24%
```

## 🔄 Modos de Filtrado

### Modo "todos"
- Pacientes que tienen **TODOS** los códigos requeridos
- Más restrictivo, menos pacientes

### Modo "cualquiera"
- Pacientes que tienen **CUALQUIERA** de los códigos requeridos
- Menos restrictivo, más pacientes

## ⚠️ Consideraciones

1. **Prioridad de Filtros**: Los filtros específicos tienen prioridad sobre los filtros básicos
2. **Exclusividad**: Solo se aplica un tipo de filtro por ejecución
3. **Validación**: El sistema valida la configuración antes de procesar
4. **Backup**: Se mantiene una copia de configuración sin filtros
5. **Nombres Únicos**: Cada ejecución genera un archivo con timestamp único

## 🛠️ Solución de Problemas

### Error: Archivo de configuración no encontrado
- Verificar que `config.yaml` existe en el directorio raíz
- Verificar permisos de lectura

### Error: Archivo Excel no encontrado
- Verificar que `files/archivofinal.xlsx` existe
- Verificar permisos de lectura

### Warning: SettingWithCopyWarning
- Es un warning de pandas, no afecta la funcionalidad
- Se puede ignorar o usar `.copy()` para evitar

### Error: Columnas faltantes
- Verificar que las columnas especificadas existen en el Excel
- Revisar nombres exactos de columnas

## 📞 Soporte

Para problemas o consultas:
1. Revisar los logs detallados del sistema
2. Verificar la configuración en `config.yaml`
3. Asegurar que el archivo Excel tiene el formato esperado

---

**Desarrollado para procesamiento de datos médicos con filtros avanzados y reglas de calidad** 