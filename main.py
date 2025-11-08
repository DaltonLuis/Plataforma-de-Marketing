import os
from src.utils.seed import initialize_tables
from shared.security import init_db, get_session, engine
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.routers import user, address, category, email, productReview, sellerReview, auth, comment
from sqlmodel import Session, select, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
         self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

description = """
*   A plataforma de marketing para empreendedores utilizada neste exemplo é a **ProcuraAqui**.
"""

app = FastAPI(title="API para plataforma de marketing para empreendedores",
              description=description,
              summary="Esta é uma API que só deve ser utilizada com a permissão do proprietário.",
              contact={
                  "name": "Dalton Luís",
                  "email": "luisinho2dbl@gmail.com",
              },)


if not os.path.exists("buyer_images"):
    os.makedirs("buyer_images")
if not os.path.exists("seller_images"):
    os.makedirs("seller_images")
if not os.path.exists("admin_images"):
    os.makedirs("admin_images")

app.mount("/seller_images", StaticFiles(directory="seller_images"), name="seller_images")
app.mount("/buyer_images", StaticFiles(directory="buyer_images"), name="buyer_images")
app.mount("/admin_images", StaticFiles(directory="admin_images"), name="admin_images")
app.mount("/static", StaticFiles(directory="static"), name="static")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event("startup")
async def on_startup():
    try:
        logger.info("Inicializando banco de dados...")
        init_db()

        db = next(get_session())
        initialize_tables(db)

        logger.info("Aplicação iniciada com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar aplicação: {e}")

@app.get('/health', tags=["Health"], response_class=JSONResponse)
async def health_check(db: Session = Depends(get_session)):
    try:
        db.exec(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "service": "ProcuraAqui API"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

@app.get('/', tags=["Default"], response_class=FileResponse)
async def get_home():
    return FileResponse('static/index.html')

@app.get('/chat', tags=["Default"], response_class=FileResponse)
async def get_chat():
    return FileResponse('static/chat.html')

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} has left the chat")


app.include_router(address.router, tags=["Address"])
app.include_router(user.router, tags=["User"])
app.include_router(sellerReview.router, tags=["Seller Review"])
app.include_router(category.router, tags=["Category"])
app.include_router(productReview.router, tags=["Product Review"])
app.include_router(email.router, tags=["Email"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(comment.router, tags=["Comment"])

if __name__ == '__main__':
    uvicorn.run('main:app', port=5000, reload=True, host='localhost')
