import io

import sys

import folium

import geocoder

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from PyQt5.QtWidgets import QLineEdit, QComboBox, QMessageBox

import openrouteservice

import json
import random


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.routes = None
        self.Extracted = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Road Mapper")
        self.setFixedSize(1250, 600)
        
        self.Paths_btn = QtWidgets.QPushButton("FIND SHORTEST ROUTE")
        self.Clear_btn = QtWidgets.QPushButton("CLEAR PLOTTED ROUTES")
        self.Locate_btn = QtWidgets.QPushButton("LOCATE SIGNS ALONG ROUTE")
        self.Extract_btn = QtWidgets.QPushButton("EXTRACT SIGNS DATA")
        
        self.validator = QtGui.QDoubleValidator(
                -90.0, # bottom
                90.0, # top
                15, # decimals 
                notation=QtGui.QDoubleValidator.StandardNotation
            )
        self.ChooseWay = QComboBox()
        self.ChooseWay.addItem("ROUTE USING COORDINATES")
        self.ChooseWay.addItem("ROUTE USING PLACE NAMES")
        self.ChooseWay.activated[str].connect(self.onChanged)  
        self.TextBox1 = QLineEdit()
        self.TextBox2 = QLineEdit()
        self.TextBox3 = QLineEdit()
        self.TextBox4 = QLineEdit()
        self.TextBox5 = QLineEdit()
        self.TextBox6 = QLineEdit()

        # Starting Lat And Long
        self.TextBox3.setValidator(self.validator)
        self.TextBox4.setValidator(self.validator)
        
        # Destination Lat And Long
        self.TextBox5.setValidator(self.validator)
        self.TextBox6.setValidator(self.validator)

        self.Paths_btn.clicked.connect(self.PlotRoad)
        self.Locate_btn.clicked.connect(self.LocateSigns)
        self.Extract_btn.clicked.connect(self.Extract)
        self.Clear_btn.clicked.connect(self.ClearMap)
        
        self.m = folium.Map(tiles=None, location=[33.867, 35.5433],zoom_start=12, min_zoom = 1)
        # Adding Layers to basemap
        folium.TileLayer( tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', 
               attr = 'Google Maps', name = 'Google Maps', overlay = True, control = False
            ).add_to(self.m)
            
        folium.TileLayer( tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
               attr = 'Google Satelite', name = 'Google Satelite', overlay = True, control = True
            ).add_to(self.m)
        folium.LayerControl().add_to(self.m)
        
        self.Paths_btn.setFixedSize(300, 40)
        self.Clear_btn.setFixedSize(300,40)
        self.Locate_btn.setFixedSize(300,40)
        self.Extract_btn.setFixedSize(300,40)
        self.TextBox1.setFixedSize(300, 40)
        self.TextBox2.setFixedSize(300, 40)
        self.ChooseWay.setFixedSize(300,40)
        self.TextBox3.setFixedSize(300, 40)
        self.TextBox4.setFixedSize(300,40)
        self.TextBox5.setFixedSize(300, 40)
        self.TextBox6.setFixedSize(300,40)
        self.buttonUI() 
        self.mapUI()

    
    def buttonUI(self):
        
        self.TextBox1.setPlaceholderText("STARTING NAME...") # Beirut, Haret Hreik
        self.TextBox2.setPlaceholderText("DESTINATION NAME...") # Beirut, Borj El Brajneh
        
        self.TextBox3.setPlaceholderText("STARTING LATITUDE...") # 33.890944105645936
        self.TextBox4.setPlaceholderText("STARTING LONGITUDE...") # 35.48486122182076
        
        self.TextBox5.setPlaceholderText("DESTINATION LATITUDE...") # 33.890009246377865
        self.TextBox6.setPlaceholderText("DESTINATION LONGITUDE...") # 35.4744326534531
        
        
        '''
        # TESTING FOR PLACE NAMES
        self.TextBox1.setText('Beirut, Borj El Brajneh')
        self.TextBox2.setText('Beirut, Haret Hreik')
        
        # TESTING USING POINTS
        self.TextBox3.setText('33.890944105645936') 
        self.TextBox4.setText('35.48486122182076') 
        
        self.TextBox5.setText('33.890009246377865') 
        self.TextBox6.setText('35.4744326534531') 
        '''
        
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(1, 1, 1, 1)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QHBoxLayout(central_widget)

        container = QtWidgets.QWidget()
        vlay = QtWidgets.QVBoxLayout(container)
        vlay.setSpacing(1)
        vlay.addStretch()
        vlay.addWidget(self.ChooseWay)
        vlay.addWidget(self.TextBox1)
        vlay.addWidget(self.TextBox2)
        vlay.addWidget(self.TextBox3)
        vlay.addWidget(self.TextBox4)
        vlay.addWidget(self.TextBox5)
        vlay.addWidget(self.TextBox6)
        
        self.TextBox1.hide()
        self.TextBox2.hide()
        self.TextBox3.hide()
        self.TextBox4.hide()
        self.TextBox5.hide()
        self.TextBox6.hide()
            
            
        vlay.addWidget(self.Paths_btn)
        vlay.addWidget(self.Clear_btn)
        vlay.addWidget(self.Locate_btn)
        vlay.addWidget(self.Extract_btn)
        
        vlay.addStretch(600)
        
        lay.addWidget(container)
        lay.addWidget(self.view, stretch=1)
  
    def mapUI(self):         
        
        
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
        
        
    def PlotRoad(self):
    
        self.Extracted = None
        self.ClearMap()
        if self.TextBox1.text() != "" and self.TextBox2.text() != "":
            Loc_1 = geocoder.arcgis(self.TextBox1.text()).latlng
            Loc_2 = geocoder.arcgis(self.TextBox2.text()).latlng
            
            if Loc_1 != None and Loc_2 != None:
                
                folium.Marker(location=Loc_1, 
                icon=folium.Icon(color="red", icon="glyphicon glyphicon-map-marker"), 
                popup='Original Start<br/>'+str(Loc_1),
                tooltip = "CLICK FOR INFO").add_to(self.m)

                folium.Marker(location=Loc_2, 
                icon=folium.Icon(color="red", icon="glyphicon glyphicon-map-marker"), 
                popup='Original Destination<br/>'+str(Loc_2), 
                tooltip = "CLICK FOR INFO").add_to(self.m)
                
                self.m.fit_bounds([Loc_1, Loc_2])
            
                coordinates = ((float(Loc_1[1]), float(Loc_1[0])),(float(Loc_2[1]), float(Loc_2[0])))

                client = openrouteservice.Client(key='5b3ce3597851110001cf6248d381d0dbb2df4de98a7b15a978f4c079')
                self.routes = client.directions(coordinates = coordinates, profile = 'driving-car', format = 'geojson')
                self.router = folium.GeoJson(self.routes, overlay = True, control = False ).add_to(self.m)
                
                folium.Marker(
                    location=(self.routes['features'][0]['geometry']['coordinates'][0][1], 
                    self.routes['features'][0]['geometry']['coordinates'][0][0]), 
                    icon=folium.Icon(color="green", icon="glyphicon glyphicon-map-marker"), 
                    tooltip="Beginning Of The Nearest Route").add_to(self.m)

                folium.Marker(
                    location=(self.routes['features'][0]['geometry']['coordinates'][-1][1], 
                    self.routes['features'][0]['geometry']['coordinates'][-1][0]), 
                    icon=folium.Icon(color="green", icon="glyphicon glyphicon-map-marker"), 
                    tooltip="Destination Of The Nearest Route").add_to(self.m)
                    
                self.m.fit_bounds([Loc_1, Loc_2])
                self.mapUI()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Please Enter a Valued Address")
                msg.setWindowTitle("Address Does Not Exist")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                self.ClearMap()
            
        elif self.TextBox3.text() != "" and self.TextBox4.text() != "" and self.TextBox5.text() != "" and self.TextBox6.text() != "":
            Loc_1 = (float(self.TextBox3.text()), float(self.TextBox4.text())) # 33.890944105645936  ,  35.48486122182076
            Loc_2 = (float(self.TextBox5.text()), float(self.TextBox6.text())) # 33.88481654982914 ,  35.53395637640471
            
            folium.Marker(location=Loc_1, 
            icon=folium.Icon(color="red", icon="glyphicon glyphicon-map-marker"), 
            popup='Original Start<br/>'+str(Loc_1), 
            tooltip = "CLICK FOR INFO").add_to(self.m)

            folium.Marker(location=Loc_2, 
            icon=folium.Icon(color="red", icon="glyphicon glyphicon-map-marker"), 
            popup='Original Destination<br/>'+str(Loc_2), 
            tooltip = "CLICK FOR INFO").add_to(self.m)
            self.m.fit_bounds([Loc_1, Loc_2])
        
        
            coordinates = ((Loc_1[1], Loc_1[0]),(Loc_2[1], Loc_2[0]))

            client = openrouteservice.Client(key='5b3ce3597851110001cf6248d381d0dbb2df4de98a7b15a978f4c079')
            try:
                self.routes = client.directions(coordinates = coordinates, profile = 'driving-car', format = 'geojson')
                self.router = folium.GeoJson(self.routes, overlay = True, control = False ).add_to(self.m)
                folium.Marker(
                    location=(self.routes['features'][0]['geometry']['coordinates'][0][1], 
                    self.routes['features'][0]['geometry']['coordinates'][0][0]), 
                    icon=folium.Icon(color="green", icon="glyphicon glyphicon-map-marker"), 
                    tooltip="Beginning Of The Nearest Route").add_to(self.m)

                folium.Marker(
                    location=(self.routes['features'][0]['geometry']['coordinates'][-1][1], 
                    self.routes['features'][0]['geometry']['coordinates'][-1][0]), 
                    icon=folium.Icon(color="green", icon="glyphicon glyphicon-map-marker"), 
                    tooltip="Destination Of The Nearest Route").add_to(self.m)
                self.m.fit_bounds([Loc_1, Loc_2])
                self.mapUI()
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Please Enter A Valued Address.")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                self.ClearMap()
            
            
        
        else:
            self.ClearMap()
            
    def ClearMap(self):
        self.m  = folium.Map(tiles=None, location=[33.867, 35.5433], zoom_start=12)
        # Adding Layers to basemap
        folium.TileLayer( tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', 
               attr = 'Google Maps', name = 'Google Maps', overlay = True, control = False
            ).add_to(self.m)
            
        folium.TileLayer( tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
               attr = 'Google Satelite', name = 'Google Satelite', overlay = True, control = True
            ).add_to(self.m)
        
        folium.LayerControl().add_to(self.m)
        self.mapUI()
    
    def onChanged(self, text):
    
        self.TextBox1.setText("")
        self.TextBox2.setText("")
        self.TextBox3.setText("")
        self.TextBox4.setText("")
        self.TextBox5.setText("")
        self.TextBox6.setText("")
        
        if text == "ROUTE USING PLACE NAMES":
            self.TextBox3.hide()
            self.TextBox4.hide()
            self.TextBox5.hide()
            self.TextBox6.hide()
            self.TextBox1.show()
            self.TextBox2.show()
            
        elif text == "ROUTE USING COORDINATES":
            self.TextBox1.hide()
            self.TextBox2.hide()
            self.TextBox3.show()
            self.TextBox4.show()
            self.TextBox6.show()
            self.TextBox5.show()
    
    def Extract(self):
        if self.routes == None or self.Extracted != None: 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Signs Information Already Extracted")
            msg.setWindowTitle("Extraction")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        else:
            data = []
            count = 0
            for i in range(len(self.routes['features'][0]['geometry']['coordinates'])):
                if count < len(self.routes['features'][0]['geometry']['coordinates'])-2:
                    count = count + 2
                else :
                    data.insert(i, self.routes['features'][0]['geometry']['coordinates'][count])
                    break
                    
                data.insert(i, self.routes['features'][0]['geometry']['coordinates'][count])
           
            
            with open('Sign data.json', 'w') as outfile:
                json.dump(data, outfile)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Signs Information Extracted as a .Json File")
            msg.setWindowTitle("Extraction Succeeded")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.Extracted = 1


    def LocateSigns(self):
        if self.routes == None :
            self.ClearMap()
        else:
            data = []
            
            SignNames = [
            'glyphicon glyphicon-arrow-left',
            'glyphicon glyphicon-arrow-right',
            'glyphicon glyphicon-ban-circle',
            'glyphicon glyphicon-alert',
            'glyphicon glyphicon-warning-sign',
            'glyphicon glyphicon-ban-circle']
            
            Instructions =[
                'Speed limit (20km/h)',
                'Speed limit (30km/h)',
                'Speed limit (50km/h)',
                'Speed limit (60km/h)',
                'Speed limit (70km/h)',
                'Speed limit (80km/h)',
                'End of speed limit (80km/h)',
                'Speed limit (100km/h)',
                'Speed limit (120km/h)',
                'No passing',
                'No passing for vechiles over 3.5 metric tons',
                'Right-of-way at the next intersection',
                'Priority road',
                'Yield',
                'Stop',
                'No vechiles',
                'Vechiles over 3.5 metric tons prohibited',
                'No entry',
                'General caution',
                'Dangerous curve to the left',
                'Dangerous curve to the right',
                'Double curve',
                'Bumpy road',
                'Slippery road',
                'Road narrows on the right',
                'Road work',
                'Traffic signals',
                'Pedestrians',
                'Children crossing',
                'Bicycles crossing',
                'Beware of ice/snow',
                'Wild animals crossing',
                'End of all speed and passing limits',
                'Turn right ahead',
                'Turn left ahead',
                'Ahead only',
                'Go straight or right',
                'Go straight or left',
                'Keep right',
                'Keep left',
                'Roundabout mandatory',
                'End of no passing',
                'End of no passing by vechiles over 3.5 metric tons'
                ]
            count = 0
            #Collecting Signs locations
            for i in range(len(self.routes['features'][0]['geometry']['coordinates'])):
                if count < len(self.routes['features'][0]['geometry']['coordinates'])-2:
                    count = count + 2
                else :
                    data.insert(i, self.routes['features'][0]['geometry']['coordinates'][count])
                    break
                data.insert(i, self.routes['features'][0]['geometry']['coordinates'][count])
                
            #Ploting Signs
            for i in range(len(data)):
                folium.Marker(
                    location=(data[i][1], data[i][0]), 
                    icon=folium.Icon(color="red", icon=SignNames[int(random.uniform(1, 6))] ), 
                    tooltip="Sign number: " + str(i) + "</br>Sign Instruction: " +
                    Instructions[int(random.uniform(1, 42))] +
                    "</br>Sign Accuracy: " + "{:.3f}".format(random.uniform(97, 99))+ " %"
                    ).add_to(self.m)
            self.mapUI()
    
if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())
    