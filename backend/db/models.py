from sqlalchemy import Column, Integer, String, Text, event
from sqlalchemy.schema import DDL
from pgvector.sqlalchemy import Vector
from db.session import Base, engine


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id          = Column(Integer, primary_key=True, index=True)
    source      = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content     = Column(Text, nullable=False)
    embedding   = Column(Vector(384), nullable=False)


# Kreira pgvector ekstenziju u PostgreSQL ako ne postoji
event.listen(
    DocumentChunk.__table__,
    "before_create",
    DDL("CREATE EXTENSION IF NOT EXISTS vector")
)