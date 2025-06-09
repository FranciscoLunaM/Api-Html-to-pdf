FROM 3.13.3-slim-bullseye
WORKDIR /api
COPY ./api ./api
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev 
    

RUN apt-get update && \
    apt-get install -y gcc libpq-dev \
    libpango-1.0-0 libpangoft2-1.0-0 gir1.2-harfbuzz-0.0 && \
    apt clean && \
    rm -rf /var/cache/apt/*
    
RUN apt-get update && apt-get install -y locales-all


ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
RUN pip install py-consul
RUN pip install weasyprint
RUN pip install qrcode
RUN pip install fastapi[standard]
CMD ["fastapi", "run", "app/main.py", "--port", "9012"]



