from databases.postgres import database

FACE_DB = {}  # student_id -> img_path

async def load_faces():
    global FACE_DB
    FACE_DB = {}
    async with database.pool.acquire() as conn:
        rows = await conn.fetch("""
            select student_id, img_path
            from Faces
        """)
    for r in rows:
        FACE_DB[r["student_id"]] = r["img_path"]
