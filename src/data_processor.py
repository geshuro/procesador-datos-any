#!/usr/bin/env python3
"""
Script para procesamiento completo de datos médicos
Convierte Excel a CSV, filtra por Tipo_Diagnostico='D' y códigos específicos
Lee configuración desde archivo YAML - maneja filtros opcionales, códigos obligatorios/opcionales, filtro específico, filtro de perímetro y modos de filtrado
"""

import pandas as pd
import os
import sys
import numpy as np
import yaml
from datetime import datetime

def load_config():
    """
    Función para cargar la configuración desde el archivo YAML
    """
    config_file = "config.yaml"
    
    if not os.path.exists(config_file):
        print(f"❌ Error: El archivo de configuración {config_file} no existe")
        print(f"📁 Directorio actual: {os.getcwd()}")
        print(f"📁 Archivos disponibles: {os.listdir('.')}")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        print("=" * 80)
        print("🏥 PROCESADOR DE DATOS MÉDICOS - CONFIGURACIÓN YAML")
        print("=" * 80)
        
        # Validar configuración
        required_keys = ['configuracion', 'columnas']
        for key in required_keys:
            if key not in config:
                print(f"❌ Error: Falta la clave '{key}' en el archivo de configuración")
                return None
        
        # Hacer opcionales los filtros
        if 'codigos_item' not in config:
            config['codigos_item'] = {'obligatorios': [], 'opcionales': []}
        elif isinstance(config['codigos_item'], list):
            # Compatibilidad con formato anterior
            config['codigos_item'] = {'obligatorios': config['codigos_item'], 'opcionales': []}
        elif not isinstance(config['codigos_item'], dict):
            config['codigos_item'] = {'obligatorios': [], 'opcionales': []}
        
        # Asegurar que existan las claves obligatorios y opcionales
        if 'obligatorios' not in config['codigos_item']:
            config['codigos_item']['obligatorios'] = []
        if 'opcionales' not in config['codigos_item']:
            config['codigos_item']['opcionales'] = []
            
        if 'valores_laboratorio' not in config:
            config['valores_laboratorio'] = []
        if 'filtrado_codigos' not in config:
            config['filtrado_codigos'] = {'modo': 'todos'}
        
        # Configurar filtro específico por defecto
        if 'filtro_especifico' not in config:
            config['filtro_especifico'] = {
                'activo': False,
                'tipo_diagnostico': ["D", "R"],
                'codigo_item_especifico': "99199.22",
                'valor_lab_especifico': ["N", "A"]
            }
        
        # Configurar filtro de perímetro por defecto
        if 'filtro_perimetro' not in config:
            config['filtro_perimetro'] = {
                'activo': False,
                'codigos_requeridos': ["Z019", "99209.04"],
                'clasificacion_perimetro': {
                    'genero_femenino': {'normal': 88, 'anormal': 88},
                    'genero_masculino': {'normal': 102, 'anormal': 102}
                },
                'modo_filtrado': "todos"
            }
        
        # Configurar filtro de valoración clínica por defecto
        if 'filtro_valoracion_clinica' not in config:
            config['filtro_valoracion_clinica'] = {
                'activo': False,
                'codigos_requeridos': ["Z019", "Z006"],
                'modo_filtrado': "todos"
            }
        
        # Configurar filtro de valoración clínica con factores de riesgo por defecto
        if 'filtro_valoracion_clinica_con_riesgo' not in config:
            config['filtro_valoracion_clinica_con_riesgo'] = {
                'activo': False,
                'codigos_requeridos': ["Z019"],
                'codigos_factores_riesgo': ["E65X", "E669", "E6691", "E6692", "E6693", "E6690"],
                'modo_filtrado': "todos"
            }
        
        # Configurar generación de nombre único
        if 'generar_nombre_unico' not in config['configuracion']:
            config['configuracion']['generar_nombre_unico'] = True
        
        print(f"\n📋 CONFIGURACIÓN CARGADA:")
        if config['codigos_item']['obligatorios'] or config['codigos_item']['opcionales']:
            if config['codigos_item']['obligatorios']:
                print(f"✅ Códigos obligatorios: {config['codigos_item']['obligatorios']}")
            if config['codigos_item']['opcionales']:
                print(f"✅ Códigos opcionales: {config['codigos_item']['opcionales']}")
            print(f"✅ Modo de filtrado: {config['filtrado_codigos']['modo']}")
        else:
            print(f"✅ Códigos de item: TODOS (no se especificaron filtros)")
            
        if config['valores_laboratorio']:
            print(f"✅ Valores de laboratorio: {config['valores_laboratorio']}")
        else:
            print(f"✅ Valores de laboratorio: TODOS (no se especificaron filtros)")
        
        # Mostrar configuración del filtro específico
        if config['filtro_especifico']['activo']:
            print(f"✅ Filtro específico: ACTIVO")
            print(f"   Tipo_Diagnostico: {config['filtro_especifico']['tipo_diagnostico']}")
            print(f"   Código_Item específico: {config['filtro_especifico']['codigo_item_especifico']}")
            print(f"   Valor_Lab específico: {config['filtro_especifico']['valor_lab_especifico']}")
        else:
            print(f"✅ Filtro específico: INACTIVO")
        
        # Mostrar configuración del filtro de perímetro
        if config['filtro_perimetro']['activo']:
            print(f"✅ Filtro de perímetro: ACTIVO")
            print(f"   Códigos requeridos: {config['filtro_perimetro']['codigos_requeridos']}")
            print(f"   Clasificación Femenino: Normal ≤{config['filtro_perimetro']['clasificacion_perimetro']['genero_femenino']['normal']}cm, Anormal >{config['filtro_perimetro']['clasificacion_perimetro']['genero_femenino']['anormal']}cm")
            print(f"   Clasificación Masculino: Normal ≤{config['filtro_perimetro']['clasificacion_perimetro']['genero_masculino']['normal']}cm, Anormal >{config['filtro_perimetro']['clasificacion_perimetro']['genero_masculino']['anormal']}cm")
            print(f"   Modo de filtrado: {config['filtro_perimetro']['modo_filtrado']}")
        else:
            print(f"✅ Filtro de perímetro: INACTIVO")
        
        # Mostrar configuración del filtro de valoración clínica
        if config['filtro_valoracion_clinica']['activo']:
            print(f"✅ Filtro de valoración clínica: ACTIVO")
            print(f"   Códigos requeridos: {config['filtro_valoracion_clinica']['codigos_requeridos']}")
            print(f"   Modo de filtrado: {config['filtro_valoracion_clinica']['modo_filtrado']}")
        else:
            print(f"✅ Filtro de valoración clínica: INACTIVO")
        
        # Mostrar configuración del filtro de valoración clínica con factores de riesgo
        if config['filtro_valoracion_clinica_con_riesgo']['activo']:
            print(f"✅ Filtro de valoración clínica con factores de riesgo: ACTIVO")
            print(f"   Códigos requeridos: {config['filtro_valoracion_clinica_con_riesgo']['codigos_requeridos']}")
            print(f"   Códigos de factores de riesgo: {config['filtro_valoracion_clinica_con_riesgo']['codigos_factores_riesgo']}")
            print(f"   Modo de filtrado: {config['filtro_valoracion_clinica_con_riesgo']['modo_filtrado']}")
        else:
            print(f"✅ Filtro de valoración clínica con factores de riesgo: INACTIVO")
            
        print(f"✅ Tipo de diagnóstico: {config['configuracion']['tipo_diagnostico']}")
        print(f"✅ Archivo de entrada: {config['configuracion']['archivo_entrada']}")
        print(f"✅ Generar nombre único: {config['configuracion']['generar_nombre_unico']}")
        print(f"✅ Columnas a mantener: {len(config['columnas'])} columnas")
        
        return config
        
    except yaml.YAMLError as e:
        print(f"❌ Error al leer el archivo YAML: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado al cargar configuración: {e}")
        return None

