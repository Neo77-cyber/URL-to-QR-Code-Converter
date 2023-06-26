from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse, JSONResponse, FileResponse
from urllib.parse import quote
import qrcode
from io import BytesIO
from tempfile import NamedTemporaryFile
import os

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.get("/qrcode/{url}")
async def generate_qrcode(url: str):
    try:
        if url[0] == '/':
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        encoded_url = quote(url, safe='')
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(encoded_url)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        image_stream = BytesIO()
        qr_image.save(image_stream)
        image_stream.seek(0)
        
        return StreamingResponse(image_stream, media_type="image/png")
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    


@app.get("/downloadqrcode/{url}")
async def download_qrcode(url: str):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    with NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file_path = temp_file.name
        qr_image.save(temp_file_path)
        temp_file.seek(0)

    try:
        if os.path.exists(temp_file_path):
            return FileResponse(temp_file_path, filename="qrcode.png", media_type="image/png")
        else:
            raise HTTPException(status_code=404, detail="QR code file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

