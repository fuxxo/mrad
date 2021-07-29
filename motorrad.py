from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import re
import json
import datetime
import sys
from math import ceil
from copy import deepcopy

packages = {
    "Paquete Dinamico" : ["Intermitentes Led","Luz trasera led","Spoiler del motor","Cubre Colin"],
    "Paquete Confort" : ["Punhos calefactables","Ordenador de a bordo","Soporte de maletas","Caballete","Parrilla equipaje","Toma de corriente"],
    "Paquete Seguridad" : ["ASC", "ESA", "TPC", "Modos Pro"]
    }

features = {
    "A2" : "A2",
    "ASC" : "ASC",
    "ASC Control de Tracción" : "ASC",
    "Equipamiento Lanzamiento" : "Equipamiento Lanzamiento",
    "Maletas" : "Maletas",
    "Soporte de maletas" : "Soporte de maletas",
    "Alarma antirrobo" : "Alarma antirrobo",
    "Bien cuidado" : "",
    "ASC Control de tracción" : "ASC",
    "Tapicería piel" : "Tapicería piel",
    "A.B.S." : "",
    "Pintura metalizada" : "Pintura Metalizada",
    "Versión para EU" : "",
    "Parrilla para equipaje" : "Parrilla equipaje",
    "Spoiler del motor" : "Spoiler del motor",
    "Toma de corriente" : "Toma de corriente",
    "Llanta Especial de Diseño" : "Llanta Especial",
    "Llanta Especial de Dise¦o" : "Llanta Especial",
    "Llanta Especial" : "Llanta Especial",
    "DTC Control dinámico de tracción" : "DTC",
    "Intermitentes Led blancos" : "Intermitentes Led",
    "Quilla del motor" : "Spoiler del motor",
    "Ordenador de a bordo" : "Ordenador de a bordo",
    "Parrilla porta equipaje" : "Parrilla equipaje",
    "Parrilla equipaje" : "Parrilla equipaje",
    "TPC" : "TPC",
    "DTC" : "DTC",
    "Caballete central" : "Caballete",
    "ABS" : "",
    "Modos de conducción Pro" : "Modos Pro",
    "Pantalla" : "",
    "Reducción de potencia a 35kw (48CV)" : "A2",
    "Parabrisas Sport" : "Parabrisas Sport",
    "Llanta de diseño" : "Llanta Especial",
    "ESA" : "ESA",
    "Modos de conduccion Pro" : "Modos Pro",
    "Modos Pro" : "Modos Pro",
    "E.S.A. (Ajuste susp. electronica)" : "ESA",
    "Punos calefactables" : "Punhos calefactables",
    "Luz trasera de led" : "Luz trasera led",
    "Luz trasera led" : "Luz trasera led",
    "Topcase" : "Topcase",
    "Asiento alto." : "Asiento alto",
    "Asiento alto" : "Asiento alto",
    "Extensión garantía + 12 meses" : "Extensión garantía + 12 meses",
    "Paquete Dinamico" : "Paquete Dinamico",
    "Catalizador" : "Catalizador",
    "Asiento bajo" : "Asiento bajo",
    "Puños calefactables" : "Punhos calefactables",
    "Punhos calefactables" : "Punhos calefactables",
    "Acabados interiores" : "Acabados interiores",
    "Caballete" : "Caballete",
    "Manillar alto" : "Manillar alto",
    "Color Metalizado" : "Pintura Metalizada",
    "Pintura Metalizada" : "Pintura Metalizada",
    "Paquete Touring" : "Paquete Confort",
    "Paquete Confort" :"Paquete Confort",
    "Cubre Colin" : "Cubre Colin",
    "Intermitentes Led" : "Intermitentes Led",
    "Paquete Seguridad" : "Paquete Seguridad",
    "Control de presión de neumáticos" : "TPC",
}

def get_html(url):
    uClient = uReq(url)
    html_page = uClient.read()
    uClient.close()
    soup = BeautifulSoup(html_page, "html.parser")
    return soup
    
