# Cliente.py

import json
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import NumericProperty, StringProperty
from kivy.network.urlrequest import UrlRequest
# ==============================================================================
# CONFIGURACIÓN DE CONEXIÓN CON LA LAPTOP
# ==============================================================================
IP_SERVIDOR = "10.144.43.56"  # <-- Cambia por la IP real de tu laptop en el Wi-Fi
URL_SERVER = f"http://{IP_SERVIDOR}:5000"
# --- UI KIVY CORREGIDA Y COMPLETA ---
KV = '''
ScreenManager:
    MenuScreen:
    ConteoScreen:
    LecturasScreen:
    VariacionesScreen:
<MenuScreen>:
    name: "menu"
    BoxLayout:
        orientation: 'vertical'
        padding: [20,30,20,20]
        spacing: 10
        Image:
            source: "logo_geo2.png"
            size_hint_y: None
            height: 120
            allow_stretch: True
        Label:
            text: "CC e Inventario Geodis"
            font_size: '26sp'
            bold: True
            halign: 'center'
            color: 1,1,1,1
            size_hint_y: None
            height: 40
        Button:
            text: "Inicializar nuevo Inventario"
            on_press: root.respaldar_inicializar()
            background_color: .11,.55,.65,1
            font_size: 20
        Button:
            text: "Generar Congelado"
            on_press: root.generar_congelado()
            background_color: .11,.49,.92,1
            font_size: 20
        Button:
            text: "Iniciar Conteo"
            on_press: app.root.current = "conteo"
            background_color: .23,.72,.48,1
            font_size: 20
        Button:
            text: "Ver lecturas"
            on_press: app.root.get_screen("lecturas").actualizar(); app.root.current = "lecturas"
            background_color: .18,.56,.80,1
            font_size: 20
        Button:
            text: "Reporte de Variaciones"
            on_press: app.root.get_screen("variaciones").actualizar(); app.root.current = "variaciones"
            background_color: .81,.59,.15,1
            font_size: 20
        Button:
            text: "Exportar Archivo final .xls"
            on_press: root.exportar_diferencias()
            background_color: .75,.11,.31,1
            font_size: 20
        Button:
            text: "Salir"
            on_press: app.stop()
            background_color: .3,.3,.3,1
            font_size: 20
<ConteoScreen>:
    name: "conteo"
    BoxLayout:
        orientation: 'vertical'
        padding: [20,20,20,20]
        spacing: 10
        Label:
            id: lbl
            text: root.mensaje_paso()
            font_size: '25sp'
            color: 1,1,1,1
            size_hint_y: None
            height: 40
        TextInput:
            id: txt
            font_size: '25sp'
            size_hint_y: None
            height: 50
            on_text_validate: root.procesar()
            multiline: False
            hint_text: "Escanear o ingresar dato"
            focus: True
        Label:
            id: estado
            text: root.estado
            color: .7,0,0,1
            font_size: '14sp'
            size_hint_y: None
            height: 24
        BoxLayout:
            size_hint_y: None
            height: 38
            spacing: 5
            Button:
                text: "Cambiar Sloc"
                on_press: root.set_paso(1)
            Button:
                text: "Cambia Ubicación"
                on_press: root.set_paso(2)
            Button:
                text: "Salir al menú"
                on_press: app.root.current = "menu"
        Label:
            id: lbl_avance
            text: ""
            font_size: '14sp'
            color: 1, 1, 1, 1
            size_hint_y: None
            height: 120
<LecturasScreen>:
    name: "lecturas"
    BoxLayout:
        orientation: 'vertical'
        padding: [10,20,10,10]
        spacing: 6
        Label:
            text: "Lecturas Registradas"
            font_size: '25sp'
            color: 1, .5, 0, 1
            size_hint_y: None
            height: 38
        BoxLayout:
            size_hint_y: None
            height: 34
            spacing: 3
            TextInput:
                id: filtro
                hint_text: "Filtrar"
                multiline: False
                on_text: root.actualizar()
            Button:
                text: "Limpiar"
                size_hint_x: None
                width: 80
                on_press: filtro.text = ""
        ScrollView:
            BoxLayout:
                id: lecturas
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 4
        Button:
            text: "Volver al Menú"
            size_hint_y: None
            height: 44
            on_press: app.root.current = "menu"
<VariacionesScreen>:
    name: "variaciones"
    BoxLayout:
        orientation: 'vertical'
        padding: [10,20,10,10]
        spacing: 6
        Label:
            text: "Reporte de Variaciones"
            font_size: '20sp'
            color: .81,.35,.05,1
            size_hint_y: None
            height: 38
        ScrollView:
            BoxLayout:
                id: variaciones
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 4
        Button:
            text: "Volver al Menú"
            size_hint_y: None
            height: 44
            on_press: app.root.current = "menu"
'''
HEADERS_JSON = {'Content-type': 'application/json', 'Accept': 'application/json'}
def popup_mensaje(titulo, mensaje):
    box = BoxLayout(orientation='vertical', padding=10, spacing=10)
    box.add_widget(Label(text=mensaje, halign="center"))
    btn = Button(text="OK", size_hint_y=None, height=40)
    box.add_widget(btn)
    popup = Popup(title=titulo, content=box, size_hint=(.8, .4), auto_dismiss=False)
    btn.bind(on_press=popup.dismiss)
    popup.open()
