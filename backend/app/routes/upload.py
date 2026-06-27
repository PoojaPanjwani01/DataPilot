from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.file_validator import file_validator
from backend.app.services.dataset_service import dataset_service
from backend.app.services.schema_service import schema_service
from backend.app.utils.logger import logger
from backend.app.utils.rate_limiter import rate_limit_query, rate_limit_upload
from backend.app.models.request import InsightsRequest
from backend.app.models.response import InsightsResponse

router = APIRouter()


@router.post("/upload/preview", dependencies=[Depends(rate_limit_upload)])
async def preview_file_upload(file: UploadFile = File(...)):
    """Validates the uploaded file structures and returns details before database import."""
    logger.info(f"Received preview request for: {file.filename}")

    # 1. Read byte contents
    content = await file.read()
    filename = file.filename

    # 2. Run validations
    try:
        file_validator.validate_file_metadata(filename, len(content))
        df = file_validator.parse_and_validate_structure(content, filename)
    except ValueError as e:
        logger.warning(f"File validation failure: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal file processing failure: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process file structure: {str(e)}"
        )

    # 3. Form preview response structure without writing to the database
    base_table_name = dataset_service.sanitize_table_name(filename)
    table_name = dataset_service.get_unique_table_name(base_table_name)
    summary = dataset_service.get_dataset_summary(table_name, df)

    return summary


@router.post("/upload/import", dependencies=[Depends(rate_limit_upload)])
async def upload_and_import_dataset(file: UploadFile = File(...)):
    """Imports the uploaded CSV/XLSX file, creates a table in PostgreSQL, and clears schema cache."""
    logger.info(f"Received import request for: {file.filename}")

    # 1. Read byte contents
    content = await file.read()
    filename = file.filename

    # 2. Run validations
    try:
        file_validator.validate_file_metadata(filename, len(content))
        df = file_validator.parse_and_validate_structure(content, filename)
    except ValueError as e:
        logger.warning(f"File validation failure: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal file processing failure: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process file structure: {str(e)}"
        )

    # 3. Create table, write rows, grant read permissions
    try:
        summary = dataset_service.import_dataset(df, filename)

        # 4. Clear the schema service cache to force Gemini to see the new tables
        schema_service.clear_cache()
        return summary
    except Exception as e:
        logger.error(f"Failed to import dataset into DB: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to import dataset: {str(e)}"
        )


@router.get("/datasets")
def list_uploaded_datasets(db: Session = Depends(get_db)):
    """Lists all dynamically imported datasets currently available."""
    try:
        return dataset_service.list_datasets(db)
    except Exception as e:
        logger.error(f"Failed to retrieve dataset listing: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Database retrieval failure: {str(e)}"
        )


@router.get("/datasets/{dataset_name}/preview")
def get_dataset_preview(dataset_name: str, db: Session = Depends(get_db)):
    """Gets preview metadata of a specific uploaded dataset."""
    try:
        return dataset_service.get_single_dataset_preview(db, dataset_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get preview for '{dataset_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/datasets/{dataset_name}")
def delete_uploaded_dataset(dataset_name: str):
    """Deletes an uploaded dataset, drops its table, and clears schema cache."""
    if not dataset_name.startswith("uploaded_"):
        raise HTTPException(
            status_code=400,
            detail="Only uploaded datasets starting with 'uploaded_' can be deleted.",
        )

    try:
        dataset_service.delete_dataset(dataset_name)
        # Clear schema cache to remove deleted table from LLM context
        schema_service.clear_cache()
        return {"status": "deleted", "dataset_name": dataset_name}
    except Exception as e:
        logger.error(f"Failed to delete dataset '{dataset_name}': {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete dataset: {str(e)}"
        )


@router.get("/schema")
def get_schema_explorer_details(db: Session = Depends(get_db)):
    """Returns a structured dictionary of all tables and columns for the Schema Explorer."""
    try:
        from sqlalchemy import inspect

        inspector = inspect(db.bind)
        schema_data = {}
        for table in inspector.get_table_names():
            columns = inspector.get_columns(table)
            schema_data[table] = [
                {"name": c["name"], "type": str(c["type"])} for c in columns
            ]
        return schema_data
    except Exception as e:
        logger.error(f"Failed to extract schema details: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve schema: {str(e)}"
        )


@router.post(
    "/insights",
    response_model=InsightsResponse,
    dependencies=[Depends(rate_limit_query)],
)
def generate_insights_endpoint(payload: InsightsRequest):
    """Generates business insights from query results using Gemini."""
    try:
        from backend.app.services.llm_service import llm_service

        insights_text = llm_service.generate_insights(
            question=payload.question, sql=payload.sql, data=payload.data
        )
        return InsightsResponse(insights=insights_text)
    except Exception as e:
        logger.error(f"Failed to generate insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
