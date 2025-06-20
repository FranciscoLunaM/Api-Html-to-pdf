
import socket
from fastapi.middleware.cors import CORSMiddleware
import consul
from fastapi import FastAPI
from routes.pdf.pdf_router import pdf_router
from dotenv import load_dotenv
import os

#log errores
import logging
logger = logging.getLogger('weasyprint')
logger.addHandler(logging.StreamHandler())

load_dotenv()
consul_host = os.getenv("CONSUL_HOST")
consul_port = os.getenv("CONSUL_PORT")



s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_address =s.getsockname()[0]
port=s.getsockname()[1]
s.close()


#consul
"""c = consul.Consul(host=consul_host, port=consul_port)

c.agent.service.register('servicios-plantillas-tabasco',
                        service_id='servicios-plantillas-tabasco',
                        port=2021,
                        address=ip_address,
                        tags=['servicios-plantillas-tabasco'])"""
#-----------------------------

app = FastAPI()
app.include_router(pdf_router, prefix="/pdf", tags=["pdf"])


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