class motorradWeb:
    results_per_page = 12
    
    def __init__(self, url='https://www.bmwmotorradpremiumselection.es/motos-de-ocasion/bmw-motorrad/f/f-800-r?condicion[marca]=BMW%20Motorrad&condicion[modelo]=F%20800%20R&gama=F&ordenacion=precio_ascendente'):
        self.web = url
        self.links = list()
        
    def getLinks(self, url):
        soup = get_html(url)
        tlinks = []
        for link in soup.findAll('a', attrs={'href': re.compile("^/moto")}):
            l = link.get('href')
            if re.search(r'\d+$',l):
                tlinks.append('https://www.bmwmotorradpremiumselection.es' + l)
        return sorted(list(set(tlinks)))

    def loadLinksFromWeb(self):
        soup = get_html(self.web)
        n_items = int(soup.select(".list-grid-top > div:nth-child(1) > h2:nth-child(1) > span:nth-child(1)")[0].get_text())
        n_pages = ceil(n_items/self.results_per_page)
        for i in range(1,n_pages+1):
            url = self.web + "&pagina=" + str(i)
            nl = self.getLinks(url)
            self.links.extend(nl)
            print("{} links found in page {}".format(len(nl),url))
        self.links = sorted(list(set(self.links)))
        print("{}(/{}) total links found in {}".format( len(self.links), n_items, self.web))
        return self.links

    def loadLinksFromFile(self, links_file="motorrad_links.json"):
        urls = json.load(open(links_file))
        for base, urls in urls.items():
            self.links.extend( urls )
        self.links = sorted(list(set(self.links)))
        return self.links
    
    def loadLinksFromList(self, mlist):
        self.links.extend( urls )
        self.links = sorted(list(set(self.links)))
        return self.links

    def dumpLinksToFile(self, links_file="data/motorrad_links-"+datetime.datetime.today().isoformat()+".json"):
        with open(links_file,'w') as ml:
            json.dump({ self.web : sorted(self.links)}, ml, indent=4, sort_keys=True)
        return links_file
            
