from flask import Flask, render_template, request, send_file

import requests
import folium
from funciones_flask import get_polygon

import webbrowser

app = Flask(__name__)



@app.route('/cities')
def home():
    options = ['charleston', 'tampa', 'boston','galveston','seattle','san diego','new orleans']
    return render_template('index.html', options=options)


@app.route('/submit', methods=['POST'])
def submit():
    selected_option = request.form.get('selected_option')
    # The REST API endpoint
    url = f"https://api1-113694561673.southamerica-east1.run.app/API/{selected_option}"
    print(url)

    # Make a GET request
    response = requests.get(url)

    print("Response Status Code:", response.status_code)
    # Check the response status code
    if response.status_code == 200:
        
        file_path = 'map.html'
        
        radio_metros = 1000  # Radio del círculo en metros
        data = response.json()
        
        dynamic_map = folium.Map(location=data, zoom_start=12)
        
        # Add a marker
        folium.Marker(
            location=data,
            popup="ACME Marker",
            icon=folium.Icon(color="blue")
        ).add_to(dynamic_map)

        # Add a circle marker
        #folium.CircleMarker(
        #    location=data,
        #    radius=50,
        #    popup="Dynamic Circle",
        #    color="red",
        #    fill=True,
        #    fill_color="red"
        #).add_to(dynamic_map)

        # Agregar el círculo al mapa
        folium.Circle(
            location=data,
            radius=radio_metros,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.4
        ).add_to(dynamic_map)


        # Save the map to an HTML file
        dynamic_map.save(file_path)
        return send_file("map.html")


    else:
        print("Error:", response.status_code, response.text)

    return f'Thanks!!!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)