def pedir_confirmacion(mensaje, accion_si, accion_no):
    box = BoxLayout(orientation='vertical', padding=10, spacing=10)
    box.add_widget(Label(text=mensaje))
    btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
    btn_si = Button(text="SÍ")
    btn_no = Button(text="NO")
    btns.add_widget(btn_si)
    btns.add_widget(btn_no)
    box.add_widget(btns)
    popup = Popup(title="Confirmar", content=box, size_hint=(.8, .4), auto_dismiss=False)
    btn_si.bind(on_press=lambda x: (popup.dismiss(), accion_si()))
    btn_no.bind(on_press=lambda x: (popup.dismiss(), accion_no()))
    popup.open()
def solicitar_password(accion_si, accion_no):
    box = BoxLayout(orientation='vertical', padding=10, spacing=10)
    box.add_widget(Label(text="Ingrese contraseña de administrador:"))
    txt = TextInput(password=True, multiline=False)
    box.add_widget(txt)
    btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
    btn_si = Button(text="Validar")
    btn_no = Button(text="Cancelar")
    btns.add_widget(btn_si)
    btns.add_widget(btn_no)
    box.add_widget(btns)
    popup = Popup(title="Validación", content=box, size_hint=(.8, .4), auto_dismiss=False)
    def validar(_):
        if txt.text == "1701":
            popup.dismiss()
            accion_si()
        else:
            popup_mensaje("Error", "Contraseña incorrecta")
    btn_si.bind(on_press=validar)
    btn_no.bind(on_press=lambda x: (popup.dismiss(), accion_no()))
    popup.open()
class MenuScreen(Screen):
    def respaldar_inicializar(self):
        def ejecutar():
            UrlRequest(
                f"{URL_SERVER}/inicializar",
                on_success=lambda r, res: popup_mensaje("Listo", res.get("mensaje")),
                on_failure=lambda r, e: popup_mensaje("Error", "La laptop rechazó la solicitud."),
                on_error=lambda r, e: popup_mensaje("Error de Red", "Laptop inalcanzable."),
                method='POST', timeout=5
            )
        solicitar_password(ejecutar, lambda: None)
    def generar_congelado(self):
        def correr_proceso():
            UrlRequest(
                f"{URL_SERVER}/generar_congelado",
                on_success=lambda r, res: popup_mensaje("Éxito", res.get("mensaje")),
                on_failure=lambda r, e: popup_mensaje("Error", "No se pudo generar."),
                on_error=lambda r, e: popup_mensaje("Error de Red", "Laptop inalcanzable."),
                method='POST', timeout=30
            )
        def pide_confirmacion():
            pedir_confirmacion("Va a generar un nuevo congelado, ¿está seguro S/N?", correr_proceso, lambda: None)
        solicitar_password(pide_confirmacion, lambda: None)
    def exportar_diferencias(self):
        UrlRequest(
            f"{URL_SERVER}/exportar_diferencias",
            on_success=lambda r, res: popup_mensaje("Éxito", res.get("mensaje")),
            on_failure=lambda r, e: popup_mensaje("Error", "Fallo al exportar excel en Laptop."),
            on_error=lambda r, e: popup_mensaje("Error de Red", "Laptop inalcanzable."),
            method='POST', timeout=15
        )
