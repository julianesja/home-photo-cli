from fastapi import  FastAPI, UploadFile, File
from app.application.use_cases.call_process_photo import CallProcessPhoto

def api_main():
    app = FastAPI()

    @app.post("/upload")
    async def subir_archivo(archivo: UploadFile = File(...)):
        call_process_photo = CallProcessPhoto()
        contenido = await archivo.read()  # Leer contenido del archivo
    
        result, photo, error = call_process_photo.process_photo(contenido)
        if (result):
            return {
                "photo": photo
            }
        else:
            return {
                "error": error
            }
    
    @app.get("/ping")
    def ping():
        return "pong"
    return app

        

        