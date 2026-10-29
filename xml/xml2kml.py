# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 09:38:46 2026

@author: Gaby
"""

import xml.etree.ElementTree as ET
import sys


class Kml(object):
   
    ROJO = 'ff0000ff'
    VERDE = 'ff00ff00'
    AZUL = 'ffff0000'
    AMARILLO = 'ff00ffff'
   
    def __init__(self):
        """
        Crea el elemento raíz y el espacio de nombres
        """
        self.raiz = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz,'Document')

    def addPlacemark(self,nombre,descripcion,long,lat,alt, modoAltitud, idEstilo):
        """
        Añade un elemento <Placemark> con puntos <Point>
        """
        pm = ET.SubElement(self.doc,'Placemark')
        ET.SubElement(pm,'name').text = nombre
        ET.SubElement(pm,'description').text = descripcion
        ET.SubElement(pm, 'styleUrl').text = '#' + idEstilo
        punto = ET.SubElement(pm,'Point')
        ET.SubElement(punto,'coordinates').text = '{},{},{}'.format(long,lat,alt)
        ET.SubElement(punto,'altitudeMode').text = modoAltitud

    def addEstilo(self, idEstilo, color):
        
        estilo = ET.SubElement(self.doc, 'Style', id=idEstilo)
        icono = ET.SubElement(estilo, 'IconStyle')
        ET.SubElement(icono, 'color').text = color
        ET.SubElement(ET.SubElement(icono, 'Icon'), 'href').text =\
            'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
        
    def addLineString(self,nombre,extrude,tesela, listaCoordenadas, modoAltitud, color, ancho):
        """
        Añade un elemento <Placemark> con líneas <LineString>
        """
        pm = ET.SubElement(self.doc,'Placemark')
        ET.SubElement(pm,'name').text = nombre
        ls = ET.SubElement(pm, 'LineString')
        ET.SubElement(ls,'extrude').text = extrude
        ET.SubElement(ls,'tessellation').text = tesela
        ET.SubElement(ls,'altitudeMode').text = modoAltitud 
        ET.SubElement(ls,'coordinates').text = listaCoordenadas

        estilo = ET.SubElement(pm, 'Style')
        linea = ET.SubElement(estilo, 'LineStyle')
        ET.SubElement (linea, 'color').text = color
        ET.SubElement (linea, 'width').text = ancho

    
    def escribir(self,nombreArchivoKML):
        """
        Escribe el archivo KML con declaración y codificación
        """
        arbol = ET.ElementTree(self.raiz)
        """
        Introduce indentacióon y saltos de línea
        para generar XML en modo texto
        """
        ET.indent(arbol)
        arbol.write(nombreArchivoKML, encoding='utf-8', xml_declaration=True)

class Xml2Kml(object):
    
    XP_SALIDA = ".//{*}lugar_Salida"
    XP_META = ".//{*}lugar_Meta"
    XP_PUERTOS = ".//{*}hitos_Importantes/{*}puerto_montaña"
    XP_SPRINTS = ".//{*}hitos_Importantes/{*}sprint_intermedio"
    XP_PUNTOS = ".//{*}puntos_Anónimos/{*}puntoAnónimo"
    
    MAX_ANONIMOS = 30
    
    
    def __init__(self, archivoXML, archivoKML):
        
       self.archivoXML = archivoXML
       self.archivoKML = archivoKML
       self.raiz = None
       self.kml = Kml()
       
    def leerXML(self):
        
        try:
            self.raiz = ET.parse(self.archivoXML).getroot()
        except IOError:
            print('No se encuentra el archivo', self.archivoXML)
            sys.exit(1)
        except ET.ParseError:
            print('Error procesando el archivo XML', self.archivoXML)
            sys.exit(1)
    
    def valor (self, elemento, nombre):
        
        if nombre in elemento.attrib:
            return elemento.attrib[nombre].strip()
        hijo = elemento.find('./{*}' + nombre)
        if hijo is not None and hijo.text:
            return hijo.text.strip()
        return None
    
    def coordenadas(self, elemento):
        
        origen = elemento.find('.//{*}coordenadas_geograficas')
        
        if origen is None:
            origen = elemento
        return (self.valor(origen, 'longitud'),
                self.valor(origen, 'latitud'),
                self.valor(origen, 'altitud') or '0')
    
    
    def nombre(self, elemento, porDefecto):
        return self.valor(elemento, 'nombre') or porDefecto
    
    def aniadirPuntos(self, xpath, idEstilo, descripcion):
        
        for i in self.raiz.findall(xpath):
            long, lat, alt = self.coordenadas(i)
            if long is None or lat is None:
                continue
            self.kml.addPlacemark(self.nombre(i, descripcion), 
                                  descripcion, long, lat, alt, 
                                  'relativeToGround', idEstilo)
    
    def extremo(self, xpath):
        
        e = self.raiz.find(xpath)
        return self.coordenadas(e)
    
    def reducir(self, lista, maximo):
        
        if len(lista)<=maximo:
            return lista
        paso = (len(lista)-1)/(maximo-1)
        
        reducida=[]
        for i in range(maximo):
            posicion = round(i*paso)
            reducida.append(lista[posicion])
        return reducida
 
    def generar(self):
        
        self.leerXML()
        
        for i,c in (('rojo', Kml.ROJO), ('verde', Kml.VERDE),
                    ('azul', Kml.AZUL), ('amarillo', Kml.AMARILLO)):
            self.kml.addEstilo(i,c)
            
        self.aniadirPuntos(self.XP_SALIDA, 'rojo', 'Salida')
        self.aniadirPuntos(self.XP_META, 'rojo', 'Meta')
        self.aniadirPuntos(self.XP_PUERTOS, 'verde', 'Puerto de montaña')
        self.aniadirPuntos(self.XP_SPRINTS, 'azul', 'Sprint intermedio')
        
        anonimos = []
        
        for i in self.raiz.findall(self.XP_PUNTOS):
            
            long,lat,alt = self.coordenadas(i)
            if long is not None and lat is not None:
                anonimos.append((self.nombre(i, None), long, lat, alt))
        anonimos = self.reducir(anonimos, self.MAX_ANONIMOS)
        
        for n, (nom, long, lat, alt) in enumerate(anonimos,1):
            self.kml.addPlacemark(nom or 'Punto ' + str(n), 
                                  'Punto anónimo', 
                                  long, lat, alt, 'relativeToGround', 'amarillo')
        
        trazado = [self.extremo(self.XP_SALIDA)]
        
        for p in anonimos:
            trazado.append((p[1], p[2], p[3]))
        trazado.append(self.extremo(self.XP_META))
        
        coords = '\n'.join('{},{},{}'.format(*p) for p in trazado)
        self.kml.addLineString('Etapa', '1', '1', coords, 
                               'relativeToGround', Kml.ROJO, '4')
    def escribir(self):
        
        self.kml.escribir(self.archivoKML)
        print('Creado el archivo: ', self.archivoKML)
        
def main():
        
    archivoKML = 'etapa.kml'
        
    if len(sys.argv)>1:
        archivoXML = sys.argv[1]
    else:
        archivoXML = 'etapaEsquema.xml'
        
    conversor = Xml2Kml(archivoXML, archivoKML)
    conversor.generar()
    conversor.escribir()
 
if __name__ == '__main__':
    main()