class motorradItem:
    actions = {"reference"     : { "formatter" : (lambda item : int(item)),
                                   "fallback"  : (lambda : 0),
                                   "parser"    : (lambda s : s.select('.wrap-ficha > h1:nth-child(2) > b:nth-child(2)')[0].get_text().split(':')[1].strip(' ')) },
               "vin"           : { "formatter" : (lambda item : item),
                                   "fallback"  : (lambda : 0),
                                   "parser"    : (lambda s : (re.search( r"WB\w+", s.select('.file-head > div:nth-child(2) > dl')[0].get_text())).group()) },
               "price"         : { "formatter" : (lambda item : float(item)), 
                                   "fallback"  : (lambda : 1),
                                   "parser"    : (lambda s : s.select('div.file-head div div.price p#oferta_financiado_2.destaco b')[0].get_text().split(' ')[0].replace('.','')) },
               "premium"       : { "formatter" : (lambda item : item),
                                   "fallback"  : (lambda : "No"),
                                   "parser"    : (lambda s : ("Yes" if (len(s.findAll("div", {"class":"file-grid p-ventajas"})) > 0) else "No")) },
               "warranty"      : { "formatter" : (lambda item : int(item)),
                                   "fallback"  : (lambda : 0),
                                   "parser"    : (lambda s : s.select('a.show_garantia:nth-child(3) > span:nth-child(1)')[0].get_text().split(' ')[0]) },
               "price-new"     : { "formatter" : (lambda item : float(item)),
                                   "fallback"  : (lambda : 1),
                                   "parser"    : (lambda s : s.select('p.ahorro:nth-child(2)')[0].get_text().split(' ')[8].replace('.','')) },
               "equip"         : { "formatter" : (lambda item : item),
                                   "fallback"  : (lambda : []),
                                   "parser"    : (lambda s : sorted(list(set(s.select('.equip')[0].get_text().split('\n') + s.select('div.file-grid:nth-child(7)')[0].get_text().split('\n'))))) },
               "mat"           : { "formatter" : (lambda item : item),
                                   "fallback"  : (lambda : "01/01/1990"),
                                   "parser"    : (lambda s : s.findAll("div", {"class":"file-grid p-tecnicos"})[0].select('div:nth-child(1) > dl:nth-child(1) > dd:nth-child(4)')[0].get_text().replace(' ','')) },
               "kms"           : { "formatter" : (lambda item : int(item)),
                                   "fallback"  : (lambda : 0),
                                   "parser"    : (lambda s : s.findAll("div", {"class":"file-grid p-tecnicos"})[0].select('div:nth-child(1) > dl:nth-child(1) > dd:nth-child(6)')[0].get_text().split(' ')[0].replace('.',''))},
               "color"         : { "formatter" : (lambda item : item),
                                   "fallback"  : (lambda : "Unknown"),
                                   "parser"    : (lambda s : s.findAll("div", {"class":"file-grid p-tecnicos"})[0].select('div:nth-child(2) > dl:nth-child(1) > dd:nth-child(6)')[0].get_text())},
               "emissions"     : { "formatter" : (lambda item : item),
                                   "fallback"  : (lambda : "E2"), 
                                   "parser"    : (lambda s : s.findAll("div", {"class":"file-grid p-tecnicos"})[0].select('div:nth-child(2) > dl:nth-child(1) > dd:nth-child(10)')[0].get_text())},
               "observaciones" : { "formatter" : (lambda item : item.replace("\n"," ")),
                                   "fallback"  : (lambda : "Sin observaciones"),
                                   "parser"    : (lambda s : s.select('.p-observaciones > p:nth-child(1)')[0].get_text())},
               "concesionario" : { "formatter" : (lambda item : item.replace("\n\n","").replace("\n"," | ")),
                                   "fallback"  : (lambda : "Concesionario desconocido"),
                                   "parser"    : (lambda s : s.findAll("div", {"class":"file-grid p-concesionario"})[0].div.get_text())}
    }
    
    def __init__(self, mdata=None, url=None):
        if mdata != None:
            self.data = deepcopy(mdata)
        elif url != None:
            self.data = self.parseWebPage(url) #sorted
        else:
            self.data = {}
        for key, val in self.actions.items():
            if ((key not in self.data) or (self.data[key]==None) or (self.data[key]=="")):
                self.data[key] = self.actions[key]["fallback"]()
            self.data[key] = self.actions[key]["formatter"](self.data[key])
        if re.search("Tenerife", self.data["concesionario"]) != None:  # Traerlo desde Canarias: +21% IVA
            self.data['price'] += 0.21 * self.data['price-new']
        s_equip = []
        for i, feature in enumerate(self.data["equip"]):        # 1...
            if feature and features[feature]:
                s_equip.append( features[feature] )
        self.data["equip"] = s_equip                            # ...translated
        for feature in self.data["equip"]:                      # 2...
            if feature in packages:
                s_equip.extend( packages[feature] )             # ...analyzed
        self.data["equip"] = s_equip                            # ...translated                
        s_equip = set(self.data["equip"])                       # 3...
        for key, val in packages.items():
            s_val = set(val)
            if s_val.issubset(s_equip):
                s_equip.difference_update(s_val)
                s_equip.add(key)
        self.data["equip"] = sorted(list(s_equip))              # ...synthesized
        self.data["abs-save"] = self.data["price-new"]-self.data["price"]
        self.data["rel-save"] = 1-self.data["price"]/self.data["price-new"]
        
    def __eq__(self,other):
        miss = False
        for key, val in self.data.items():
            if self.data[key] != other.data[key]:
                miss = True
                break
        return not(miss)

    def __hash__(self):
        return id(self)
    
    def sameProduct(self,other):
        return self.data["vin"] == other.data["vin"]
    
    def has(self,filter):
        miss = False
        for key,val in filter.items():
            if key == "equip":
                miss = not(set(self.data[key]).issuperset(set(val)))
            elif key == "mat":
                df = datetime.datetime.strptime(filter[key] ,'%d/%m/%Y')
                dm = datetime.datetime.strptime(self.data[key] ,'%d/%m/%Y')
                miss = dm < df
            elif key == "kms":
                miss = self.data[key] > val
            elif key == "price-new":
                miss = self.data[key] < val                
            else:
                miss = self.data[key] != val                
            if miss:
                break
        return not(miss)

    def __str__(self):
        return "\r\n".join([ "{:>16} : {}".format(key,val) for key,val in sorted(list(self.data.items()))])

    def parseWebPage(self,url):
        print("Parsing {}".format(url))
        soup = get_html(url)
        item = {"url":url}
        for key in self.actions:
            try:
                item[key] = self.actions[key]["parser"](soup)
            except Exception as e:
                #e = sys.exc_info()[0]
                print("Got {} for key \'{} \'".format( str(e), key ))
                item[key] = self.actions[key]["fallback"]()
        return item
    
    
