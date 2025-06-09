import base64
import locale
import socket
from weasyprint import HTML as WeasyHTML, CSS
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from io import BytesIO
import consul
from fastapi.middleware.cors import CORSMiddleware
import qrcode
import hashlib
from datetime import datetime
from fastapi.exceptions import RequestValidationError

#servicios-plantillas-tabasco


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_address =s.getsockname()[0]
port=s.getsockname()[1]
s.close()



#consul

#-----------------------------

app = FastAPI()


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    html: str
    css: str | None = None

class HtmlContent(BaseModel):  
    header: str
    body: str
    footer: str
    css: str

class Ciudadano(BaseModel):
    nombre: str
    curp: str

class Titular(BaseModel):
    nombre:str
    cargo:str

class UnidadDireccion(BaseModel):
    unidad_administrativa: str
    unidad_telefono:str | None = None
    unidad_sitio_web:str | None = None
    unidad_direccion:str 
    
class BodyForHtmlToPdf(BaseModel):
    unidad_administrativa: str
    ente: str 
    logo: str
    html: HtmlContent
    direccion: str
    cadena_hash: str | None = None
    sello: str | None = None
    qr:str
    asunto: str 
    oficio:str 
    ciudadanos: Ciudadano

class BodyForHtmlToPdf2(BaseModel):
    ente: str 
    logo: str
    html: HtmlContent
    unidad: UnidadDireccion
    cadena_hash: str | None = None
    sello: str | None = None
    qr:str
    asunto: str 
    oficio:str 
    ciudadanos: Ciudadano
    fecha:str 
    ciudad:str
    titular:Titular

class MessageError(BaseModel):
    detail: str

class Response(BaseModel):
    pdf_base64: str
    hash:str | None = None

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    raise HTTPException(status_code=400, detail=f"error en el json enviado:{exc.errors()}")

@app.get("/test")
async def root():
    return {"message": "Hello World"}


@app.post("/pdf/base64")
async def version2(body: BodyForHtmlToPdf2)->Response: 
        try:
            img = qrcode.make(body.qr)
            image = BytesIO()
            img.save(image, format='PNG')
            image.seek(0)
            img_base64 = base64.b64encode(image.read()).decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al generar el codigo qr: {str(e)}")
            #--------------------------

            #generando el pdf
        try:    
            data = {
                "unidad_administrativa": body.unidad.unidad_administrativa,
                "ente": body.ente,
                "logo": body.logo,
                "unidad_telefono": body.unidad.unidad_telefono,
                "unidad_sitio_web": body.unidad.unidad_sitio_web,
                "unidad_direccion": body.unidad.unidad_direccion,
                "cadena_hash": body.cadena_hash if body.cadena_hash else "",
                "sello": body.sello if body.sello else "",
                "nombre": body.ciudadanos.nombre,
                "curp": body.ciudadanos.curp,
                "qr": img_base64 if img_base64 else "",
                "asunto":body.asunto,
                "oficio":body.oficio,
                "fecha": DateFormat(body.fecha) ,
                "ciudad": body.ciudad,
                "titular_nombre": body.titular.nombre,
                "titular_cargo": body.titular.cargo
            }

            if body.cadena_hash =="":
                body.html.body = body.html.body.replace("Cadena Original:", "")
            if body.sello=="":
                body.html.body = body.html.body.replace("Firma:", "")
            
            html_content = f'<!DOCTYPE html><html lang="es"><header>{body.html.header}</header><body> {body.html.body}  </body><footer>{body.html.footer}</footer></html>'
            htmlFormatted = html_content.format(**data)
            pdf_io = BytesIO()
            WeasyHTML(string=htmlFormatted).write_pdf(
                pdf_io,
                stylesheets=[CSS(string=body.html.css)] if body.html.css else None
            )
            pdf_io.seek(0)
            
            pdf_bytes = pdf_io.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

            # Generar el hash del PDF
            hash_bytes=convert_to_hash(pdf_base64)
            

            response= Response(pdf_base64=pdf_base64, hash=base64.b64encode(hash_bytes).decode('utf-8') if hash_bytes else None)
            
            return response
        except Exception as e:
                    str(e)
                    raise HTTPException(status_code=400, detail=f"Error al generar el html, posiblemente con una variable: {str(e)}")

@app.post("pdf/tofile" )
async def version2_1(body: BodyForHtmlToPdf2) -> Response :
    #convirtiendo el qr en base 64
        try:
            img = qrcode.make(body.qr)
            image = BytesIO()
            img.save(image, format='PNG')
            image.seek(0)
            img_base64 = base64.b64encode(image.read()).decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al generar el codigo qr: {str(e)}")
            #--------------------------

            #generando el pdf
        try:    
            data = {
                "unidad_administrativa": body.unidad.unidad_administrativa,
                "ente": body.ente,
                "logo": body.logo,
                "unidad_telefono": body.unidad.unidad_telefono,
                "unidad_sitio_web": body.unidad.unidad_sitio_web,
                "unidad_direccion": body.unidad.unidad_direccion,
                "cadena_hash": body.cadena_hash if body.cadena_hash else "",
                "sello": body.sello if body.sello else "",
                "nombre": body.ciudadanos.nombre,
                "curp": body.ciudadanos.curp,
                "qr": img_base64 if img_base64 else "",
                "asunto":body.asunto,
                "oficio":body.oficio,
                "fecha": DateFormat(body.fecha) ,
                "ciudad": body.ciudad,
                "titular_nombre": body.titular.nombre,
                "titular_cargo": body.titular.cargo
            }

        
            if body.cadena_hash =="":
                body.html.body = body.html.body.replace("Cadena Original:", "")
            if body.sello=="":
                body.html.body = body.html.body.replace("Firma:", "")
            
            html_content = f'<!DOCTYPE html><html lang="es"><header>{body.html.header}</header><body> {body.html.body}  </body><footer>{body.html.footer}</footer></html>'
            htmlFormatted = html_content.format(**data)
            pdf_io = BytesIO()
            WeasyHTML(string=htmlFormatted).write_pdf(
                pdf_io,
                stylesheets=[CSS(string=body.html.css)] if body.html.css else None
            )
            pdf_io.seek(0)
            #return para visualizar el pdf en el navegador
            
            return StreamingResponse(pdf_io, media_type="application/pdf", headers={
                "Content-Disposition": "inline; filename=output.pdf"
            })
        except Exception as e:
            str(e)
            raise HTTPException(status_code=400, detail=f"Error al generar el html, posiblemente con una variable: {str(e)}")
       


def DateFormat(date_str: str) -> str:
    try:

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        #print(date_obj.strftime("dia %d del mes de %B del año %Y"))
        return date_obj.strftime("dia %d del mes de %B del año %Y")
    except ValueError:
        print(f"Error parsing date: {date_str}")
        return date_str  

    
def convert_to_hash(data: str) -> str:
    try:
      decoded_data = base64.b64decode(data)
    except Exception as e:
        print(f"Error decoding base64 string:")
        return None

    hash_object = hashlib.sha256()
    hash_object.update(decoded_data)
    return hash_object.digest()
