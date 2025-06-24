from io import BytesIO
import qrcode
import hashlib
from datetime import datetime
from fastapi.exceptions import RequestValidationError
import os
from fastapi.responses import StreamingResponse
import base64
import locale
from fastapi import APIRouter, HTTPException
from routes.pdf.pdf_models import *
from weasyprint.text.fonts import FontConfiguration
from weasyprint import HTML, CSS

font_config = FontConfiguration()

pdf_router= APIRouter()

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

@pdf_router.get("/test")
async def root():
    return {"message": "Hello World"}


@pdf_router.post("/base64")
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
                "cadena_hash": body.cadena_hash.replace("/", "&#8288;/&#8288;") if body.cadena_hash else "",
                "sello": body.sello.replace("/", "&#8288;/&#8288;")  if body.sello else "",
                "nombre": body.ciudadanos.nombre,
                "curp": body.ciudadanos.curp,
                "qr": img_base64 if img_base64 else "",
                "asunto":body.asunto,
                "oficio":body.oficio,
                "fecha": DateFormat(body.fecha) ,
                "ciudad": body.ciudad,
                "titular_nombre": body.titular.nombre,
                "titular_cargo": body.titular.cargo,
                "foto": body.ciudadanos.foto,
            }

            if body.cadena_hash =="":
                body.html.body = body.html.body.replace("Cadena Original:", "")
            if body.sello=="":
                body.html.body = body.html.body.replace("Firma:", "")

             
            html_content = f'<!DOCTYPE html><html lang="es"><header>{body.html.header}</header><body> <footer>{body.html.footer}</footer> {body.html.body}</body></html>'
            htmlFormatted = html_content.format(**data)
            pdf_io = BytesIO()
            
            html=HTML(string=htmlFormatted, base_url='api')
            css = CSS(string=body.html.css,font_config=font_config)
            html.write_pdf(
            pdf_io, stylesheets=[css],
            font_config=font_config)
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

@pdf_router.post("/" )
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
                "cadena_hash": body.cadena_hash.replace("/", "&#8288;/&#8288;") if body.cadena_hash else "",
                "sello": body.sello.replace("/", "&#8288;/&#8288;") if body.sello else "",
                "nombre": body.ciudadanos.nombre,
                "curp": body.ciudadanos.curp,
                "qr": img_base64 if img_base64 else "",
                "asunto":body.asunto,
                "oficio":body.oficio,
                "fecha": DateFormat(body.fecha) ,
                "ciudad": body.ciudad,
                "titular_nombre": body.titular.nombre,
                "titular_cargo": body.titular.cargo,
                "foto": body.ciudadanos.foto,
            }

        
            if body.cadena_hash =="":
                body.html.body = body.html.body.replace("Cadena Original:", "")
            if body.sello=="":
                body.html.body = body.html.body.replace("Firma:", "")

            

            html_content = f'<!DOCTYPE html><html lang="es"><header>{body.html.header}</header><body> <footer>{body.html.footer}</footer> {body.html.body}</body></html>'
            htmlFormatted = html_content.format(**data)
            pdf_io = BytesIO()
            html=HTML(string=htmlFormatted, base_url='api')
            css = CSS(string=body.html.css,font_config=font_config)
            html.write_pdf(
            pdf_io, stylesheets=[css],
            font_config=font_config)
            pdf_io.seek(0)
            #return para visualizar el pdf en el navegador
            
            return StreamingResponse(pdf_io, media_type="pdf_routerlication/pdf", headers={
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
