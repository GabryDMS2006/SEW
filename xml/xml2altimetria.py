# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 18:53:52 2026

@author: Gaby
"""

import xml.etree.ElementTree as ET

class Svg(object):
    """
    Genera archivos SVG con rectángulos, círculos, líneas, polilíneas y texto
    @version 1.0 18/Octubre/2024
    @author: Juan Manuel Cueva Lovelle. Universidad de Oviedo
    """
    def __init__(self):
        """
        Crea el elemento raíz, el espacio de nombres y la versión
        """
        self.raiz = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="2.0")

    
    def addRect(self,x,y,width,height,fill, strokeWidth,stroke):
        """
        Añade un elemento rect
        """
        ET.SubElement(self.raiz,'rect',
                      x=x,
                      y=y,
                      width=width,
                      height=height,
                      fill=fill, 
                      strokeWidth=strokeWidth,
                      stroke=stroke)
        
    def addCircle(self,cx,cy,r,fill):
        """
        Añade un elemento circle
        """
        ET.SubElement(self.raiz,'circle',
                      cx=cx,
                      cy=cy,
                      r=r,
                      fill=fill)
        
    def addLine(self,x1,y1,x2,y2,stroke,strokeWith):
        """
        Añade un elemento line
        """
        ET.SubElement(self.raiz,'line',
                      x1=x1,
                      y1=y1,
                      x2=x2,
                      y2=y2,
                      stroke=stroke,
                      strokeWith=strokeWith)

    def addPolyline(self,points,stroke,strokeWith,fill):
        """
        Añade un elemento polyline
        """
        ET.SubElement(self.raiz,'polyline',
                      points=points,
                      stroke=stroke,
                      strokeWith=strokeWith,
                      fill=fill)
        
    def addText(self,texto,x,y,fontFamily,fontSize,style):
        """
        Añade un elemento texto
        """
        ET.SubElement(self.raiz,'text',
                      x=x,
                      y=y,
                      fontFamily=fontFamily,
                      fontSize=fontSize,
                      style=style).text=texto

    def escribir(self,nombreArchivoSVG):
        """ de
        Escribe el archivo SVG con declaración y codificación
        """
        arbol = ET.ElementTree(self.raiz)
        
        """
        Introduce indentacióon y saltos de línea
        para generar XML en modo texto
        """
        ET.indent(arbol)
        
        arbol.write(nombreArchivoSVG, 
                    encoding='utf-8', 
                    xml_declaration=True
                    )

class Xml2Altimetria(object):
    
    def __init__(self, nombreXML):
        
        self.nombreXML = nombreXML
        
        self.arbol = ET.parse(nombreXML)
        self.raiz = self.arbol.getroot()
        
        self.puntos = []
        
        self.svg = Svg()
        self.ancho = 1200
        self.alto = 500
        
        self.margenIzquierdo = 70
        self.margenDerecho = 30
        self.margenSuperior = 50
        self.margenInferior = 150
    
    def obtenerPuntos(self):
    
        
        salida = self.raiz.find('{*}lugar_Salida/{*}coordenadas_geograficas')        
        altitud = float(salida.find('{*}altitud').text)
        
        self.puntos.append((0.0, altitud))
        
        elementos = self.raiz.findall('.//{*}puntoAnónimo')
        
        for elemento in elementos:
            
            distancia = float(elemento.find('{*}distancia').text)
            coordenadas = elemento.find('{*}coordenadas_geograficas')
            altitud = float(coordenadas.find('{*}altitud').text)
            
            self.puntos.append((distancia, altitud))
        
        elementos = self.raiz.findall('.//{*}puerto_montaña')
        
        for elemento in elementos:
            
            distancia = float(elemento.find('{*}distancia').text)

            coordenadas = elemento.find('{*}coordenadas_geograficas')

            altitud = float(coordenadas.find('{*}altitud').text)

            self.puntos.append((distancia, altitud))

        elementos = self.raiz.findall('.//{*}sprint_intermedio')

        for elemento in elementos:

            distancia = float(elemento.find('{*}distancia').text)

            coordenadas = elemento.find('{*}coordenadas_geograficas')

            altitud = float(coordenadas.find('{*}altitud').text)

            self.puntos.append((distancia, altitud))

        
        meta = self.raiz.find('{*}lugar_Meta/{*}coordenadas_geograficas')
        

        altitud = float(meta.find('{*}altitud').text)
        

        longitudEtapa = float(self.raiz.find('{*}longitud_Etapa').text)
        

        self.puntos.append((longitudEtapa, altitud))

        self.puntos.sort(key=lambda punto: punto[0])
        
        return self.puntos
    
    def convertirPunto(self, distancia, altitud,
                       distanciaMaxima, altitudMaxima):

        """
        Convierte distancia y altitud en coordenadas SVG.
        """

        anchoGrafica = (self.ancho
            - self.margenIzquierdo
            - self.margenDerecho)

        altoGrafica = (self.alto
            - self.margenSuperior
            - self.margenInferior)

        x = (self.margenIzquierdo
            + distancia / distanciaMaxima * anchoGrafica)

        y = (self.alto
            - self.margenInferior
            - altitud / altitudMaxima * altoGrafica)

        return x, y

    def generarGrafica(self):

        puntos = self.obtenerPuntos()

        distanciaMaxima = puntos[-1][0]

        altitudMaxima = max(punto[1] for punto in puntos)

        #Perfil de altimetría
        puntosSVG = []

        for distancia, altitud in puntos:

            x, y = self.convertirPunto(
            distancia,
            altitud,
            distanciaMaxima,
            altitudMaxima)

            puntosSVG.append(str(x) + ',' + str(y))

        puntos = ' '.join(puntosSVG)

        self.svg.addPolyline(
        puntos,
        'red',
        '5',
        'none')

        # Escala horizontal
        yEscala = self.alto - self.margenInferior

        self.svg.addLine(
        str(self.margenIzquierdo),
        str(yEscala),
        str(self.ancho - self.margenDerecho),
        str(yEscala),
        'black',
        '1')

        
        for distancia in range(0, 181, 20):

            if distancia > distanciaMaxima:
                distancia = distanciaMaxima

            x, y = self.convertirPunto(distancia,
            0,
            distanciaMaxima,
            altitudMaxima)

            self.svg.addLine(
            str(x),
            str(yEscala),
            str(x),
            str(yEscala + 5),
            'black',
            '1')

            self.svg.addText(
            str(distancia),
            str(x - 8),
            str(yEscala + 20),
            'Arial',
            '11',
            ''
        )
            
        xEscala = self.margenIzquierdo
        
        self.svg.addLine(str(xEscala), str(self.margenSuperior), 
                         str(xEscala), str(yEscala), 
                         'black', '1')
        
        for altitud in range(0,401,100):
            
            if altitud > altitudMaxima:
                altitud = altitudMaxima
            
            x,y = self.convertirPunto(0, altitud, distanciaMaxima, 
                                      altitudMaxima)
            
            self.svg.addLine(str(xEscala-5), 
                             str(y), str(xEscala), 
                             str(y), 'black', '1')
            
            self.svg.addText(str(altitud), str(xEscala-35), 
                             str(y+4), 
                             'Arial', 
                             '11', 
                             '')
            

        # Salida
        x, y = self.convertirPunto(
        0,
        self.puntos[0][1],
        distanciaMaxima,
        altitudMaxima)

        self.svg.addText(
        'Salida',
        str(x - 15),
        str(yEscala + 45),
        'Arial',
        '12',
        '')

        # Sprint
        elementos = self.raiz.findall('.//{*}sprint_intermedio')

        for elemento in elementos:

            distancia = float(elemento.find('{*}distancia').text)

            nombre = elemento.get('nombre')

            x, y = self.convertirPunto(
            distancia,
            0,
            distanciaMaxima,
            altitudMaxima)

            self.svg.addText(
            nombre,
            str(x - 15),
            str(yEscala + 45),
            'Arial',
            '12',
            '')
            
        elementos = self.raiz.findall('.//{*}sprint_bonificado')

        for elemento in elementos:

             distancia = float(elemento.find('{*}distancia').text)

             nombre = elemento.get('nombre')

             x, y = self.convertirPunto(
             distancia,
             0,
             distanciaMaxima,
             altitudMaxima)

             self.svg.addText(
             nombre,
             str(x - 15),
             str(yEscala + 45),
             'Arial',
             '12',
             '')

        # Puerto de montaña
        elementos = self.raiz.findall('.//{*}puerto_montaña')

        for elemento in elementos:

            distancia = float(elemento.find('{*}distancia').text)

            nombre = elemento.get('nombre')

            x, y = self.convertirPunto(
            distancia,
            0,
            distanciaMaxima,
            altitudMaxima)

            self.svg.addText(
            nombre,
            str(x - 25),
            str(yEscala + 45),
            'Arial',
            '12',
            '')

        # Meta
        x, y = self.convertirPunto(
        distanciaMaxima,
        0,
        distanciaMaxima,
        altitudMaxima)

        self.svg.addText(
        'Meta',
        str(x - 15),
        str(yEscala + 45),
        'Arial',
        '12',
        '')

        # Título
        nombreEtapa = self.raiz.find('{*}nombre_Etapa').text

        self.svg.addText(nombreEtapa,
        '500',
        '30',
        'Arial',
        '18',
        '')
    
    def ejecutar(self):
        
        self.generarGrafica()
        self.svg.escribir('altimetria.svg')

        print('Creado el archivo: altimetria.svg')

def main():
    
    program = Xml2Altimetria("etapaEsquema.xml")
    program.ejecutar()
    
if __name__ == "__main__":
    main()