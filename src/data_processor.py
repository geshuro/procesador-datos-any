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
                'valor_lab_especifico': ["N", "A"],
                'fecha_atencion_rango': None,
                'tipo_presion_arterial_activo': False,
                'tipo_presion_arterial': ["S", "D"]
            }
        
        # Asegurar que existen todas las claves en el filtro específico
        if 'fecha_atencion_rango' not in config['filtro_especifico']:
            config['filtro_especifico']['fecha_atencion_rango'] = None
        if 'tipo_presion_arterial_activo' not in config['filtro_especifico']:
            config['filtro_especifico']['tipo_presion_arterial_activo'] = False
        if 'tipo_presion_arterial' not in config['filtro_especifico']:
            config['filtro_especifico']['tipo_presion_arterial'] = ["S", "D"]
        
        # Configurar filtro de perímetro por defecto
        if 'filtro_perimetro' not in config:
            config['filtro_perimetro'] = {
                'activo': False,
                'codigos_requeridos': ["Z019", "99209.04"],
                'clasificacion_perimetro': {
                    'genero_femenino': {'normal': 88, 'anormal': 88},
                    'genero_masculino': {'normal': 102, 'anormal': 102}
                },
                'modo_filtrado': "todos",
                'fecha_atencion_activo': False
            }
        
        # Asegurar que existe fecha_atencion_activo en el filtro de perímetro
        if 'fecha_atencion_activo' not in config['filtro_perimetro']:
            config['filtro_perimetro']['fecha_atencion_activo'] = False
        
        # Configurar filtro de valoración clínica por defecto
        if 'filtro_valoracion_clinica' not in config:
            config['filtro_valoracion_clinica'] = {
                'activo': False,
                'codigos_requeridos': ["Z019", "Z006"],
                'modo_filtrado': "todos",
                'valor_lab_especifico': [],
                'fecha_atencion_activo': False
            }
        
        # Asegurar que existen las nuevas claves en el filtro de valoración clínica
        if 'valor_lab_especifico' not in config['filtro_valoracion_clinica']:
            config['filtro_valoracion_clinica']['valor_lab_especifico'] = []
        if 'fecha_atencion_activo' not in config['filtro_valoracion_clinica']:
            config['filtro_valoracion_clinica']['fecha_atencion_activo'] = False
        
        # Configurar filtro de valoración clínica con factores de riesgo por defecto
        if 'filtro_valoracion_clinica_con_riesgo' not in config:
            config['filtro_valoracion_clinica_con_riesgo'] = {
                'activo': False,
                'codigos_requeridos': ["Z019"],
                'codigos_factores_riesgo': ["E65X", "E669", "E6691", "E6692", "E6693", "E6690"],
                'valor_lab_especifico': [],
                'fecha_atencion_activo': False,
                'modo_filtrado': "todos"
            }
        
        # Asegurar que existen las nuevas claves en el filtro de valoración clínica con factores de riesgo
        if 'valor_lab_especifico' not in config['filtro_valoracion_clinica_con_riesgo']:
            config['filtro_valoracion_clinica_con_riesgo']['valor_lab_especifico'] = []
        if 'fecha_atencion_activo' not in config['filtro_valoracion_clinica_con_riesgo']:
            config['filtro_valoracion_clinica_con_riesgo']['fecha_atencion_activo'] = False
        
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
            if 'valor_lab_especifico' in config['filtro_especifico'] and config['filtro_especifico']['valor_lab_especifico']:
                print(f"   Valor_Lab específico: {config['filtro_especifico']['valor_lab_especifico']}")
            if config['filtro_especifico']['fecha_atencion_rango']:
                print(f"   Rango de fechas: {config['filtro_especifico']['fecha_atencion_rango'][0]} a {config['filtro_especifico']['fecha_atencion_rango'][1]}")
            else:
                print(f"   Rango de fechas: No especificado")
            if config['filtro_especifico']['tipo_presion_arterial_activo']:
                print(f"   Filtro presión arterial: ACTIVO")
                print(f"   Tipos presión arterial: {config['filtro_especifico']['tipo_presion_arterial']}")
            else:
                print(f"   Filtro presión arterial: INACTIVO")
        else:
            print(f"✅ Filtro específico: INACTIVO")
        
        # Mostrar configuración del filtro de perímetro
        if config['filtro_perimetro']['activo']:
            print(f"✅ Filtro de perímetro: ACTIVO")
            print(f"   Códigos requeridos: {config['filtro_perimetro']['codigos_requeridos']}")
            print(f"   Clasificación Femenino: Normal ≤{config['filtro_perimetro']['clasificacion_perimetro']['genero_femenino']['normal']}cm, Anormal >{config['filtro_perimetro']['clasificacion_perimetro']['genero_femenino']['anormal']}cm")
            print(f"   Clasificación Masculino: Normal ≤{config['filtro_perimetro']['clasificacion_perimetro']['genero_masculino']['normal']}cm, Anormal >{config['filtro_perimetro']['clasificacion_perimetro']['genero_masculino']['anormal']}cm")
            print(f"   Modo de filtrado: {config['filtro_perimetro']['modo_filtrado']}")
            if config['filtro_perimetro']['fecha_atencion_activo']:
                print(f"   Filtro por fecha de atención: ACTIVO")
            else:
                print(f"   Filtro por fecha de atención: INACTIVO")
        else:
            print(f"✅ Filtro de perímetro: INACTIVO")
        
        # Mostrar configuración del filtro de valoración clínica
        if config['filtro_valoracion_clinica']['activo']:
            print(f"✅ Filtro de valoración clínica: ACTIVO")
            print(f"   Códigos requeridos: {config['filtro_valoracion_clinica']['codigos_requeridos']}")
            print(f"   Modo de filtrado: {config['filtro_valoracion_clinica']['modo_filtrado']}")
            if config['filtro_valoracion_clinica']['valor_lab_especifico']:
                print(f"   Valor_Lab específico: {config['filtro_valoracion_clinica']['valor_lab_especifico']}")
            if config['filtro_valoracion_clinica']['fecha_atencion_activo']:
                print(f"   Filtro por fecha de atención: ACTIVO")
            else:
                print(f"   Filtro por fecha de atención: INACTIVO")
        else:
            print(f"✅ Filtro de valoración clínica: INACTIVO")
        
        # Mostrar configuración del filtro de valoración clínica con factores de riesgo
        if config['filtro_valoracion_clinica_con_riesgo']['activo']:
            print(f"✅ Filtro de valoración clínica con factores de riesgo: ACTIVO")
            print(f"   Códigos requeridos: {config['filtro_valoracion_clinica_con_riesgo']['codigos_requeridos']}")
            print(f"   Códigos de factores de riesgo: {config['filtro_valoracion_clinica_con_riesgo']['codigos_factores_riesgo']}")
            print(f"   Modo de filtrado: {config['filtro_valoracion_clinica_con_riesgo']['modo_filtrado']}")
            if config['filtro_valoracion_clinica_con_riesgo']['valor_lab_especifico']:
                print(f"   Valor_Lab específico: {config['filtro_valoracion_clinica_con_riesgo']['valor_lab_especifico']}")
            if config['filtro_valoracion_clinica_con_riesgo']['fecha_atencion_activo']:
                print(f"   Filtro por fecha de atención: ACTIVO")
            else:
                print(f"   Filtro por fecha de atención: INACTIVO")
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
    Si fecha_atencion_activo es True, agrupa por paciente y fecha
    """
    filtro_perimetro = config['filtro_perimetro']
    clasificacion = filtro_perimetro['clasificacion_perimetro']
    fecha_atencion_activo = filtro_perimetro.get('fecha_atencion_activo', False)
    
    # Crear nueva columna para clasificación
    df['Clasificacion_Perimetro'] = 'NO_CLASIFICADO'
    
    if fecha_atencion_activo:
        print(f"📅 Clasificando perímetro por paciente y fecha de atención...")
        
        # Agrupar por paciente y fecha para clasificación
        for (patient_id, fecha), group in df.groupby(['Numero_Documento_Paciente', 'Fecha_Atencion']):
            # Clasificar por género femenino
            mask_f = (group['Genero'] == 'F') & (group['Perimetro_Abdominal'].notna())
            df.loc[(df['Numero_Documento_Paciente'] == patient_id) & 
                   (df['Fecha_Atencion'] == fecha) & 
                   mask_f & (df['Perimetro_Abdominal'] <= clasificacion['genero_femenino']['normal']), 
                   'Clasificacion_Perimetro'] = 'NORMAL'
            df.loc[(df['Numero_Documento_Paciente'] == patient_id) & 
                   (df['Fecha_Atencion'] == fecha) & 
                   mask_f & (df['Perimetro_Abdominal'] > clasificacion['genero_femenino']['anormal']), 
                   'Clasificacion_Perimetro'] = 'ANORMAL'
            
            # Clasificar por género masculino
            mask_m = (group['Genero'] == 'M') & (group['Perimetro_Abdominal'].notna())
            df.loc[(df['Numero_Documento_Paciente'] == patient_id) & 
                   (df['Fecha_Atencion'] == fecha) & 
                   mask_m & (df['Perimetro_Abdominal'] <= clasificacion['genero_masculino']['normal']), 
                   'Clasificacion_Perimetro'] = 'NORMAL'
            df.loc[(df['Numero_Documento_Paciente'] == patient_id) & 
                   (df['Fecha_Atencion'] == fecha) & 
                   mask_m & (df['Perimetro_Abdominal'] > clasificacion['genero_masculino']['anormal']), 
                   'Clasificacion_Perimetro'] = 'ANORMAL'
    else:
        print(f"📅 Clasificando perímetro por registro individual...")
        
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
            if 'valor_lab_especifico' in filtro_especifico and filtro_especifico['valor_lab_especifico']:
                print(f"   Valor_Lab: {filtro_especifico['valor_lab_especifico']}")
            
            # Aplicar filtros específicos básicos
            df_filtered = df[
                (df['Tipo_Diagnostico'].isin(filtro_especifico['tipo_diagnostico'])) &
                (df['Codigo_Item'] == filtro_especifico['codigo_item_especifico'])
            ].copy()
            
            # Aplicar filtro de Valor_Lab solo si está especificado
            if 'valor_lab_especifico' in filtro_especifico and filtro_especifico['valor_lab_especifico']:
                df_filtered = df_filtered[df_filtered['Valor_Lab'].isin(filtro_especifico['valor_lab_especifico'])].copy()
            
            print(f"📊 Registros después de filtros básicos: {len(df_filtered):,}")
            
            # Aplicar filtro por rango de fechas si está especificado
            if filtro_especifico['fecha_atencion_rango'] and len(filtro_especifico['fecha_atencion_rango']) == 2:
                fecha_inicio = filtro_especifico['fecha_atencion_rango'][0]
                fecha_fin = filtro_especifico['fecha_atencion_rango'][1]
                print(f"   Rango de fechas: {fecha_inicio} a {fecha_fin}")
                
                try:
                    # Convertir fechas a datetime
                    fecha_inicio_dt = pd.to_datetime(fecha_inicio)
                    fecha_fin_dt = pd.to_datetime(fecha_fin)
                    
                    # Convertir Fecha_Atencion a datetime si no lo está
                    df_filtered['Fecha_Atencion'] = pd.to_datetime(df_filtered['Fecha_Atencion'])
                    
                    # Aplicar filtro de rango de fechas
                    df_filtered = df_filtered[
                        (df_filtered['Fecha_Atencion'] >= fecha_inicio_dt) &
                        (df_filtered['Fecha_Atencion'] <= fecha_fin_dt)
                    ].copy()
                    
                    print(f"📊 Registros después del filtro de fechas: {len(df_filtered):,}")
                    
                    # Mostrar estadísticas de fechas
                    if len(df_filtered) > 0:
                        min_date = df_filtered['Fecha_Atencion'].min()
                        max_date = df_filtered['Fecha_Atencion'].max()
                        print(f"📅 Rango de fechas en datos filtrados: {min_date.date()} a {max_date.date()}")
                    
                except Exception as e:
                    print(f"⚠️  Error al procesar filtro de fechas: {e}")
                    print(f"📊 Continuando sin filtro de fechas...")
            else:
                print(f"   Rango de fechas: No especificado")
            
            # Aplicar filtro de presión arterial si está activo
            if filtro_especifico['tipo_presion_arterial_activo']:
                print(f"\n🩺 Aplicando filtro de presión arterial:")
                print(f"   Tipos presión arterial: {filtro_especifico['tipo_presion_arterial']}")
                
                try:
                    # Verificar que Id_Correlativo existe
                    if 'Id_Correlativo' not in df_filtered.columns:
                        print(f"❌ Error: Columna Id_Correlativo no encontrada")
                        return False
                    
                    # Convertir Valor_Lab a numérico para cálculos
                    df_filtered['Valor_Lab_Numeric'] = pd.to_numeric(df_filtered['Valor_Lab'], errors='coerce')
                    
                    # Calcular tipo de presión arterial por paciente y fecha
                    print(f"📊 Calculando tipo de presión arterial por paciente y fecha...")
                    
                    # Obtener min y max Id_Correlativo por paciente y fecha
                    patient_date_correlativo = df_filtered.groupby(['Numero_Documento_Paciente', 'Fecha_Atencion'])['Id_Correlativo'].agg(['min', 'max']).reset_index()
                    patient_date_correlativo.columns = ['Numero_Documento_Paciente', 'Fecha_Atencion', 'Id_Correlativo_Min', 'Id_Correlativo_Max']
                    
                    # Crear mapeo de tipo de presión arterial
                    df_filtered = df_filtered.merge(patient_date_correlativo, on=['Numero_Documento_Paciente', 'Fecha_Atencion'], how='left')
                    
                    # Asignar tipo de presión arterial
                    df_filtered['tipo_presion'] = 'D'  # Por defecto Diastólica
                    df_filtered.loc[df_filtered['Id_Correlativo'] == df_filtered['Id_Correlativo_Min'], 'tipo_presion'] = 'S'
                    
                    # Calcular valor de presión
                    df_filtered['valor_presion'] = 'NORMAL'
                    df_filtered.loc[(df_filtered['tipo_presion'] == 'S') & (df_filtered['Valor_Lab_Numeric'] >= 140), 'valor_presion'] = 'ANORMAL'
                    df_filtered.loc[(df_filtered['tipo_presion'] == 'D') & (df_filtered['Valor_Lab_Numeric'] >= 90), 'valor_presion'] = 'ANORMAL'
                    
                    # Calcular valor_presion_total por paciente y fecha
                    print(f"📊 Calculando valor_presion_total por paciente y fecha...")
                    
                    # Crear agregación por paciente y fecha para determinar si hay algún valor ANORMAL
                    patient_date_anormal = df_filtered.groupby(['Numero_Documento_Paciente', 'Fecha_Atencion'])['valor_presion'].apply(
                        lambda x: 'ANORMAL' if 'ANORMAL' in x.values else 'NORMAL'
                    ).reset_index()
                    patient_date_anormal.columns = ['Numero_Documento_Paciente', 'Fecha_Atencion', 'valor_presion_total']
                    
                    # Merge con el dataframe principal
                    df_filtered = df_filtered.merge(patient_date_anormal, on=['Numero_Documento_Paciente', 'Fecha_Atencion'], how='left')
                    
                    # Filtrar solo los tipos de presión arterial especificados
                    df_filtered = df_filtered[df_filtered['tipo_presion'].isin(filtro_especifico['tipo_presion_arterial'])].copy()
                    
                    print(f"📊 Registros después del filtro de presión arterial: {len(df_filtered):,}")
                    
                    # Mostrar distribución de tipos de presión
                    print(f"\n📊 Distribución de tipos de presión arterial:")
                    presion_counts = df_filtered['tipo_presion'].value_counts()
                    for tipo, count in presion_counts.items():
                        print(f"  {tipo}: {count:,} registros")
                    
                    # Mostrar distribución de valores de presión
                    print(f"\n📊 Distribución de valores de presión:")
                    valor_counts = df_filtered['valor_presion'].value_counts()
                    for valor, count in valor_counts.items():
                        print(f"  {valor}: {count:,} registros")
                    
                    # Mostrar estadísticas por tipo
                    print(f"\n📊 Estadísticas por tipo de presión:")
                    for tipo in filtro_especifico['tipo_presion_arterial']:
                        tipo_data = df_filtered[df_filtered['tipo_presion'] == tipo]
                        if len(tipo_data) > 0:
                            normal_count = len(tipo_data[tipo_data['valor_presion'] == 'NORMAL'])
                            anormal_count = len(tipo_data[tipo_data['valor_presion'] == 'ANORMAL'])
                            print(f"  {tipo}: Normal={normal_count}, Anormal={anormal_count}")
                    
                    # Mostrar distribución de valor_presion_total
                    print(f"\n📊 Distribución de valor_presion_total:")
                    total_counts = df_filtered['valor_presion_total'].value_counts()
                    for valor, count in total_counts.items():
                        print(f"  {valor}: {count:,} registros")
                    
                except Exception as e:
                    print(f"⚠️  Error al procesar filtro de presión arterial: {e}")
                    print(f"📊 Continuando sin filtro de presión arterial...")
            else:
                print(f"   Filtro presión arterial: INACTIVO")
            
            print(f"📊 Registros después del filtro específico completo: {len(df_filtered):,}")
            
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
        
        # Agregar columnas de presión arterial si el filtro está activo
        if aplicar_filtro_especifico and filtro_especifico['tipo_presion_arterial_activo']:
            additional_columns = ['tipo_presion', 'valor_presion', 'valor_presion_total']
            columns_to_keep_extended = columns_to_keep + additional_columns
            print(f"🔧 Agregando columnas de presión arterial: {additional_columns}")
        else:
            columns_to_keep_extended = columns_to_keep
        
        # Verificar que las columnas existen
        missing_columns = [col for col in columns_to_keep_extended if col not in df_filtered.columns]
        if missing_columns:
            print(f"❌ Error: Columnas no encontradas: {missing_columns}")
            return False
        
        df_selected = df_filtered[columns_to_keep_extended].copy()
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
            if filtro_perimetro.get('fecha_atencion_activo', False):
                print(f"   Filtro por fecha de atención: ACTIVO")
            else:
                print(f"   Filtro por fecha de atención: INACTIVO")
            
            # Filtrar por códigos requeridos
            df_perimetro = df_clean[df_clean['Codigo_Item'].isin(filtro_perimetro['codigos_requeridos'])].copy()
            print(f"📊 Registros con códigos de perímetro: {len(df_perimetro):,}")
            
            # Mostrar distribución de códigos
            print(f"\n📊 Distribución de códigos de perímetro:")
            code_counts = df_perimetro['Codigo_Item'].value_counts()
            for code, count in code_counts.items():
                print(f"  {code}: {count:,} registros")
            
            # Verificar completitud de códigos por paciente y fecha
            if filtro_perimetro.get('fecha_atencion_activo', False):
                print(f"\n📅 Verificando completitud de códigos por paciente y fecha...")
                
                # Agrupar por paciente y fecha para verificar códigos
                patient_date_codes = df_perimetro.groupby(['Numero_Documento_Paciente', 'Fecha_Atencion'])['Codigo_Item'].apply(set)
                
                # Filtrar solo grupos que tienen TODOS los códigos requeridos
                complete_groups = patient_date_codes[patient_date_codes.apply(lambda x: set(filtro_perimetro['codigos_requeridos']).issubset(x))]
                
                print(f"📊 Grupos (paciente-fecha) con TODOS los códigos: {len(complete_groups):,}")
                
                # Crear lista de (paciente, fecha) que tienen todos los códigos
                complete_patient_dates = complete_groups.index.tolist()
                
                # Filtrar registros que pertenecen a grupos completos
                df_perimetro = df_perimetro[df_perimetro.set_index(['Numero_Documento_Paciente', 'Fecha_Atencion']).index.isin(complete_patient_dates)].copy()
                
                print(f"📊 Registros después de filtrado por completitud de códigos por fecha: {len(df_perimetro):,}")
                
                # Mostrar estadísticas de grupos eliminados
                total_groups_before = len(patient_date_codes)
                groups_removed = total_groups_before - len(complete_groups)
                print(f"📊 Grupos (paciente-fecha) eliminados por códigos incompletos: {groups_removed:,}")
            
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
            if filtro_valoracion_clinica.get('valor_lab_especifico'):
                print(f"   Valor_Lab específico: {filtro_valoracion_clinica['valor_lab_especifico']}")
            if filtro_valoracion_clinica.get('fecha_atencion_activo', False):
                print(f"   Filtro por fecha de atención: ACTIVO")
            else:
                print(f"   Filtro por fecha de atención: INACTIVO")
            
            # Filtrar por códigos requeridos
            df_valoracion = df_clean[df_clean['Codigo_Item'].isin(filtro_valoracion_clinica['codigos_requeridos'])].copy()
            print(f"📊 Registros con códigos de valoración clínica: {len(df_valoracion):,}")
            
            # Mostrar distribución de códigos
            print(f"\n📊 Distribución de códigos de valoración clínica:")
            code_counts = df_valoracion['Codigo_Item'].value_counts()
            for code, count in code_counts.items():
                print(f"  {code}: {count:,} registros")
            
            # Aplicar filtro de Valor_Lab específico si está configurado
            if filtro_valoracion_clinica.get('valor_lab_especifico'):
                print(f"\n🔍 Aplicando filtro de Valor_Lab específico:")
                print(f"   Valor_Lab requerido: {filtro_valoracion_clinica['valor_lab_especifico']}")
                
                # Filtrar registros Z006 que no tienen el Valor_Lab específico
                z006_records = df_valoracion[df_valoracion['Codigo_Item'] == 'Z006']
                z006_with_specific_lab = z006_records[z006_records['Valor_Lab'].isin(filtro_valoracion_clinica['valor_lab_especifico'])]
                
                print(f"📊 Registros Z006 con Valor_Lab específico: {len(z006_with_specific_lab):,}")
                print(f"📊 Registros Z006 eliminados: {len(z006_records) - len(z006_with_specific_lab):,}")
                
                # Mantener solo registros Z006 con Valor_Lab específico y todos los otros códigos
                other_codes = df_valoracion[df_valoracion['Codigo_Item'] != 'Z006']
                df_valoracion = pd.concat([other_codes, z006_with_specific_lab], ignore_index=True)
                print(f"📊 Registros después de filtro Valor_Lab específico: {len(df_valoracion):,}")
            
            # Verificar completitud de códigos por paciente y fecha si está activo
            if filtro_valoracion_clinica.get('fecha_atencion_activo', False):
                print(f"\n📅 Verificando completitud de códigos por paciente y fecha...")
                
                # Agrupar por paciente y fecha para verificar códigos
                patient_date_codes = df_valoracion.groupby(['Numero_Documento_Paciente', 'Fecha_Atencion'])['Codigo_Item'].apply(set)
                
                # Filtrar solo grupos que tienen TODOS los códigos requeridos
                complete_groups = patient_date_codes[patient_date_codes.apply(lambda x: set(filtro_valoracion_clinica['codigos_requeridos']).issubset(x))]
                
                print(f"📊 Grupos (paciente-fecha) con TODOS los códigos: {len(complete_groups):,}")
                
                # Crear lista de (paciente, fecha) que tienen todos los códigos
                complete_patient_dates = complete_groups.index.tolist()
                
                # Filtrar registros que pertenecen a grupos completos
                df_valoracion = df_valoracion[df_valoracion.set_index(['Numero_Documento_Paciente', 'Fecha_Atencion']).index.isin(complete_patient_dates)].copy()
                
                print(f"📊 Registros después de filtrado por completitud de códigos por fecha: {len(df_valoracion):,}")
                
                # Mostrar estadísticas de grupos eliminados
                total_groups_before = len(patient_date_codes)
                groups_removed = total_groups_before - len(complete_groups)
                print(f"📊 Grupos (paciente-fecha) eliminados por códigos incompletos: {groups_removed:,}")
            
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
            if filtro_valoracion_clinica_con_riesgo.get('valor_lab_especifico'):
                print(f"   Valor_Lab específico: {filtro_valoracion_clinica_con_riesgo['valor_lab_especifico']}")
            if filtro_valoracion_clinica_con_riesgo.get('fecha_atencion_activo', False):
                print(f"   Filtro por fecha de atención: ACTIVO")
            else:
                print(f"   Filtro por fecha de atención: INACTIVO")
            
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
            
            # Aplicar filtro de Valor_Lab específico si está configurado
            if filtro_valoracion_clinica_con_riesgo.get('valor_lab_especifico'):
                print(f"\n🔍 Aplicando filtro de Valor_Lab específico a códigos de factores de riesgo:")
                print(f"   Valor_Lab requerido: {filtro_valoracion_clinica_con_riesgo['valor_lab_especifico']}")
                
                # Filtrar registros de factores de riesgo que no tienen el Valor_Lab específico
                factores_riesgo_with_specific_lab = df_factores_riesgo[df_factores_riesgo['Valor_Lab'].isin(filtro_valoracion_clinica_con_riesgo['valor_lab_especifico'])]
                
                print(f"📊 Registros de factores de riesgo con Valor_Lab específico: {len(factores_riesgo_with_specific_lab):,}")
                print(f"📊 Registros de factores de riesgo eliminados: {len(df_factores_riesgo) - len(factores_riesgo_with_specific_lab):,}")
                
                # Actualizar df_factores_riesgo con solo los registros que tienen el Valor_Lab específico
                df_factores_riesgo = factores_riesgo_with_specific_lab.copy()
                print(f"📊 Registros de factores de riesgo después de filtro Valor_Lab específico: {len(df_factores_riesgo):,}")
            
            # Verificar completitud de códigos por paciente y fecha si está activo
            if filtro_valoracion_clinica_con_riesgo.get('fecha_atencion_activo', False):
                print(f"\n📅 Verificando completitud de códigos por paciente y fecha...")
                
                # Combinar códigos requeridos y de factores de riesgo para verificar completitud
                todos_codigos_riesgo = filtro_valoracion_clinica_con_riesgo['codigos_requeridos'] + filtro_valoracion_clinica_con_riesgo['codigos_factores_riesgo']
                
                # Filtrar registros que tienen códigos requeridos o de factores de riesgo
                df_todos_codigos = df_clean[df_clean['Codigo_Item'].isin(todos_codigos_riesgo)].copy()
                
                # Agrupar por paciente y fecha para verificar códigos
                patient_date_codes = df_todos_codigos.groupby(['Numero_Documento_Paciente', 'Fecha_Atencion'])['Codigo_Item'].apply(set)
                
                # Filtrar solo grupos que tienen al menos un código requerido Y al menos un factor de riesgo
                def has_required_and_risk_codes(codes):
                    has_required = any(code in codes for code in filtro_valoracion_clinica_con_riesgo['codigos_requeridos'])
                    has_risk = any(code in codes for code in filtro_valoracion_clinica_con_riesgo['codigos_factores_riesgo'])
                    return has_required and has_risk
                
                complete_groups = patient_date_codes[patient_date_codes.apply(has_required_and_risk_codes)]
                
                print(f"📊 Grupos (paciente-fecha) con códigos requeridos Y factores de riesgo: {len(complete_groups):,}")
                
                # Crear lista de (paciente, fecha) que tienen códigos completos
                complete_patient_dates = complete_groups.index.tolist()
                
                # Filtrar registros que pertenecen a grupos completos
                df_todos_codigos = df_todos_codigos[df_todos_codigos.set_index(['Numero_Documento_Paciente', 'Fecha_Atencion']).index.isin(complete_patient_dates)].copy()
                
                print(f"📊 Registros después de filtrado por completitud de códigos por fecha: {len(df_todos_codigos):,}")
                
                # Mostrar estadísticas de grupos eliminados
                total_groups_before = len(patient_date_codes)
                groups_removed = total_groups_before - len(complete_groups)
                print(f"📊 Grupos (paciente-fecha) eliminados por códigos incompletos: {groups_removed:,}")
                
                # Usar los datos filtrados por fecha
                df_final = df_todos_codigos.copy()
            else:
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
            
            # Aplicar filtrado de pacientes según códigos obligatorios y opcionales
            if codigos_obligatorios and len(codigos_obligatorios) > 0:
                print(f"\n🔍 Aplicando filtrado de pacientes por códigos obligatorios - Modo: {modo_filtrado}")
                print(f"📋 Códigos obligatorios: {codigos_obligatorios}")
                if codigos_opcionales:
                    print(f"📋 Códigos opcionales: {codigos_opcionales}")
                
                if modo_filtrado == "todos":
                    print(f"📋 Filtrando pacientes con TODOS los códigos obligatorios: {codigos_obligatorios}")
                    patients_with_codes = df_lab.groupby('Numero_Documento_Paciente')['Codigo_Item'].apply(set)
                    patients_with_all = patients_with_codes[patients_with_codes.apply(lambda x: set(codigos_obligatorios).issubset(x))].index
                    print(f"👥 Pacientes con TODOS los códigos obligatorios: {len(patients_with_all):,}")
                    
                    # Si hay códigos opcionales, filtrar pacientes que tienen al menos uno de los opcionales
                    if codigos_opcionales and len(codigos_opcionales) > 0:
                        print(f"📋 Filtrando pacientes con al menos UNO de los códigos opcionales: {codigos_opcionales}")
                        patients_with_optional = df_lab[df_lab['Codigo_Item'].isin(codigos_opcionales)]['Numero_Documento_Paciente'].unique()
                        print(f"👥 Pacientes con códigos opcionales: {len(patients_with_optional):,}")
                        
                        # Pacientes que tienen TODOS los obligatorios Y al menos uno opcional
                        patients_final = set(patients_with_all) & set(patients_with_optional)
                        print(f"👥 Pacientes con TODOS los obligatorios Y al menos uno opcional: {len(patients_final):,}")
                        
                        # Filtrar solo los registros de pacientes que cumplen ambos criterios
                        df_final = df_lab[df_lab['Numero_Documento_Paciente'].isin(patients_final)].copy()
                        print(f"📊 Registros finales (pacientes con obligatorios + opcionales): {len(df_final):,}")
                    else:
                        # Solo códigos obligatorios, sin opcionales
                        df_final = df_lab[df_lab['Numero_Documento_Paciente'].isin(patients_with_all)].copy()
                        print(f"📊 Registros finales (pacientes con TODOS los códigos obligatorios): {len(df_final):,}")
                    
                elif modo_filtrado == "cualquiera":
                    print(f"📋 Filtrando pacientes con CUALQUIERA de los códigos obligatorios: {codigos_obligatorios}")
                    patients_with_any = df_lab[df_lab['Codigo_Item'].isin(codigos_obligatorios)]['Numero_Documento_Paciente'].unique()
                    print(f"👥 Pacientes con CUALQUIERA de los códigos obligatorios: {len(patients_with_any):,}")
                    
                    # Si hay códigos opcionales, filtrar pacientes que tienen al menos uno de los opcionales
                    if codigos_opcionales and len(codigos_opcionales) > 0:
                        print(f"📋 Filtrando pacientes con al menos UNO de los códigos opcionales: {codigos_opcionales}")
                        patients_with_optional = df_lab[df_lab['Codigo_Item'].isin(codigos_opcionales)]['Numero_Documento_Paciente'].unique()
                        print(f"👥 Pacientes con códigos opcionales: {len(patients_with_optional):,}")
                        
                        # Pacientes que tienen CUALQUIERA de los obligatorios Y al menos uno opcional
                        patients_final = set(patients_with_any) & set(patients_with_optional)
                        print(f"👥 Pacientes con CUALQUIERA de los obligatorios Y al menos uno opcional: {len(patients_final):,}")
                        
                        # Filtrar solo los registros de pacientes que cumplen ambos criterios
                        df_final = df_lab[df_lab['Numero_Documento_Paciente'].isin(patients_final)].copy()
                        print(f"📊 Registros finales (pacientes con obligatorios + opcionales): {len(df_final):,}")
                    else:
                        # Solo códigos obligatorios, sin opcionales
                        df_final = df_lab[df_lab['Numero_Documento_Paciente'].isin(patients_with_any)].copy()
                        print(f"📊 Registros finales (pacientes con CUALQUIERA de los códigos obligatorios): {len(df_final):,}")
                    
                else:
                    print(f"⚠️  Modo de filtrado '{modo_filtrado}' no reconocido. Usando modo 'todos' por defecto.")
                    patients_with_codes = df_lab.groupby('Numero_Documento_Paciente')['Codigo_Item'].apply(set)
                    patients_with_all = patients_with_codes[patients_with_codes.apply(lambda x: set(codigos_obligatorios).issubset(x))].index
                    
                    # Si hay códigos opcionales, aplicar la misma lógica
                    if codigos_opcionales and len(codigos_opcionales) > 0:
                        patients_with_optional = df_lab[df_lab['Codigo_Item'].isin(codigos_opcionales)]['Numero_Documento_Paciente'].unique()
                        patients_final = set(patients_with_all) & set(patients_with_optional)
                        df_final = df_lab[df_lab['Numero_Documento_Paciente'].isin(patients_final)].copy()
                    else:
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
        
        # PASO 10: Ordenar por Numero_Documento_Paciente y 
        
        print(f"\n📋 Ordenando registros por Numero_Documento_Paciente y Fecha_Atencion...")
        df_final = df_final.sort_values(['Numero_Documento_Paciente', 'Fecha_Atencion'])
        
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
            if 'valor_lab_especifico' in filtro_especifico and filtro_especifico['valor_lab_especifico']:
                print(f"   Valor_Lab: {filtro_especifico['valor_lab_especifico']}")
            if filtro_especifico['tipo_presion_arterial_activo']:
                print(f"   Filtro presión arterial: ACTIVO")
                print(f"   Tipos presión arterial: {filtro_especifico['tipo_presion_arterial']}")
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