def generate_unique_filename(base_filename):
    """
    Genera un nombre de archivo único con timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(base_filename)
    return f"{name}_{timestamp}{ext}"

def classify_perimeter_abdominal(df, config):
    """
    Clasifica el perímetro abdominal según género y rangos específicos
    """
    filtro_perimetro = config['filtro_perimetro']
    clasificacion = filtro_perimetro['clasificacion_perimetro']
    
    # Crear nueva columna para clasificación
    df['Clasificacion_Perimetro'] = 'NO_CLASIFICADO'
    
    # Clasificar por género femenino
    mask_f = (df['Genero'] == 'F') & (df['Perimetro_Abdominal'].notna())
    df.loc[mask_f & (df['Perimetro_Abdominal'] <= clasificacion['genero_femenino']['normal']), 'Clasificacion_Perimetro'] = 'NORMAL'
    df.loc[mask_f & (df['Perimetro_Abdominal'] > clasificacion['genero_femenino']['anormal']), 'Clasificacion_Perimetro'] = 'ANORMAL'
    
    # Clasificar por género masculino
    mask_m = (df['Genero'] == 'M') & (df['Perimetro_Abdominal'].notna())
    df.loc[mask_m & (df['Perimetro_Abdominal'] <= clasificacion['genero_masculino']['normal']), 'Clasificacion_Perimetro'] = 'NORMAL'
    df.loc[mask_m & (df['Perimetro_Abdominal'] > clasificacion['genero_masculino']['anormal']), 'Clasificacion_Perimetro'] = 'ANORMAL'
    
    return df

def process_medical_data():
    """
    Función principal que procesa los datos médicos completos
    """
    try:
        print("=" * 80)
        print("🏥 PROCESADOR DE DATOS MÉDICOS")
        print("=" * 80)
        
        # Cargar configuración desde YAML
        config = load_config()
        if config is None:
            print("❌ Error: No se pudo cargar la configuración")
            return False
        
        # Extraer valores de la configuración
        codigos_obligatorios = config['codigos_item']['obligatorios']
        codigos_opcionales = config['codigos_item']['opcionales']
        todos_codigos = codigos_obligatorios + codigos_opcionales
        valores_lab = config['valores_laboratorio']
        modo_filtrado = config['filtrado_codigos']['modo']
        tipo_diagnostico = config['configuracion']['tipo_diagnostico']
        excel_file = config['configuracion']['archivo_entrada']
        base_output_file = config['configuracion']['archivo_salida']
        generar_nombre_unico = config['configuracion']['generar_nombre_unico']
        columns_to_keep = config['columnas']
        validaciones = config.get('validaciones', {})
        
        # Configurar filtros
        filtro_especifico = config['filtro_especifico']
        aplicar_filtro_especifico = filtro_especifico['activo']
        
        filtro_perimetro = config['filtro_perimetro']
        aplicar_filtro_perimetro = filtro_perimetro['activo']
        
        filtro_valoracion_clinica = config['filtro_valoracion_clinica']
        aplicar_filtro_valoracion_clinica = filtro_valoracion_clinica['activo']
        
        filtro_valoracion_clinica_con_riesgo = config['filtro_valoracion_clinica_con_riesgo']
        aplicar_filtro_valoracion_clinica_con_riesgo = filtro_valoracion_clinica_con_riesgo['activo']
        
        # Generar nombre único si está habilitado
        if generar_nombre_unico:
            final_file = generate_unique_filename(base_output_file)
        else:
            final_file = base_output_file
        
        print(f"✅ Archivo de salida: {final_file}")
        
        # PASO 1: Verificar que el archivo Excel existe
        if not os.path.exists(excel_file):
            print(f"❌ Error: El archivo {excel_file} no existe")
            print(f"📁 Directorio actual: {os.getcwd()}")
            print(f"📁 Archivos disponibles en files/: {os.listdir('files') if os.path.exists('files') else 'Carpeta files/ no existe'}")
            return False
        
        # PASO 2: Leer archivo Excel
        print(f"\n📊 Leyendo archivo Excel: {excel_file}")
        df = pd.read_excel(excel_file)
        
        print(f"✅ Registros originales: {len(df):,}")
        print(f"📋 Columnas originales: {len(df.columns)}")
        
        # PASO 3: Aplicar filtro específico si está activo
        if aplicar_filtro_especifico:
            print(f"\n🎯 Aplicando filtro específico:")
            print(f"   Tipo_Diagnostico: {filtro_especifico['tipo_diagnostico']}")
            print(f"   Código_Item: {filtro_especifico['codigo_item_especifico']}")
            print(f"   Valor_Lab: {filtro_especifico['valor_lab_especifico']}")
            
            # Aplicar filtros específicos
            df_filtered = df[
                (df['Tipo_Diagnostico'].isin(filtro_especifico['tipo_diagnostico'])) &
                (df['Codigo_Item'] == filtro_especifico['codigo_item_especifico']) &
                (df['Valor_Lab'].isin(filtro_especifico['valor_lab_especifico']))
            ].copy()
            
            print(f"📊 Registros después del filtro específico: {len(df_filtered):,}")
            
            # Mostrar distribución de Tipo_Diagnostico
            print(f"\n📊 Distribución de Tipo_Diagnostico:")
            tipo_counts = df_filtered['Tipo_Diagnostico'].value_counts()
            for tipo, count in tipo_counts.items():
                print(f"  {tipo}: {count:,} registros")
            
            # Mostrar distribución de Valor_Lab
            print(f"\n📊 Distribución de Valor_Lab:")
            lab_counts = df_filtered['Valor_Lab'].value_counts()
            for lab, count in lab_counts.items():
                print(f"  {lab}: {count:,} registros")
                
        else:
            # PASO 3: Filtrar por Tipo_Diagnostico (método original)
            print(f"\n🔍 Filtrando registros con Tipo_Diagnostico = '{tipo_diagnostico}'")
            df_filtered = df[df['Tipo_Diagnostico'] == tipo_diagnostico].copy()
            print(f"📊 Registros con Tipo_Diagnostico = '{tipo_diagnostico}': {len(df_filtered):,}")
        
        # PASO 4: Seleccionar columnas específicas
        print(f"\n🔧 Seleccionando columnas específicas: {columns_to_keep}")
        
        # Verificar que las columnas existen
        missing_columns = [col for col in columns_to_keep if col not in df_filtered.columns]
        if missing_columns:
            print(f"❌ Error: Columnas no encontradas: {missing_columns}")
            return False
        
        df_selected = df_filtered[columns_to_keep].copy()
        print(f"📊 Registros después de seleccionar columnas: {len(df_selected):,}")
        
        # PASO 5: Eliminar registros nulos de Numero_Documento_Paciente
        print(f"\n🧹 Eliminando registros nulos de Numero_Documento_Paciente")
        null_count = df_selected['Numero_Documento_Paciente'].isnull().sum()
        print(f"📊 Registros nulos en Numero_Documento_Paciente: {null_count:,}")
        
        df_clean = df_selected.dropna(subset=['Numero_Documento_Paciente'])
        print(f"📊 Registros después de eliminar nulos: {len(df_clean):,}")
        
        # PASO 6: Aplicar reglas de calidad de datos
        print(f"\n🔧 Aplicando reglas de calidad de datos...")
        
        # Regla 1: Convertir Numero_Documento_Paciente a numérico
        df_clean['Numero_Documento_Paciente'] = pd.to_numeric(df_clean['Numero_Documento_Paciente'], errors='coerce')
        df_clean = df_clean.dropna(subset=['Numero_Documento_Paciente'])
        print(f"📊 Registros después de conversión numérica: {len(df_clean):,}")
        
        # Regla 2: Validar rango de edad
        edad_min = validaciones.get('edad_minima', 0)
        edad_max = validaciones.get('edad_maxima', 120)
        if 'Edad_Reg' in df_clean.columns:
            df_clean = df_clean[(df_clean['Edad_Reg'] >= edad_min) & (df_clean['Edad_Reg'] <= edad_max)]
            print(f"📊 Registros después de validación de edad ({edad_min}-{edad_max}): {len(df_clean):,}")
        
        # Regla 3: Validar género
        generos_validos = validaciones.get('generos_validos', ['M', 'F'])
        if 'Genero' in df_clean.columns:
            df_clean = df_clean[df_clean['Genero'].isin(generos_validos)]
            print(f"📊 Registros después de validación de género: {len(df_clean):,}")
        
        # Regla 4: Validar formato de fecha
        if 'Fecha_Atencion' in df_clean.columns:
            # Convertir a datetime y verificar fechas válidas
            df_clean['Fecha_Atencion'] = pd.to_datetime(df_clean['Fecha_Atencion'], errors='coerce')
            df_clean = df_clean.dropna(subset=['Fecha_Atencion'])
            print(f"📊 Registros después de validación de fecha: {len(df_clean):,}")
        
        # PASO 7: Aplicar filtro de perímetro si está activo
        if aplicar_filtro_perimetro:
            print(f"\n📏 Aplicando filtro de perímetro abdominal:")
            print(f"   Códigos requeridos: {filtro_perimetro['codigos_requeridos']}")
            print(f"   Modo de filtrado: {filtro_perimetro['modo_filtrado']}")
            
            # Filtrar por códigos requeridos
            df_perimetro = df_clean[df_clean['Codigo_Item'].isin(filtro_perimetro['codigos_requeridos'])].copy()
            print(f"📊 Registros con códigos de perímetro: {len(df_perimetro):,}")
            
            # Mostrar distribución de códigos
            print(f"\n📊 Distribución de códigos de perímetro:")
            code_counts = df_perimetro['Codigo_Item'].value_counts()
            for code, count in code_counts.items():
                print(f"  {code}: {count:,} registros")
            
            # Aplicar filtrado de pacientes según modo
            if filtro_perimetro['modo_filtrado'] == "todos":
                print(f"📋 Filtrando pacientes con TODOS los códigos de perímetro: {filtro_perimetro['codigos_requeridos']}")
                patients_with_codes = df_perimetro.groupby('Numero_Documento_Paciente')['Codigo_Item'].apply(set)
                patients_with_all = patients_with_codes[patients_with_codes.apply(lambda x: set(filtro_perimetro['codigos_requeridos']).issubset(x))].index
                print(f"👥 Pacientes con TODOS los códigos de perímetro: {len(patients_with_all):,}")
                
                # Filtrar solo los registros de pacientes que tienen todos los códigos
                df_perimetro = df_perimetro[df_perimetro['Numero_Documento_Paciente'].isin(patients_with_all)].copy()
                print(f"📊 Registros después de filtrado de pacientes: {len(df_perimetro):,}")
            
            # Clasificar perímetro abdominal
            df_perimetro = classify_perimeter_abdominal(df_perimetro, config)
            
            # Mostrar distribución de clasificación
            print(f"\n📊 Distribución de clasificación de perímetro:")
            clasif_counts = df_perimetro['Clasificacion_Perimetro'].value_counts()
            for clasif, count in clasif_counts.items():
                print(f"  {clasif}: {count:,} registros")
            
            # Mostrar estadísticas por género
            print(f"\n📊 Estadísticas de perímetro por género:")
            for genero in ['F', 'M']:
                df_genero = df_perimetro[df_perimetro['Genero'] == genero]
                if len(df_genero) > 0:
                    normal_count = len(df_genero[df_genero['Clasificacion_Perimetro'] == 'NORMAL'])
                    anormal_count = len(df_genero[df_genero['Clasificacion_Perimetro'] == 'ANORMAL'])
                    no_clasif_count = len(df_genero[df_genero['Clasificacion_Perimetro'] == 'NO_CLASIFICADO'])
                    print(f"  Género {genero}: Normal={normal_count}, Anormal={anormal_count}, No clasificado={no_clasif_count}")
            
            # Usar datos del filtro de perímetro
            df_final = df_perimetro.copy()
            print(f"📊 Registros finales del filtro de perímetro: {len(df_final):,}")
            
        # PASO 8: Aplicar filtro de valoración clínica si está activo
        elif aplicar_filtro_valoracion_clinica:
            print(f"\n🏥 Aplicando filtro de valoración clínica sin factores de riesgo:")
            print(f"   Códigos requeridos: {filtro_valoracion_clinica['codigos_requeridos']}")
            print(f"   Modo de filtrado: {filtro_valoracion_clinica['modo_filtrado']}")
            
            # Filtrar por códigos requeridos
            df_valoracion = df_clean[df_clean['Codigo_Item'].isin(filtro_valoracion_clinica['codigos_requeridos'])].copy()
            print(f"📊 Registros con códigos de valoración clínica: {len(df_valoracion):,}")
            
            # Mostrar distribución de códigos
            print(f"\n📊 Distribución de códigos de valoración clínica:")
            code_counts = df_valoracion['Codigo_Item'].value_counts()
            for code, count in code_counts.items():
                print(f"  {code}: {count:,} registros")
            
            # Aplicar filtrado de pacientes según modo
            if filtro_valoracion_clinica['modo_filtrado'] == "todos":
                print(f"📋 Filtrando pacientes con TODOS los códigos de valoración clínica: {filtro_valoracion_clinica['codigos_requeridos']}")
                patients_with_codes = df_valoracion.groupby('Numero_Documento_Paciente')['Codigo_Item'].apply(set)
                patients_with_all = patients_with_codes[patients_with_codes.apply(lambda x: set(filtro_valoracion_clinica['codigos_requeridos']).issubset(x))].index
                print(f"👥 Pacientes con TODOS los códigos de valoración clínica: {len(patients_with_all):,}")
                
                # Filtrar solo los registros de pacientes que tienen todos los códigos
                df_valoracion = df_valoracion[df_valoracion['Numero_Documento_Paciente'].isin(patients_with_all)].copy()
                print(f"📊 Registros después de filtrado de pacientes: {len(df_valoracion):,}")
            
            # Usar datos del filtro de valoración clínica
            df_final = df_valoracion.copy()
            print(f"📊 Registros finales del filtro de valoración clínica: {len(df_final):,}")
            
        # PASO 8.5: Aplicar filtro de valoración clínica con factores de riesgo si está activo
        elif aplicar_filtro_valoracion_clinica_con_riesgo:
            print(f"\n🏥 Aplicando filtro de valoración clínica con factores de riesgo:")
            print(f"   Códigos requeridos: {filtro_valoracion_clinica_con_riesgo['codigos_requeridos']}")
            print(f"   Códigos de factores de riesgo: {filtro_valoracion_clinica_con_riesgo['codigos_factores_riesgo']}")
            print(f"   Modo de filtrado: {filtro_valoracion_clinica_con_riesgo['modo_filtrado']}")
            
            # Filtrar por códigos requeridos (Z019)
            df_valoracion_con_riesgo = df_clean[df_clean['Codigo_Item'].isin(filtro_valoracion_clinica_con_riesgo['codigos_requeridos'])].copy()
            print(f"📊 Registros con códigos requeridos (Z019): {len(df_valoracion_con_riesgo):,}")
            
            # Mostrar distribución de códigos requeridos
            print(f"\n📊 Distribución de códigos requeridos:")
            code_counts = df_valoracion_con_riesgo['Codigo_Item'].value_counts()
            for code, count in code_counts.items():
                print(f"  {code}: {count:,} registros")
            
            # Filtrar por códigos de factores de riesgo
            df_factores_riesgo = df_clean[df_clean['Codigo_Item'].isin(filtro_valoracion_clinica_con_riesgo['codigos_factores_riesgo'])].copy()
            print(f"📊 Registros con códigos de factores de riesgo: {len(df_factores_riesgo):,}")
            
            # Mostrar distribución de códigos de factores de riesgo
            print(f"\n📊 Distribución de códigos de factores de riesgo:")
            riesgo_counts = df_factores_riesgo['Codigo_Item'].value_counts()
            for code, count in riesgo_counts.items():
                print(f"  {code}: {count:,} registros")
            
            # Obtener pacientes que tienen Z019
            pacientes_con_z019 = df_valoracion_con_riesgo['Numero_Documento_Paciente'].unique()
            print(f"👥 Pacientes con código Z019: {len(pacientes_con_z019):,}")
            
            # Obtener pacientes que tienen al menos un factor de riesgo
            pacientes_con_riesgo = df_factores_riesgo['Numero_Documento_Paciente'].unique()
            print(f"👥 Pacientes con factores de riesgo: {len(pacientes_con_riesgo):,}")
            
            # Pacientes que tienen Z019 Y al menos un factor de riesgo
            pacientes_finales = set(pacientes_con_z019) & set(pacientes_con_riesgo)
            print(f"👥 Pacientes con Z019 Y factores de riesgo: {len(pacientes_finales):,}")
            
            # Filtrar registros de pacientes que cumplen ambos criterios
            df_final = df_clean[df_clean['Numero_Documento_Paciente'].isin(pacientes_finales)].copy()
            print(f"📊 Registros finales del filtro de valoración clínica con factores de riesgo: {len(df_final):,}")
            
        # PASO 9: Aplicar filtros adicionales solo si no se aplicó ningún filtro específico
        elif not aplicar_filtro_especifico and not aplicar_filtro_perimetro and not aplicar_filtro_valoracion_clinica and not aplicar_filtro_valoracion_clinica_con_riesgo:
            # Filtrar por códigos específicos (si se especificaron)
            if todos_codigos:
                print(f"\n🎯 Filtrando registros con códigos:")
                if codigos_obligatorios:
                    print(f"   Obligatorios: {codigos_obligatorios}")
                if codigos_opcionales:
                    print(f"   Opcionales: {codigos_opcionales}")
                
                df_codes = df_clean[df_clean['Codigo_Item'].isin(todos_codigos)].copy()
                print(f"📊 Registros con códigos específicos: {len(df_codes):,}")
                
                # Mostrar distribución de códigos
                print(f"\n📊 Distribución de códigos encontrados:")
                code_counts = df_codes['Codigo_Item'].value_counts()
                for code, count in code_counts.items():
                    status = "OBLIGATORIO" if code in codigos_obligatorios else "OPCIONAL"
                    print(f"  {code} ({status}): {count:,} registros")
            else:
                print(f"\n🎯 No se especificaron códigos de filtrado - considerando todos los códigos")
                df_codes = df_clean.copy()
                print(f"📊 Registros después de limpieza: {len(df_codes):,}")
                
                # Mostrar todos los códigos disponibles
                print(f"\n📊 Todos los códigos disponibles:")
                all_codes = df_codes['Codigo_Item'].value_counts()
                for code, count in all_codes.head(10).items():
                    print(f"  {code}: {count:,} registros")
                if len(all_codes) > 10:
                    print(f"  ... y {len(all_codes) - 10} códigos más")
            
            # Filtrar por valores de laboratorio (si se especificaron)
            if valores_lab:
                print(f"\n🔬 Filtrando registros con valores de laboratorio: {valores_lab}")
                df_lab = df_codes[df_codes['Valor_Lab'].isin(valores_lab)].copy()
                print(f"📊 Registros con valores de laboratorio específicos: {len(df_lab):,}")
                
                # Mostrar distribución de valores de laboratorio
                print(f"\n📊 Distribución de valores de laboratorio encontrados:")
                lab_counts = df_lab['Valor_Lab'].value_counts()
                for lab, count in lab_counts.items():
                    print(f"  {lab}: {count:,} registros")
            else:
                print(f"\n🔬 No se especificaron valores de laboratorio - considerando todos los valores")
                df_lab = df_codes.copy()
                print(f"📊 Registros después de filtrado de códigos: {len(df_lab):,}")
                
                # Mostrar todos los valores de laboratorio disponibles
                print(f"\n📊 Todos los valores de laboratorio disponibles:")
                all_labs = df_lab['Valor_Lab'].value_counts()
                for lab, count in all_labs.head(10).items():
                    print(f"  {lab}: {count:,} registros")
                if len(all_labs) > 10:
                    print(f"  ... y {len(all_labs) - 10} valores más")
            
            # Aplicar filtrado de pacientes según códigos obligatorios
            if codigos_obligatorios and len(codigos_obligatorios) > 0:
                print(f"\n🔍 Aplicando filtrado de pacientes por códigos obligatorios - Modo: {modo_filtrado}")
                print(f"📋 Códigos obligatorios: {codigos_obligatorios}")
                
                if modo_filtrado == "todos":
                    print(f"📋 Filtrando pacientes con TODOS los códigos obligatorios: {codigos_obligatorios}")
                    patients_with_codes = df_lab.groupby('Numero_Documento_Paciente')['Codigo_Item'].apply(set)
                    patients_with_all = patients_with_codes[patients_with_codes.apply(lambda x: set(codigos_obligatorios).issubset(x))].index
                    print(f"👥 Pacientes con TODOS los códigos obligatorios: {len(patients_with_all):,}")
                    
                    # Filtrar solo los registros de pacientes que tienen todos los códigos obligatorios
                    df_final = df_lab[df_lab['Numero_Documento_Paciente'].isin(patients_with_all)].copy()
                    print(f"📊 Registros finales (pacientes con TODOS los códigos obligatorios): {len(df_final):,}")
                    
                elif modo_filtrado == "cualquiera":
                    print(f"📋 Filtrando pacientes con CUALQUIERA de los códigos obligatorios: {codigos_obligatorios}")
                    patients_with_any = df_lab[df_lab['Codigo_Item'].isin(codigos_obligatorios)]['Numero_Documento_Paciente'].unique()
                    print(f"👥 Pacientes con CUALQUIERA de los códigos obligatorios: {len(patients_with_any):,}")
                    
                    # Filtrar solo los registros de pacientes que tienen al menos uno de los códigos obligatorios
                    df_final = df_lab[df_lab['Numero_Documento_Paciente'].isin(patients_with_any)].copy()
                    print(f"📊 Registros finales (pacientes con CUALQUIERA de los códigos obligatorios): {len(df_final):,}")
                    
                else:
                    print(f"⚠️  Modo de filtrado '{modo_filtrado}' no reconocido. Usando modo 'todos' por defecto.")
                    patients_with_codes = df_lab.groupby('Numero_Documento_Paciente')['Codigo_Item'].apply(set)
                    patients_with_all = patients_with_codes[patients_with_codes.apply(lambda x: set(codigos_obligatorios).issubset(x))].index
                    df_final = df_lab[df_lab['Numero_Documento_Paciente'].isin(patients_with_all)].copy()
                    print(f"📊 Registros finales (modo por defecto): {len(df_final):,}")
            else:
                print(f"\n🔍 No se especificaron códigos obligatorios - no se aplica filtrado por códigos obligatorios")
                df_final = df_lab.copy()
                print(f"📊 Registros finales: {len(df_final):,}")
        else:
            # Si se aplicó algún filtro específico, usar directamente los datos filtrados
            if aplicar_filtro_especifico:
                print(f"\n🔍 Usando datos del filtro específico")
            elif aplicar_filtro_perimetro:
                print(f"\n🔍 Usando datos del filtro de perímetro")
            elif aplicar_filtro_valoracion_clinica:
                print(f"\n🔍 Usando datos del filtro de valoración clínica")
            elif aplicar_filtro_valoracion_clinica_con_riesgo:
                print(f"\n🔍 Usando datos del filtro de valoración clínica con factores de riesgo")
            else:
                print(f"\n🔍 Usando datos sin filtros específicos")
            df_final = df_clean.copy()
            print(f"📊 Registros finales: {len(df_final):,}")
        
        # PASO 9: Aplicar formato numérico entero
        print(f"\n🔧 Aplicando formato numérico entero a Numero_Documento_Paciente...")
        df_final['Numero_Documento_Paciente'] = df_final['Numero_Documento_Paciente'].astype('Int64')
        
        # PASO 10: Ordenar por Numero_Documento_Paciente
        print(f"\n📋 Ordenando registros por Numero_Documento_Paciente...")
        df_final = df_final.sort_values('Numero_Documento_Paciente')
        
        # PASO 11: Aplicar reglas finales de calidad
        print(f"\n🔧 Aplicando reglas finales de calidad...")
        
        # Verificar completitud de datos críticos
        critical_columns = ['Numero_Documento_Paciente', 'Genero', 'Edad_Reg', 'Codigo_Item', 'Tipo_Diagnostico', 'Fecha_Atencion']
        for col in critical_columns:
            if col in df_final.columns:
                missing_count = df_final[col].isnull().sum()
                print(f"📊 Valores faltantes en {col}: {missing_count}")
        
        # Verificar consistencia de datos
        if 'Edad_Reg' in df_final.columns:
            invalid_age = df_final[(df_final['Edad_Reg'] < edad_min) | (df_final['Edad_Reg'] > edad_max)]
            if len(invalid_age) > 0:
                print(f"⚠️  Registros con edad inválida: {len(invalid_age)}")
                df_final = df_final[(df_final['Edad_Reg'] >= edad_min) & (df_final['Edad_Reg'] <= edad_max)]
        
        # Verificar formato de códigos (solo si se especificaron y no se aplicó filtro específico)
        if not aplicar_filtro_especifico and not aplicar_filtro_perimetro and not aplicar_filtro_valoracion_clinica and not aplicar_filtro_valoracion_clinica_con_riesgo and todos_codigos and 'Codigo_Item' in df_final.columns:
            invalid_codes = df_final[~df_final['Codigo_Item'].isin(todos_codigos)]
            if len(invalid_codes) > 0:
                print(f"⚠️  Registros con códigos inválidos: {len(invalid_codes)}")
                df_final = df_final[df_final['Codigo_Item'].isin(todos_codigos)]
        
        # Verificar valores de laboratorio (solo si se especificaron y no se aplicó filtro específico)
        if not aplicar_filtro_especifico and not aplicar_filtro_perimetro and not aplicar_filtro_valoracion_clinica and not aplicar_filtro_valoracion_clinica_con_riesgo and valores_lab and 'Valor_Lab' in df_final.columns:
            invalid_labs = df_final[~df_final['Valor_Lab'].isin(valores_lab)]
            if len(invalid_labs) > 0:
                print(f"⚠️  Registros con valores de laboratorio inválidos: {len(invalid_labs)}")
                df_final = df_final[df_final['Valor_Lab'].isin(valores_lab)]
        
        # Verificar Tipo_Diagnostico (solo si no se aplicó filtro específico)
        if not aplicar_filtro_especifico and not aplicar_filtro_perimetro and not aplicar_filtro_valoracion_clinica and not aplicar_filtro_valoracion_clinica_con_riesgo and 'Tipo_Diagnostico' in df_final.columns:
            invalid_types = df_final[df_final['Tipo_Diagnostico'] != tipo_diagnostico]
            if len(invalid_types) > 0:
                print(f"⚠️  Registros con Tipo_Diagnostico inválido: {len(invalid_types)}")
                df_final = df_final[df_final['Tipo_Diagnostico'] == tipo_diagnostico]
        
        # Verificar formato de fecha
        if 'Fecha_Atencion' in df_final.columns:
            invalid_dates = df_final[df_final['Fecha_Atencion'].isnull()]
            if len(invalid_dates) > 0:
                print(f"⚠️  Registros con fecha inválida: {len(invalid_dates)}")
                df_final = df_final.dropna(subset=['Fecha_Atencion'])
        
        # PASO 12: Mostrar información final
        print(f"\n📋 Información del dataset final:")
        print(f"📊 Registros finales: {len(df_final):,}")
        print(f"📋 Columnas: {len(df_final.columns)}")
        print(f"📋 Columnas: {list(df_final.columns)}")
        
        # Mostrar las primeras filas
        print(f"\n📋 Primeras 10 filas del dataset final:")
        print(df_final.head(10))
        
        # Mostrar estadísticas básicas
        print(f"\n📈 Estadísticas básicas:")
        print(df_final.describe())
        
        # Mostrar distribución final de códigos
        print(f"\n📊 Distribución final de códigos:")
        final_code_counts = df_final['Codigo_Item'].value_counts()
        for code, count in final_code_counts.head(10).items():
            if not aplicar_filtro_especifico and not aplicar_filtro_perimetro and not aplicar_filtro_valoracion_clinica and not aplicar_filtro_valoracion_clinica_con_riesgo:
                status = "OBLIGATORIO" if code in codigos_obligatorios else "OPCIONAL" if code in codigos_opcionales else "OTRO"
                print(f"  {code} ({status}): {count:,} registros")
            else:
                print(f"  {code}: {count:,} registros")
        if len(final_code_counts) > 10:
            print(f"  ... y {len(final_code_counts) - 10} códigos más")
        
        # Mostrar distribución final de valores de laboratorio
        print(f"\n📊 Distribución final de valores de laboratorio:")
        final_lab_counts = df_final['Valor_Lab'].value_counts()
        for lab, count in final_lab_counts.head(10).items():
            print(f"  {lab}: {count:,} registros")
        if len(final_lab_counts) > 10:
            print(f"  ... y {len(final_lab_counts) - 10} valores más")
        
        # Mostrar distribución de clasificación de perímetro si está disponible
        if 'Clasificacion_Perimetro' in df_final.columns:
            print(f"\n📊 Distribución final de clasificación de perímetro:")
            final_clasif_counts = df_final['Clasificacion_Perimetro'].value_counts()
            for clasif, count in final_clasif_counts.items():
                print(f"  {clasif}: {count:,} registros")
        
        # Mostrar número de pacientes únicos
        unique_patients = df_final['Numero_Documento_Paciente'].nunique()
        print(f"\n👥 Pacientes únicos en el dataset final: {unique_patients:,}")
        
        # Mostrar rango de fechas
        if 'Fecha_Atencion' in df_final.columns:
            min_date = df_final['Fecha_Atencion'].min()
            max_date = df_final['Fecha_Atencion'].max()
            print(f"\n📅 Rango de fechas de atención:")
            print(f"   Fecha mínima: {min_date}")
            print(f"   Fecha máxima: {max_date}")
        
        # PASO 13: Guardar archivo final
        print(f"\n💾 Guardando archivo final: {final_file}")
        df_final.to_csv(final_file, index=False, encoding='utf-8')
        
        # Verificar que el archivo se guardó correctamente
        if os.path.exists(final_file):
            file_size = os.path.getsize(final_file)
            print(f"✅ Archivo final creado exitosamente ({file_size:,} bytes)")
        else:
            print("❌ Error: No se pudo crear el archivo final")
            return False
        
        # RESUMEN FINAL
        print(f"\n{'='*80}")
        print("📊 RESUMEN FINAL DEL PROCESAMIENTO")
        print(f"{'='*80}")
        print(f"✅ Archivo Excel original: {excel_file}")
        print(f"✅ Registros originales: {len(df):,}")
        if aplicar_filtro_especifico:
            print(f"✅ Filtro específico aplicado: ✅")
            print(f"   Tipo_Diagnostico: {filtro_especifico['tipo_diagnostico']}")
            print(f"   Código_Item: {filtro_especifico['codigo_item_especifico']}")
            print(f"   Valor_Lab: {filtro_especifico['valor_lab_especifico']}")
        elif aplicar_filtro_perimetro:
            print(f"✅ Filtro de perímetro aplicado: ✅")
            print(f"   Códigos requeridos: {filtro_perimetro['codigos_requeridos']}")
            print(f"   Modo de filtrado: {filtro_perimetro['modo_filtrado']}")
        elif aplicar_filtro_valoracion_clinica:
            print(f"✅ Filtro de valoración clínica aplicado: ✅")
            print(f"   Códigos requeridos: {filtro_valoracion_clinica['codigos_requeridos']}")
            print(f"   Modo de filtrado: {filtro_valoracion_clinica['modo_filtrado']}")
        elif aplicar_filtro_valoracion_clinica_con_riesgo:
            print(f"✅ Filtro de valoración clínica con factores de riesgo aplicado: ✅")
            print(f"   Códigos requeridos: {filtro_valoracion_clinica_con_riesgo['codigos_requeridos']}")
            print(f"   Códigos de factores de riesgo: {filtro_valoracion_clinica_con_riesgo['codigos_factores_riesgo']}")
            print(f"   Modo de filtrado: {filtro_valoracion_clinica_con_riesgo['modo_filtrado']}")
        else:
            print(f"✅ Registros con Tipo_Diagnostico = '{tipo_diagnostico}': {len(df_filtered):,}")
        print(f"✅ Registros después de limpieza: {len(df_clean):,}")
        if not aplicar_filtro_especifico and not aplicar_filtro_perimetro and not aplicar_filtro_valoracion_clinica and not aplicar_filtro_valoracion_clinica_con_riesgo:
            if todos_codigos:
                print(f"✅ Registros con códigos específicos: {len(df_codes):,}")
            if valores_lab:
                print(f"✅ Registros con valores de laboratorio específicos: {len(df_lab):,}")
        print(f"✅ Registros finales: {len(df_final):,}")
        print(f"✅ Archivo final: {final_file}")
        if not aplicar_filtro_especifico and not aplicar_filtro_perimetro and not aplicar_filtro_valoracion_clinica and not aplicar_filtro_valoracion_clinica_con_riesgo:
            if codigos_obligatorios or codigos_opcionales:
                if codigos_obligatorios:
                    print(f"✅ Códigos obligatorios: {codigos_obligatorios}")
                if codigos_opcionales:
                    print(f"✅ Códigos opcionales: {codigos_opcionales}")
                print(f"✅ Modo de filtrado: {modo_filtrado}")
            else:
                print(f"✅ Códigos filtrados: TODOS (sin filtro específico)")
            if valores_lab:
                print(f"✅ Valores de laboratorio filtrados: {valores_lab}")
            else:
                print(f"✅ Valores de laboratorio filtrados: TODOS (sin filtro específico)")
        print(f"✅ Configuración desde YAML: ✅")
        print(f"✅ Reglas de calidad aplicadas: ✅")
        print(f"✅ Formato numérico aplicado: ✅")
        print(f"✅ Ordenamiento aplicado: ✅")
        print(f"✅ Nombre único generado: ✅")
        if aplicar_filtro_perimetro:
            print(f"✅ Clasificación de perímetro aplicada: ✅")
        if aplicar_filtro_valoracion_clinica:
            print(f"✅ Filtro de valoración clínica aplicado: ✅")
        if aplicar_filtro_valoracion_clinica_con_riesgo:
            print(f"✅ Filtro de valoración clínica con factores de riesgo aplicado: ✅")
        print(f"{'='*80}")
        
        # Mostrar estadísticas de reducción
        reduction_total = ((len(df) - len(df_final)) / len(df)) * 100
        print(f"📈 Reducción total de registros: {reduction_total:.2f}%")
        print(f"{'='*80}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {str(e)}")
        return False

if __name__ == "__main__":
    success = process_medical_data()
    if success:
        print("\n🎉 Procesamiento completado exitosamente!")
    else:
        print("\n❌ Error en el procesamiento")
        sys.exit(1) 