class ConteoScreen(Screen):
    paso = NumericProperty(1)
    estado = StringProperty("")
    datos = {}
    def mensaje_paso(self):
        return {1: "Escanear Sloc", 2: "Escanear Ubicación", 3: "Escanear Material", 4: "Escanear Número de Serie"}.get(self.paso, "")
    def set_paso(self, p):
        self.paso = p
        self.estado = ""
        self.ids.txt.text = ""
        self.ids.lbl.text = self.mensaje_paso()
        if p == 1:
            for campo in ['Ubicacion', 'Material', 'MaterialDescription', 'SerialNumber']:
                self.datos.pop(campo, None)
        elif p == 2:
            for campo in ['Material', 'MaterialDescription', 'SerialNumber']:
                self.datos.pop(campo, None)
        self.mostrar_avance()
    def mostrar_avance(self):
        self.ids.lbl_avance.text = (
            f"Sloc: {self.datos.get('StorageLocation', '')}\n"
            f"Ubicación: {self.datos.get('Ubicacion', '')}\n"
            f"Material: {self.datos.get('Material', '')}\n"
            f"Serie: {self.datos.get('SerialNumber', '')}"
        )
    def procesar(self):
        valor = self.ids.txt.text.strip()
        if not valor:
            return
        if self.paso == 1:
            UrlRequest(
                f"{URL_SERVER}/validar/sloc", req_body=json.dumps({"valor": valor}), req_headers=HEADERS_JSON,
                on_success=lambda r, res: self.guardar_y_seguir('StorageLocation', valor, 2) if res.get("existe") else pedir_confirmacion("StorageLocation NO existe, ¿agregar?", lambda: self.guardar_y_seguir('StorageLocation', valor, 2), lambda: self.set_paso(1)),
                on_error=lambda r, e: setattr(self, 'estado', "Sin conexión con la laptop."), method='POST'
            )
        elif self.paso == 2:
            UrlRequest(
                f"{URL_SERVER}/validar/ubicacion", req_body=json.dumps({"valor": valor}), req_headers=HEADERS_JSON,
                on_success=lambda r, res: self.guardar_y_seguir('Ubicacion', valor, 3) if res.get("existe") else pedir_confirmacion("Ubicación NO existe, ¿agregar?", lambda: self.guardar_y_seguir('Ubicacion', valor, 3), lambda: self.set_paso(2)),
                on_error=lambda r, e: setattr(self, 'estado', "Sin conexión con la laptop."), method='POST'
            )
        elif self.paso == 3:
            UrlRequest(
                f"{URL_SERVER}/buscar_material", req_body=json.dumps({"material": valor}), req_headers=HEADERS_JSON,
                on_success=self.resultado_material,
                on_error=lambda r, e: setattr(self, 'estado', "Sin conexión con la laptop."), method='POST'
            )
        elif self.paso == 4:
            self.datos['SerialNumber'] = valor
            self.mostrar_avance()
            self.registrar_lectura_api(1)
    def resultado_material(self, req, res):
        valor = self.ids.txt.text.strip()
        if not res.get("encontrado"):
            pedir_confirmacion("Material no existe en Congelado, ¿agregar?", lambda: self.material_nuevo(valor), lambda: self.set_paso(3))
        else:
            mat_info = res.get("info")
            self.datos['Material'] = valor
            self.datos['MaterialDescription'] = mat_info['MaterialDescription']
            self.mostrar_avance()
            if mat_info['SerialNumber'] == "Sin Serie":
                self.solicitar_unidades()
            else:
                self.paso = 4
                self.ids.lbl.text = self.mensaje_paso()
                self.ids.txt.text = ""
                self.mostrar_avance()
    def guardar_y_seguir(self, campo, valor, siguiente):
        self.datos[campo] = valor.upper()
        self.set_paso(siguiente)
    def material_nuevo(self, mat):
        self.datos['Material'] = mat
        self.datos['MaterialDescription'] = ""
        self.mostrar_avance()
        self.solicitar_unidades()
    def solicitar_unidades(self):
        def aceptar():
            try:
                cant = int(txt.text)
            except:
                cant = 1
            self.datos['SerialNumber'] = "Sin Serie"
            self.mostrar_avance()
            self.registrar_lectura_api(cant)
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text="Ingrese Unidades:"))
        txt = TextInput(multiline=False, input_filter="int")
        box.add_widget(txt)
        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_ok = Button(text="Aceptar")
        btn_cancel = Button(text="Cancelar")
        btns.add_widget(btn_ok)
        btns.add_widget(btn_cancel)
        box.add_widget(btns)
        popup = Popup(title="Unidades", content=box, size_hint=(.7, .3), auto_dismiss=False)
        btn_ok.bind(on_press=lambda x: (popup.dismiss(), aceptar()))
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()
    def registrar_lectura_api(self, fisico, forzar=False):
        payload = {
            "StorageLocation": self.datos.get('StorageLocation', ''),
            "Ubicacion": self.datos.get('Ubicacion', ''),
            "Material": self.datos.get('Material', ''),
            "SerialNumber": self.datos.get('SerialNumber', ''),
            "MaterialDescription": self.datos.get('MaterialDescription', ''),
            "Fisico": fisico,
            "forzar_reemplazo": forzar
        }
        def respuesta_registro(req, res):
            if res.get("status") == "duplicado":
                pedir_confirmacion(res.get("mensaje"), lambda: self.registrar_lectura_api(fisico, forzar=True), lambda: self.set_paso(3))
            else:
                self.estado = "Lectura registrada."
                self.ids.estado.text = self.estado
                self.ids.estado.color = (0, 0.6, 0, 1)
                self.ids.txt.text = ""
                self.set_paso(3)
        UrlRequest(
            f"{URL_SERVER}/registrar_lectura", req_body=json.dumps(payload), req_headers=HEADERS_JSON,
            on_success=respuesta_registro, on_error=lambda r, e: setattr(self, 'estado', "Error al sincronizar con laptop."), method='POST'
        )
