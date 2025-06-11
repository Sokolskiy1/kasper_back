import sys
from typing import Optional
from urllib.parse import unquote
from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from urllib.parse import quote_plus
import logging
from fastapi.responses import JSONResponse
from fastapi import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

username = "postgres"
password = "123"
db_name = "kaspersky_db"

encoded_password = quote_plus(password) if any(c in password for c in ['@', ':', '/']) else password

DATABASE_URL = f"postgresql://{username}:{encoded_password}@localhost:5432/{db_name}"

engine = create_engine(DATABASE_URL)
try:
    conn = engine.connect()
    conn.close()
    print("✅ DB connection successful")
except Exception as e:
    print(f"❌ DB connection failed: {e}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/gg")
def read_items(request: Request,db: Session = Depends(get_db),sort: Optional[str] = None,search: str = None):
    query_params = request.query_params

    page = int(query_params.get("page"))
    items_per_page = 1000



    start_row = (page-1) * items_per_page
    finish_row =  items_per_page



    columns = ['id', 'name', 'count', '"desc"','parent','country','version',]  # ваш массив
    sql_query = f"""
    SELECT 
        {', '.join(columns)}, 
        to_char(created_at, 'YYYY-MM-DD"T"HH24:MI:SS') as created_at 
    FROM 
        kaspersky_list
    """
    params = {'limit': finish_row, 'offset': start_row}

    if search:
        search = unquote(search)
        sql_query += " WHERE "  # Ключевое добавление!
        if len(search) == 1:
            sql_query += """
                (name ILIKE :search_term || '%' OR
                'desc' ILIKE :search_term || '%' OR
                count::TEXT ILIKE :search_term || '%')
            """
            params['search_term'] = search.replace(' ', ' & ')
        else:
            sql_query += "search_vector @@ to_tsquery('russian', :search_term)"
            params['search_term'] = f"{search}:*"

    else:
        params = {'limit': finish_row, 'offset': start_row}
    if sort:
        sort_fields = sort.split(',')
        order_clauses = []

        for field in sort_fields:
            field_parts = field.split(':')
            if len(field_parts) == 2:
                column, order = field_parts
                if order == 'ascend':
                    order = 'ASC'
                elif order == 'descend':
                    order = 'DESC'
                else:
                    continue
                order_clauses.append(f"{column} {order}")

        if order_clauses:
            order_clauses = [f"`{col.strip()}`" if col.strip().lower() == 'desc' else col for col in order_clauses]
            sql_query += " ORDER BY " + ", ".join(order_clauses)
    else:
            sql_query += " ORDER BY id ASC"

    sql_query += " LIMIT :limit OFFSET :offset"

    result = db.execute(
        text(sql_query),
        params
    )

    count_table_elements  =  db.execute(text("""SELECT COUNT(*) FROM kaspersky_list""")).scalar()

    items = [dict(row) for row in result.mappings()]
    columns = list(result.keys())
    mass_columns = [{"title":column,"dataIndex":column,"key":column,"sorter":"true", "filterSearch": "true","sorter":{"multiple": 3,}} for column in columns]

    return JSONResponse(
        content={
            "status": "success",
            "data": items,
            # "kkkk": mass_columns,
            "columns": mass_columns,
            "count": count_table_elements,
            "count_table_elements":count_table_elements
        },
        status_code=200
    )


@router.get("/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    # Безопасный запрос с параметрами
    item = db.execute(
        text("SELECT * FROM items WHERE id = :item_id"),
        {"item_id": item_id}
    ).fetchone()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": dict(item)}