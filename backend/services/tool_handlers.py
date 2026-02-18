"""Concrete tool handler implementations for the agent.

Import this module to register all tools with the tool registry.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UseCase, UseCaseStatus, Company, Industry, Transcript, Role
from db.models.use_case import UseCaseStatus as UseCaseStatusEnum
from services.tools import register_tool
from services.extraction import extract_use_cases, ExtractionError

_ROLE_LEVEL = {Role.READER: 0, Role.MAINTAINER: 1, Role.ADMIN: 2}


def _check_role(user, min_role: Role) -> dict | None:
    """Return error dict if user lacks the required role, else None."""
    if not user:
        return {"error": "Nicht authentifiziert."}
    if _ROLE_LEVEL.get(user.role, -1) < _ROLE_LEVEL[min_role]:
        return {"error": f"Keine Berechtigung. Benötigte Rolle: {min_role.value}"}

# Valid status transitions (reuse from API layer)
ALLOWED_TRANSITIONS: dict[UseCaseStatusEnum, set[UseCaseStatusEnum]] = {
    UseCaseStatusEnum.NEW: {UseCaseStatusEnum.IN_REVIEW},
    UseCaseStatusEnum.IN_REVIEW: {UseCaseStatusEnum.APPROVED, UseCaseStatusEnum.COMPLETED, UseCaseStatusEnum.NEW},
    UseCaseStatusEnum.APPROVED: {UseCaseStatusEnum.IN_PROGRESS, UseCaseStatusEnum.IN_REVIEW},
    UseCaseStatusEnum.IN_PROGRESS: {UseCaseStatusEnum.COMPLETED, UseCaseStatusEnum.APPROVED},
    UseCaseStatusEnum.COMPLETED: {UseCaseStatusEnum.ARCHIVED},
    UseCaseStatusEnum.ARCHIVED: set(),
}


# ---------- E3-UC2: list_use_cases ----------

async def _list_use_cases(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
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

async def _get_use_case(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
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

async def _create_use_case(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.MAINTAINER):
        return err
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

async def _update_use_case(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.MAINTAINER):
        return err
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

async def _set_status(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.MAINTAINER):
        return err
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

async def _archive_use_case(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.ADMIN):
        return err
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


# ---------- restore_use_case ----------

async def _restore_use_case(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.ADMIN):
        return err
    uc = await db.get(UseCase, args["use_case_id"])
    if not uc:
        return {"error": f"Use Case mit ID {args['use_case_id']} nicht gefunden."}

    if uc.status != UseCaseStatusEnum.ARCHIVED:
        return {"error": f"Use Case ist nicht archiviert (aktueller Status: '{uc.status.value}')."}

    uc.status = UseCaseStatusEnum.NEW
    await db.commit()
    await db.refresh(uc)

    return {"id": uc.id, "title": uc.title, "status": uc.status.value, "message": "Use Case wiederhergestellt."}


register_tool(
    "restore_use_case",
    {
        "type": "function",
        "function": {
            "name": "restore_use_case",
            "description": "Stelle einen archivierten Use Case wieder her (setzt Status auf 'new').",
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case_id": {"type": "integer", "description": "Die ID des Use Cases"},
                },
                "required": ["use_case_id"],
            },
        },
    },
    _restore_use_case,
)


# ---------- E3-UC8: analyze_transcript ----------

async def _analyze_transcript(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.MAINTAINER):
        return err
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
        "message": f"{len(use_cases)} Use Cases aus Transkript {transcript.id} extrahiert. Liste sie dem Nutzer auf.",
        "use_cases": [
            {"id": uc.id, "title": uc.title, "description": uc.description[:150]}
            for uc in use_cases
        ],
    }


register_tool(
    "analyze_transcript",
    {
        "type": "function",
        "function": {
            "name": "analyze_transcript",
            "description": "Analysiere ein Transkript und extrahiere Use Cases daraus mittels KI. Liste die extrahierten Use Cases dem Nutzer immer einzeln auf.",
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

async def _list_companies(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
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


# ---------- E9-UC11: list_industries ----------

async def _list_industries(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    result = await db.execute(select(Industry).order_by(Industry.name))
    industries = result.scalars().all()

    return {
        "industries": [
            {"id": i.id, "name": i.name, "description": i.description}
            for i in industries
        ],
    }


register_tool(
    "list_industries",
    {
        "type": "function",
        "function": {
            "name": "list_industries",
            "description": "Liste alle verfügbaren Branchen auf. Nutze dieses Tool BEVOR du eine Firma anlegst, um die passende Branche zu finden.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    _list_industries,
)


# ---------- E9-UC11: create_industry ----------

async def _create_industry(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.MAINTAINER):
        return err

    name = args["name"].strip()
    existing = await db.execute(select(Industry).where(Industry.name == name))
    if existing.scalar_one_or_none():
        return {"error": f"Branche '{name}' existiert bereits."}

    industry = Industry(name=name, description=args.get("description"))
    db.add(industry)
    await db.commit()
    await db.refresh(industry)

    return {"id": industry.id, "name": industry.name, "message": "Branche angelegt."}


register_tool(
    "create_industry",
    {
        "type": "function",
        "function": {
            "name": "create_industry",
            "description": "Lege eine neue Branche an.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name der Branche"},
                    "description": {"type": "string", "description": "Optionale Beschreibung der Branche"},
                },
                "required": ["name"],
            },
        },
    },
    _create_industry,
)


# ---------- E9-UC11: create_company ----------

async def _create_company(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.MAINTAINER):
        return err

    name = args["name"].strip()
    industry_id = args["industry_id"]

    industry = await db.get(Industry, industry_id)
    if not industry:
        return {"error": f"Branche mit ID {industry_id} nicht gefunden."}

    existing = await db.execute(select(Company).where(Company.name == name))
    if existing.scalar_one_or_none():
        return {"error": f"Firma '{name}' existiert bereits."}

    company = Company(name=name, industry_id=industry_id)
    db.add(company)
    await db.commit()
    await db.refresh(company)

    return {
        "id": company.id,
        "name": company.name,
        "industry_id": company.industry_id,
        "industry_name": industry.name,
        "message": "Firma angelegt.",
    }


register_tool(
    "create_company",
    {
        "type": "function",
        "function": {
            "name": "create_company",
            "description": "Lege eine neue Firma an. WICHTIG: Frage den Nutzer IMMER zuerst nach der Branche. Nutze vorher list_industries, um die verfügbaren Branchen aufzulisten und dem Nutzer zur Auswahl zu präsentieren. Lege die Firma NICHT an, ohne dass der Nutzer die Branche bestätigt hat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name der Firma"},
                    "industry_id": {"type": "integer", "description": "ID der Branche"},
                },
                "required": ["name", "industry_id"],
            },
        },
    },
    _create_company,
)


# ---------- E9-UC7: save_transcript ----------

async def _save_transcript(args: dict, db: AsyncSession, user=None, session_id=None) -> dict:
    if err := _check_role(user, Role.MAINTAINER):
        return err

    if not session_id:
        return {"error": "Kein Session-Kontext verfügbar."}

    from services.agent import get_file

    file_data = get_file(session_id)
    if not file_data:
        return {"error": "Keine angehängte Datei gefunden. Bitte zuerst eine .txt-Datei anhängen."}

    company = await db.get(Company, args["company_id"])
    if not company:
        return {"error": f"Unternehmen mit ID {args['company_id']} nicht gefunden."}

    transcript = Transcript(
        filename=file_data["filename"],
        content=file_data["content"],
        company_id=args["company_id"],
    )
    db.add(transcript)
    await db.commit()
    await db.refresh(transcript)

    return {
        "transcript_id": transcript.id,
        "message": f"Transkript '{file_data['filename']}' gespeichert (ID {transcript.id}). Nutze jetzt analyze_transcript um Use Cases zu extrahieren.",
    }


register_tool(
    "save_transcript",
    {
        "type": "function",
        "function": {
            "name": "save_transcript",
            "description": (
                "Speichere das angehängte Transkript in der Datenbank. "
                "WICHTIG: Frage den Nutzer IMMER zuerst nach der Firma. "
                "Nutze list_companies, um die verfügbaren Firmen aufzulisten und dem Nutzer zur Auswahl zu präsentieren. "
                "Führe dieses Tool NICHT aus, ohne dass der Nutzer die Firma bestätigt hat. "
                "Rufe danach analyze_transcript auf, um Use Cases zu extrahieren."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "company_id": {"type": "integer", "description": "ID des Unternehmens, dem das Transkript zugeordnet wird"},
                },
                "required": ["company_id"],
            },
        },
    },
    _save_transcript,
)