class motorradDB(list):
    def __init__(self, *args):
        list.__init__(self, *args)

    def loadFromFile(self, db_file="motorrad_db.json"):
        temp = json.load(open(db_file))
        for item in temp:
            self.append( motorradItem( mdata=item ) )

    def loadFromUrls(self, urls):
        print("\nParsing {} urls".format(len(urls)))
        for i,u in enumerate(urls,1):
            print("\nUrl-{}".format(i))
            item = motorradItem( url=u )
            print(item)
            self.append( item )

    def dumpToFile(self, db_file="data/motorrad_db-"+datetime.datetime.today().isoformat()+".json"):
        d = [item.data for item in self]
        with open(db_file,'w') as ml:
            json.dump( d, ml, indent=4, sort_keys=True)
        return db_file
            
    def filter(self, filt):
        temp = motorradDB()
        for item in self:
            if item.has(filt):
                temp.append(item)
        return temp

    def allFeatures(self):
        equip_set=set()
        for item in self:
            equip_set.update(set(item.data["equip"]))
        return sorted(list(equip_set))

    def add(self, item):
        self.append(item)
        
    def __str__(self):
        out = [ str(item) for item in self]
        info = "There are {} results".format(len(out))
        return str("\r\n\r\n-------------\r\n".join(out) + "\r\n\r\n{}\r\n".format(info))

    def plot( self, keys_list ):
        # Bokeh Libraries
        from bokeh.io import output_file
        from bokeh.plotting import figure, show
        from bokeh.palettes import Turbo256
        from bokeh.models import ColumnDataSource, OpenURL, TapTool
        from bokeh.transform import linear_cmap
        from bokeh.layouts import gridplot

        TOOLTIPS = [
            ("Ref", "@reference"),
            ("Precio", "@price"),
            ("Nuevo", "@{price-new}"),
            ("Ahorro", "@{rel-save}"),
            ("Matriculacion", "@mat"),
            ("Kms", "@kms"),
            ("Extras","@equip")
        ]
        # Specify the tools
        toolList = ['lasso_select', 'tap', 'reset', 'save']
        output_file('bmwmotorrad.html', title='BMW Motorrad DashBoard')
        
        # Coordinate data
        data = dict()
        for key, value in self[0].data.items():
            data[key] = list()
        for item in self:
            for key,val in item.data.items():
                data[key].append(val)
        for keys in keys_list:
            mi,ma = (min(data[keys["u"]]),max(data[keys["u"]]))
            data[keys["u"]+'-size'] = [ (((i-mi)/(ma-mi))*80)+8 for i in data[keys["u"]] ]
        source = ColumnDataSource(data=data)

        figs = list()
        for keys in keys_list:
            fig = figure(title=None,
                         plot_height=1200, plot_width=1200,
                         toolbar_location=None,
                         tooltips=TOOLTIPS,
                         tools=toolList, sizing_mode="stretch_both")
            fig.circle(x=keys["x"], y=keys["y"],
                       size=keys["u"]+'-size', fill_color=linear_cmap(keys["v"], 'Turbo256', low=min(data[keys["v"]]), high=max(data[keys["v"]])),
                       source=source,alpha=0.5)
            taptool = fig.select(type=TapTool)
            taptool.callback = OpenURL(url="@url")
            if keys["interpolation"] > 0:
                poly = np.polyfit( data[keys["x"]], data[keys["y"]], keys["interpolation"])
                yi = np.poly1d(poly)
                xi = np.linspace( min(data[keys["x"]]) , max(data[keys["x"]]) )
                fig.line(x=xi,y=yi(xi), line_width=2)
                
            figs.append(fig)
                
        # Create layout
        grid = gridplot([figs])

        # Visualize
        show(grid)