class LecturasScreen(Screen):
    def actualizar(self):
        box = self.ids.lecturas
        box.clear_widgets()
        filtro = self.ids.filtro.text.strip().lower()
        encabezado = BoxLayout(size_hint_y=None, height=32, spacing=6)
        encabezado.add_widget(Label(text="Sloc", font_size='12sp', size_hint_x=0.13))
        encabezado.add_widget(Label(text="Ubicación", font_size='12sp', size_hint_x=0.18))
        encabezado.add_widget(Label(text="Material", font_size='12sp', size_hint_x=0.18))
        encabezado.add_widget(Label(text="Serie", font_size='12sp', size_hint_x=0.18))
        encabezado.add_widget(Label(text="Cantidad", font_size='12sp', size_hint_x=0.12))
        encabezado.add_widget(Label(text="Acciones", font_size='12sp', size_hint_x=0.21))
        box.add_widget(encabezado)
        def pintar_filas(req, registros):
            registros.sort(key=lambda x: (str(x['sloc']), str(x['ubicacion']), str(x['material']), str(x['serial'])))
            for row in registros:
                if filtro and filtro not in f"{row['sloc']}|{row['ubicacion']}|{row['material']}|{row['serial']}".lower():
                    continue
                lay = BoxLayout(size_hint_y=None, height=32, spacing=4)
                lay.add_widget(Label(text=str(row['sloc']), font_size='11sp', size_hint_x=0.13))
                lay.add_widget(Label(text=str(row['ubicacion']), font_size='11sp', size_hint_x=0.18))
                lay.add_widget(Label(text=str(row['material']), font_size='11sp', size_hint_x=0.18))
                lay.add_widget(Label(text=str(row['serial']), font_size='11sp', size_hint_x=0.18))
                lay.add_widget(Label(text=str(row['fisico']), font_size='11sp', size_hint_x=0.12))
                acciones = BoxLayout(orientation='horizontal', size_hint_x=0.21, spacing=4)
                btn_edit = Button(text="Edit", size_hint=(None, None), size=(40, 28), font_size='10sp', background_color=(0,0,1,1), background_normal='')
                btn_edit.bind(on_press=lambda inst, r=row: self.editar(r))
                btn_del = Button(text="Borrar", size_hint=(None, None), size=(40, 28), font_size='10sp', background_color=(1,0,0,1), background_normal='')
                btn_del.bind(on_press=lambda inst, idx=row['idx']: self.eliminar(idx))
                acciones.add_widget(btn_edit)
                acciones.add_widget(btn_del)
                lay.add_widget(acciones)
                box.add_widget(lay)
        UrlRequest(f"{URL_SERVER}/obtener_lecturas", on_success=pintar_filas, on_error=lambda r, e: box.add_widget(Label(text="Error de conexión.")))
    def eliminar(self, idx):
        UrlRequest(f"{URL_SERVER}/eliminar_lectura", req_body=json.dumps({"idx": idx}), req_headers=HEADERS_JSON, on_success=lambda r, res: self.actualizar(), method='POST')
    def editar(self, registro):
        content = BoxLayout(orientation='vertical', spacing=8, padding=8)
        content.add_widget(Label(text=f"Sloc: {registro['sloc']} | Ubicación: {registro['ubicacion']}"))
        content.add_widget(Label(text=f"Material: {registro['material']}"))
        content.add_widget(Label(text="Modificar unidades:"))
        txt_cantidad = TextInput(text=str(registro['fisico']), multiline=False, input_filter='int')
        content.add_widget(txt_cantidad)
        btn_guardar = Button(text="Guardar", height=36)
        btn_cancelar = Button(text="Cancelar", height=36)
        btn_layout = BoxLayout(size_hint_y=None, height=36, spacing=8)
        btn_layout.add_widget(btn_guardar)
        btn_layout.add_widget(btn_cancelar)
        content.add_widget(btn_layout)
        popup = Popup(title="Editar unidades", content=content, size_hint=(0.7, 0.5))
        def guardar_edicion(inst):
            UrlRequest(
                f"{URL_SERVER}/editar_lectura", req_body=json.dumps({"idx": registro['idx'], "cantidad": int(txt_cantidad.text)}), req_headers=HEADERS_JSON,
                on_success=lambda r, res: (popup.dismiss(), self.actualizar()), method='POST'
            )
        btn_guardar.bind(on_press=guardar_edicion)
        btn_cancelar.bind(on_press=lambda inst: popup.dismiss())
        popup.open()
class VariacionesScreen(Screen):
    def actualizar(self):
        box = self.ids.variaciones
        box.clear_widgets()
        box.add_widget(Label(text=" Sloc | Ubicacion | Material | Serie | Cong | Fis | Dif", bold=True, color=(.8, .35, .05, 1), size_hint_y=None, height=28, font_size='12sp'))
        def cargar_tabla(req, res):
            if res.get("status") == "ok":
                for v in res.get("variaciones", []):
                    texto = f"{v['sloc']} | {v['ubicacion']} | {v['material']} | {v['serial']} | {v['congelado']} | {v['fisico']} | {v['dif']}"
                    box.add_widget(Label(text=texto, size_hint_y=None, height=24, font_size='11sp'))
            else:
                box.add_widget(Label(text=res.get("mensaje", "Error")))
        UrlRequest(f"{URL_SERVER}/exportar_diferencias", on_success=cargar_tabla, on_error=lambda r, e: box.add_widget(Label(text="Sin conexión con laptop.")), method='POST')
class GeodisApp(App):
    def build(self):
        Window.size = (390, 700)
        return Builder.load_string(KV)
if __name__ == "__main__":
    GeodisApp().run()
