import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Obtener el directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)  # Directorio principal del proyecto

# Definir rutas
data_dir = os.path.join(project_dir, 'data')
output_dir = os.path.join(project_dir, 'output')
viz_dir = os.path.join(output_dir, 'visualizations')
maps_dir = os.path.join(output_dir, 'maps')
reports_dir = os.path.join(output_dir, 'reports')

# Crear directorios si no existen
for directory in [data_dir, output_dir, viz_dir, maps_dir, reports_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Creado directorio: {directory}")

# Construir ruta al archivo CSV
csv_path = os.path.join(data_dir, 'BurgersSpain_20250216_2154.csv')

# Cargar datos si el archivo existe
if os.path.exists(csv_path):
    print(f"Cargando datos desde: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
else:
    print(f"ERROR: El archivo CSV no se encuentra en {csv_path}")
    print("Por favor, coloca el archivo en la carpeta correcta y vuelve a ejecutar el script.")
    exit(1)  # Salir del script con código de error

# Filtrar solo hamburgueserías
hamburger_df = df[df['category'].str.lower().str.contains('hamburger restaurant', na=False)]
print(f"Registros filtrados (solo hamburgueserías): {hamburger_df.shape[0]} de {df.shape[0]}")

# Limpieza de datos
# 1. Eliminar duplicados
hamburger_df = hamburger_df.drop_duplicates(subset=['id'])

# 2. Convertir tipos de datos
hamburger_df['lat'] = pd.to_numeric(hamburger_df['lat'], errors='coerce')
hamburger_df['lng'] = pd.to_numeric(hamburger_df['lng'], errors='coerce')
hamburger_df['ratings'] = pd.to_numeric(hamburger_df['ratings'], errors='coerce')
hamburger_df['score'] = pd.to_numeric(hamburger_df['score'], errors='coerce')

# 3. Manejar valores faltantes
hamburger_df = hamburger_df.dropna(subset=['lat', 'lng'])  # Esenciales para análisis geográfico
hamburger_df['ratings'] = hamburger_df['ratings'].fillna(0)

# 4. Crear columnas derivadas
# Identificar franquicias (más de 5 establecimientos)
nombre_conteo = hamburger_df['name'].value_counts()
franquicias = nombre_conteo[nombre_conteo >= 5].index.tolist()
hamburger_df['es_franquicia'] = hamburger_df['name'].isin(franquicias)

# Guardar el dataframe limpio para análisis posteriores
hamburger_df.to_csv(os.path.join(data_dir, 'hamburgueserias_limpias.csv'), index=False)
print("Datos limpios guardados en 'datos/hamburgueserias_limpias.csv'")
# Para guardar visualizaciones, mapas y reportes:
plt.savefig(os.path.join(viz_dir, 'top_ciudades.png'), dpi=300)

# Crear un mapa de calor (ejemplo usando folium)
import folium
from folium.plugins import HeatMap

# Crear un mapa base centrado en España
mapa = folium.Map(location=[40.416775, -3.703790], zoom_start=6)

# Añadir capa de calor
heat_data = [[row['lat'], row['lng']] for index, row in hamburger_df.iterrows()]
HeatMap(heat_data).add_to(mapa)

# Guardar el mapa
mapa.save(os.path.join(maps_dir, 'mapa_calor_hamburgueserias.html'))
# Separar franquicias e independientes
franquicias_df = hamburger_df[hamburger_df['es_franquicia']]
independientes_df = hamburger_df[~hamburger_df['es_franquicia']]

# Estadísticas básicas
print(f"\nTotal de franquicias: {len(franquicias_df)} ({len(franquicias_df)/len(hamburger_df)*100:.1f}%)")
print(f"Total de independientes: {len(independientes_df)} ({len(independientes_df)/len(hamburger_df)*100:.1f}%)")

# Top franquicias
franquicias_top = franquicias_df['name'].value_counts().head(10)
print("\nPRINCIPALES FRANQUICIAS:")
for i, (nombre, cantidad) in enumerate(franquicias_top.items(), 1):
    print(f"{i}. {nombre}: {cantidad} establecimientos")

# Comparar distribución por precio
precio_franquicias = franquicias_df['price'].value_counts(normalize=True).sort_index() * 100
precio_independientes = independientes_df['price'].value_counts(normalize=True).sort_index() * 100

precio_comparativa = pd.DataFrame({
    'Franquicias (%)': precio_franquicias,
    'Independientes (%)': precio_independientes
}).fillna(0)

print("\nDISTRIBUCIÓN POR PRECIO:")
print(precio_comparativa)

# Visualizar distribución por precio
plt.figure(figsize=(12, 7))
x = np.arange(len(precio_comparativa.index))
width = 0.35

plt.bar(x - width/2, precio_comparativa['Franquicias (%)'], width, label='Franquicias', color='#FF9999')
plt.bar(x + width/2, precio_comparativa['Independientes (%)'], width, label='Independientes', color='#66B2FF')

plt.xlabel('Categoría de Precio')
plt.ylabel('Porcentaje (%)')
plt.title('Distribución por Precio: Franquicias vs Independientes', fontsize=15)
plt.xticks(x, precio_comparativa.index)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('resultados/visualizaciones/distribucion_precio_comparativa.png', dpi=300)
plt.close()

# Comparar ratings
rating_franquicias = franquicias_df['score'].mean()
rating_independientes = independientes_df['score'].mean()

print("\nRATING PROMEDIO:")
print(f"Franquicias: {rating_franquicias:.2f} estrellas")
print(f"Independientes: {rating_independientes:.2f} estrellas")

# Visualizar comparativa de ratings
plt.figure(figsize=(8, 6))
bars = plt.bar(
    ['Franquicias', 'Independientes'],
    [rating_franquicias, rating_independientes],
    color=['#FF9999', '#66B2FF']
)

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2., 
        height*1.01,
        f'{height:.2f}',
        ha='center', 
        va='bottom'
    )

plt.title('Comparativa de Ratings: Franquicias vs Independientes', fontsize=15)
plt.ylabel('Rating Promedio')
plt.ylim(4.0, 4.5)  # Ajustar para mejor visualización
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('resultados/visualizaciones/franquicias_vs_independientes.png', dpi=300)
plt.close()
# Relación entre precio y rating
rating_por_precio = hamburger_df.groupby('price')['score'].agg(['mean', 'count']).reset_index()
rating_por_precio.columns = ['Categoría de Precio', 'Rating Promedio', 'Número de Establecimientos']
rating_por_precio = rating_por_precio[rating_por_precio['Número de Establecimientos'] > 0]

print("\nRELACIÓN PRECIO-RATING:")
print(rating_por_precio)

# Visualizar relación precio-rating
plt.figure(figsize=(10, 6))
bars = plt.bar(
    rating_por_precio['Categoría de Precio'],
    rating_por_precio['Rating Promedio'],
    color='skyblue'
)

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2., 
        height*1.01,
        f'{height:.2f}',
        ha='center', 
        va='bottom'
    )

