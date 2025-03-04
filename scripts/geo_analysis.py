import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
import matplotlib.pyplot as plt

# Load the hamburger data into a DataFrame
hamburger_df = pd.read_csv('path_to_your_hamburger_data.csv')

# 1. Top ciudades
top_ciudades = hamburger_df['city'].value_counts().head(15)
print("\nTOP 15 CIUDADES CON MÁS HAMBURGUESERÍAS:")
for i, (ciudad, cantidad) in enumerate(top_ciudades.items(), 1):
    print(f"{i}. {ciudad}: {cantidad} hamburgueserías")

# Visualizar top ciudades
plt.figure(figsize=(12, 8))
top_ciudades.plot(kind='bar', color='skyblue')
plt.title('Ciudades con más hamburgueserías en España', fontsize=15)
plt.xlabel('Ciudad')
plt.ylabel('Número de hamburgueserías')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('resultados/visualizaciones/top_ciudades.png', dpi=300)
plt.close()

# 2. Crear un mapa de calor
mapa = folium.Map(location=[40.416775, -3.703790], zoom_start=6)
puntos_calor = hamburger_df[['lat', 'lng']].values.tolist()
HeatMap(puntos_calor).add_to(mapa)
mapa.save('resultados/mapas/mapa_calor_hamburgueserias.html')
print("Mapa de calor guardado")

# 3. Mapa con las mejores hamburgueserías
mejores = hamburger_df[(hamburger_df['score'] >= 4.8) & (hamburger_df['ratings'] >= 50)].sort_values(by='score', ascending=False)

if not mejores.empty:
    mapa_mejores = folium.Map(location=[40.416775, -3.703790], zoom_start=6)
    
    for idx, row in mejores.iterrows():
        popup_text = f"""
        <b>{row['name']}</b><br>
        Rating: {row['score']} ({row['ratings']} reseñas)<br>
        Dirección: {row['address']}<br>
        Precio: {row['price'] if pd.notna(row['price']) else 'No disponible'}<br>
        """
        
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color='green', icon='star')
        ).add_to(mapa_mejores)
    
    mapa_mejores.save('resultados/mapas/mapa_mejores_hamburgueserias.html')
    print("Mapa de mejores hamburgueserías guardado")