"""Concrete tool handler implementations for the agent.

Import this module to register all tools with the tool registry.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UseCase, UseCaseStatus, Company, Transcript
from db.models.use_case import UseCaseStatus as UseCaseStatusEnum
from services.tools import register_tool
from services.extraction import extract_use_cases, ExtractionError

# Valid status transitions (reuse from API layer)
ALLOWED_TRANSITIONS: dict[UseCaseStatusEnum, set[UseCaseStatusEnum]] = {
    UseCaseStatusEnum.NEW: {UseCaseStatusEnum.IN_REVIEW},
    UseCaseStatusEnum.IN_REVIEW: {UseCaseStatusEnum.APPROVED, UseCaseStatusEnum.NEW},
    UseCaseStatusEnum.APPROVED: {UseCaseStatusEnum.IN_PROGRESS, UseCaseStatusEnum.IN_REVIEW},
    UseCaseStatusEnum.IN_PROGRESS: {UseCaseStatusEnum.COMPLETED, UseCaseStatusEnum.APPROVED},
    UseCaseStatusEnum.COMPLETED: {UseCaseStatusEnum.ARCHIVED},
    UseCaseStatusEnum.ARCHIVED: set(),
}


# ---------- E3-UC2: list_use_cases ----------

async def _list_use_cases(args: dict, db: AsyncSession, user=None) -> dict:
    query = select(UseCase)

    if args.get("company_id"):
        query = query.where(UseCase.company_id == args["company_id"])
    if args.get("status"):
        query = query.where(UseCase.status == args["status"])
    if args.get("search"):
        pattern = f"%{args['search']}%"
        query = query.where(
            UseCase.title.ilike(pattern) | UseCase.description.ilike(pattern)
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(UseCase.created_at.desc()).limit(20)
    result = await db.execute(query)
    use_cases = result.scalars().all()

    return {
        "total": total,
        "use_cases": [
            {
                "id": uc.id,
                "title": uc.title,
                "status": uc.status.value,
                "company_id": uc.company_id,
                "description": uc.description[:150] + "..." if len(uc.description) > 150 else uc.description,
            }
            for uc in use_cases
        ],
    }


register_tool(
    "list_use_cases",
    {
        "type": "function",
        "function": {
            "name": "list_use_cases",
            "description": "Liste Use Cases auf, optional gefiltert nach Unternehmen, Status oder Suchbegriff.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "integer", "description": "Filter nach Unternehmens-ID"},
                    "status": {
                        "type": "string",
                        "enum": ["new", "in_review", "approved", "in_progress", "completed", "archived"],
                        "description": "Filter nach Status",
                    },
                    "search": {"type": "string", "description": "Suchbegriff für Titel oder Beschreibung"},
                },
                "required": [],
            },
        },
    },
    _list_use_cases,
)


# ---------- E3-UC3: get_use_case ----------

async def _get_use_case(args: dict, db: AsyncSession, user=None) -> dict:
    uc = await db.get(UseCase, args["use_case_id"])
    if not uc:
        return {"error": f"Use Case mit ID {args['use_case_id']} nicht gefunden."}

    return {
        "id": uc.id,
        "title": uc.title,
        "description": uc.description,
        "status": uc.status.value,
        "stakeholders": uc.stakeholders,
        "expected_benefit": uc.expected_benefit,
        "company_id": uc.company_id,
        "transcript_id": uc.transcript_id,
        "created_at": uc.created_at,
        "updated_at": uc.updated_at,
    }


register_tool(
    "get_use_case",
    {
        "type": "function",
        "function": {
            "name": "get_use_case",
            "description": "Rufe einen einzelnen Use Case mit allen Details ab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case_id": {"type": "integer", "description": "Die ID des Use Cases"},
                },
                "required": ["use_case_id"],
            },
        },
    },
    _get_use_case,
)


# ---------- E3-UC4: create_use_case ----------

async def _create_use_case(args: dict, db: AsyncSession, user=None) -> dict:
    company = await db.get(Company, args["company_id"])
    if not company:
        return {"error": f"Unternehmen mit ID {args['company_id']} nicht gefunden."}

    uc = UseCase(
        title=args["title"],
        description=args["description"],
        company_id=args["company_id"],
        stakeholders=args.get("stakeholders"),
        expected_benefit=args.get("expected_benefit"),
    )
    db.add(uc)
    await db.commit()
    await db.refresh(uc)

    return {"id": uc.id, "title": uc.title, "status": uc.status.value, "message": "Use Case erstellt."}


register_tool(
    "create_use_case",
    {
        "type": "function",
        "function": {
            "name": "create_use_case",
            "description": "Erstelle einen neuen Use Case.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Titel des Use Cases"},
                    "description": {"type": "string", "description": "Beschreibung des Use Cases"},
                    "company_id": {"type": "integer", "description": "ID des zugehörigen Unternehmens"},
                    "stakeholders": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "role": {"type": "string"},
                            },
                        },
                        "description": "Liste der Stakeholder (optional)",
                    },
                    "expected_benefit": {"type": "string", "description": "Erwarteter Nutzen (optional)"},
                },
                "required": ["title", "description", "company_id"],
            },
        },
    },
    _create_use_case,
)


# ---------- E3-UC5: update_use_case ----------

async def _update_use_case(args: dict, db: AsyncSession, user=None) -> dict:
    uc = await db.get(UseCase, args["use_case_id"])
    if not uc:
        return {"error": f"Use Case mit ID {args['use_case_id']} nicht gefunden."}

    updatable = ["title", "description", "stakeholders", "expected_benefit"]
    for field in updatable:
        if field in args:
            setattr(uc, field, args[field])

    await db.commit()
    await db.refresh(uc)

    return {"id": uc.id, "title": uc.title, "status": uc.status.value, "message": "Use Case aktualisiert."}


register_tool(
    "update_use_case",
    {
        "type": "function",
        "function": {
            "name": "update_use_case",
            "description": "Aktualisiere Felder eines Use Cases (Titel, Beschreibung, Stakeholder, Nutzen).",
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case_id": {"type": "integer", "description": "Die ID des Use Cases"},
                    "title": {"type": "string", "description": "Neuer Titel"},
                    "description": {"type": "string", "description": "Neue Beschreibung"},
                    "stakeholders": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {"name": {"type": "string"}, "role": {"type": "string"}},
                        },
                        "description": "Neue Stakeholder-Liste",
                    },
                    "expected_benefit": {"type": "string", "description": "Neuer erwarteter Nutzen"},
                },
                "required": ["use_case_id"],
            },
        },
    },
    _update_use_case,
)


# ---------- E3-UC6: set_status ----------

async def _set_status(args: dict, db: AsyncSession, user=None) -> dict:
    uc = await db.get(UseCase, args["use_case_id"])
    if not uc:
        return {"error": f"Use Case mit ID {args['use_case_id']} nicht gefunden."}

    new_status = UseCaseStatusEnum(args["new_status"])
    allowed = ALLOWED_TRANSITIONS.get(uc.status, set())

    if new_status not in allowed:
        return {
            "error": f"Ungültiger Übergang von '{uc.status.value}' nach '{new_status.value}'. "
                     f"Erlaubt: {[s.value for s in allowed]}"
        }

    uc.status = new_status
    await db.commit()
    await db.refresh(uc)

    return {"id": uc.id, "title": uc.title, "status": uc.status.value, "message": "Status geändert."}


register_tool(
    "set_status",
    {
        "type": "function",
        "function": {
            "name": "set_status",
            "description": "Ändere den Status eines Use Cases. Nur valide Übergänge sind erlaubt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case_id": {"type": "integer", "description": "Die ID des Use Cases"},
                    "new_status": {
                        "type": "string",
                        "enum": ["new", "in_review", "approved", "in_progress", "completed", "archived"],
                        "description": "Der neue Status",
                    },
                },
                "required": ["use_case_id", "new_status"],
            },
        },
    },
    _set_status,
)


# ---------- E3-UC7: archive_use_case ----------

async def _archive_use_case(args: dict, db: AsyncSession, user=None) -> dict:
    uc = await db.get(UseCase, args["use_case_id"])
    if not uc:
        return {"error": f"Use Case mit ID {args['use_case_id']} nicht gefunden."}

    if uc.status == UseCaseStatusEnum.ARCHIVED:
        return {"error": "Use Case ist bereits archiviert."}

    uc.status = UseCaseStatusEnum.ARCHIVED
    await db.commit()
    await db.refresh(uc)

    return {"id": uc.id, "title": uc.title, "status": uc.status.value, "message": "Use Case archiviert."}


register_tool(
    "archive_use_case",
    {
        "type": "function",
        "function": {
            "name": "archive_use_case",
            "description": "Archiviere einen Use Case (Soft Delete).",
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case_id": {"type": "integer", "description": "Die ID des Use Cases"},
                },
                "required": ["use_case_id"],
            },
        },
    },
    _archive_use_case,
)


# ---------- E3-UC8: analyze_transcript ----------

async def _analyze_transcript(args: dict, db: AsyncSession, user=None) -> dict:
    transcript = await db.get(Transcript, args["transcript_id"])
    if not transcript:
        return {"error": f"Transkript mit ID {args['transcript_id']} nicht gefunden."}

    try:
        extracted = await extract_use_cases(transcript.content)
    except ExtractionError as e:
        return {"error": f"Extraktion fehlgeschlagen: {e}"}

    use_cases = []
    for item in extracted:
        uc = UseCase(
            title=item.title,
            description=item.description,
            stakeholders=[s.model_dump() for s in item.stakeholders],
            expected_benefit=item.expected_benefit,
            company_id=transcript.company_id,
            transcript_id=transcript.id,
        )
        db.add(uc)
        use_cases.append(uc)

    await db.commit()
    for uc in use_cases:
        await db.refresh(uc)

    return {
        "message": f"{len(use_cases)} Use Cases aus Transkript {transcript.id} extrahiert.",
        "use_cases": [{"id": uc.id, "title": uc.title} for uc in use_cases],
    }


register_tool(
    "analyze_transcript",
    {
        "type": "function",
        "function": {
            "name": "analyze_transcript",
            "description": "Analysiere ein Transkript und extrahiere Use Cases daraus mittels KI.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transcript_id": {"type": "integer", "description": "Die ID des Transkripts"},
                },
                "required": ["transcript_id"],
            },
        },
    },
    _analyze_transcript,
)


# ---------- E3-UC10: list_companies ----------

async def _list_companies(args: dict, db: AsyncSession, user=None) -> dict:
    query = select(Company).order_by(Company.name)
    result = await db.execute(query)
    companies = result.scalars().all()

    return {
        "companies": [
            {"id": c.id, "name": c.name, "industry_id": c.industry_id}
            for c in companies
        ],
    }


register_tool(
    "list_companies",
    {
        "type": "function",
        "function": {
            "name": "list_companies",
            "description": "Liste alle Unternehmen auf.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    _list_companies,
)
