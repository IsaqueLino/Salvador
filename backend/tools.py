import re

from sqlalchemy import text
from backend.Principal import get_engine_for_db
from langchain.tools import BaseTool
from langchain_core.tools import ToolException
from pydantic import BaseModel, Field
from datetime import datetime


class ArgsConsultDatabase(BaseModel):
    tool_input: str = Field(..., description=r"Query to be executed on the database. **IMPORTANTE** não use o \\ e use aspas simples(')")


class ConsultDatabaseTool(BaseTool):
    name: str = "ConsultDatabase"  # Adicionada a anotação de tipo
    description: str = r"Consulta o banco de dados, permitindo apenas operações de leitura."

    def _run(self, tool_input: str):
        db = next(get_engine_for_db())
        try:
            query_str = tool_input

            # Lista de comandos proibidos
            forbidden_commands = [
                "DELETE", "ALTER", "CREATE", "DROP", "UPDATE", "INSERT", "TRUNCATE", "REPLACE",
            ]

            # Verificar se a consulta contém algum comando proibido
            if any(command in query_str.upper() for command in forbidden_commands):
                return {"error": "Apenas operações de leitura são permitidas."}

            result = db.execute(text(query_str))

            if result.returns_rows:
                rows = result.fetchall()
                result_str = "\n".join(str(row) for row in rows)
                return result_str

            return {"rows_affected": result.rowcount}

        except Exception as e:
            return {"error": str(e)}

        finally:
            db.close()


class ArgsShowTables(BaseModel):
    tool_input: str


class ShowTablesTool(BaseTool):
    name: str = "ShowTables"  # Adicionada a anotação de tipo
    description: str = "Exibe todas as tabelas do banco de dados."

    def _run(self, tool_input: str):
        db = next(get_engine_for_db())
        try:
            result = db.execute(text("SHOW TABLES;"))

            if result.returns_rows:
                rows = result.fetchall()
                result_str = "\n".join(str(row) for row in rows)
                return result_str

            return {"rows_affected": result.rowcount}

        except Exception as e:
            try:
                result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))

                if result.returns_rows:
                    rows = result.fetchall()
                    result_str = "\n".join(str(row) for row in rows)
                    return result_str

                return {"rows_affected": result.rowcount}

            except Exception as e:
                return {"error": str(e)}

        finally:
            db.close()


class ArgsDeleteDatabase(BaseModel):
    tool_input: str = Field(..., description="O comando DELETE do SQL a ser executado.")


class DeleteDatabaseTool(BaseTool):
    name: str = "delete_database"  # Adicionada a anotação de tipo
    description: str = "Executa uma query SQL do tipo delete no banco de dados."

    def _run(self, query: str):
        db = next(get_engine_for_db())
        try:
            query_segura = re.sub(r"\\'", "'", query)
            result = db.execute(text(query_segura))
            db.commit()

            if result.returns_rows:
                rows = result.fetchall()
                result_str = "\n".join(str(row) for row in rows)
                return result_str

            return {"rows_affected": result.rowcount}

        except Exception as e:
            return {"error": str(e)}

        finally:
            db.close()


class ArgsUpdateDatabase(BaseModel):
    tool_input: str = Field(..., description="O comando UPDATE do SQL a ser executado. use APENAS LIKE")


class UpdateDatabaseTool(BaseTool):
    name: str = "update_database"  # Adicionada a anotação de tipo
    description: str = "Executa uma query SQL do tipo update no banco de dados."

    def _run(self, query: str):
        db = next(get_engine_for_db())
        try:
            query_segura = re.sub(r"\\'", "'", query)
            result = db.execute(text(query_segura))
            db.commit()

            if result.returns_rows:
                rows = result.fetchall()
                result_str = "\n".join(str(row) for row in rows)
                return result_str

            return {"rows_affected": result.rowcount}

        except Exception as e:
            return {"error": str(e)}

        finally:
            db.close()


class ArgsInsertDatabase(BaseModel):
    tool_input: str = Field(..., description="O comando INSERT do SQL a ser executado.")


class InsertDatabaseTool(BaseTool):
    name: str = "insert_database"  # Adicionada a anotação de tipo
    description: str = "Executa uma query SQL do tipo insert no banco de dados."

    def _run(self, query: str):
        db = next(get_engine_for_db())
        try:
            query_segura = re.sub(r"\\'", "'", query)
            result = db.execute(text(query_segura))
            db.commit()

            if result.returns_rows:
                rows = result.fetchall()
                result_str = "\n".join(str(row) for row in rows)
                return result_str

            return {"rows_affected": result.rowcount}

        except Exception as e:
            return {"error": str(e)}

        finally:
            db.close()