plt.title('Rating Promedio por Categoría de Precio', fontsize=15)
plt.xlabel('Categoría de Precio')
plt.ylabel('Rating Promedio')
plt.ylim(4.0, 5.0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('resultados/visualizaciones/rating_por_precio.png', dpi=300)
plt.close()

# Top hamburgueserías mejor valoradas
top_hamburgueserias = hamburger_df[hamburger_df['ratings'] >= 50].sort_values(by='score', ascending=False).head(10)

print("\nTOP 10 HAMBURGUESERÍAS MEJOR VALORADAS (MIN. 50 RESEÑAS):")
for i, (_, row) in enumerate(top_hamburgueserias.iterrows(), 1):
    print(f"{i}. {row['name']} ({row['city']}): {row['score']} estrellas, {row['ratings']} reseñas")
    
    # Hamburgueserías emergentes (alto rating pero pocas reseñas)
emergentes = independientes_df[
    (independientes_df['score'] >= 4.8) & 
    (independientes_df['ratings'] >= 10) & 
    (independientes_df['ratings'] <= 50)
].sort_values(by=['score', 'ratings'], ascending=[False, False]).head(15)

print("\nHAMBURGUESERÍAS EMERGENTES (ALTO RATING, 10-50 RESEÑAS):")
for i, (_, row) in enumerate(emergentes.iterrows(), 1):
    print(f"{i}. {row['name']} ({row['city']}): {row['score']} estrellas, {row['ratings']} reseñas")

# Distribución geográfica de tendencias emergentes
ciudades_emergentes = emergentes['city'].value_counts().head(10)
print("\nCIUDADES CON MÁS HAMBURGUESERÍAS EMERGENTES:")
for ciudad, cantidad in ciudades_emergentes.items():
    print(f"{ciudad}: {cantidad}")

# Visualizar ciudades con hamburgueserías emergentes
plt.figure(figsize=(12, 6))
ciudades_emergentes.plot(kind='bar', color='lightgreen')
plt.title('Ciudades con más hamburgueserías emergentes', fontsize=15)
plt.xlabel('Ciudad')
plt.ylabel('Número de hamburgueserías emergentes')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('resultados/visualizaciones/ciudades_tendencias_emergentes.png', dpi=300)
plt.close()

from datetime import datetime

# Recopilar estadísticas clave
estadisticas = {
    'total_hamburgueserias': len(hamburger_df),
    'rating_promedio': hamburger_df['score'].mean(),
    'ciudades_principales': ', '.join(hamburger_df['city'].value_counts().head(3).index.tolist()),
    'franquicias_pct': len(franquicias_df) / len(hamburger_df) * 100,
    'independientes_pct': len(independientes_df) / len(hamburger_df) * 100
}

# Generar reporte
reporte = f"""
Estadísticas clave:
- Total de hamburgueserías: {estadisticas['total_hamburgueserias']}
- Rating promedio: {estadisticas['rating_promedio']:.2f}
- Ciudades principales: {estadisticas['ciudades_principales']}
- Porcentaje de franquicias: {estadisticas['franquicias_pct']:.1f}%
- Porcentaje de independientes: {estadisticas['independientes_pct']:.1f}%
"""