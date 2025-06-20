from pydantic import BaseModel

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
    foto: str

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
