"""Gate 11 operator service delegating to frozen Gates 2-10 contracts."""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import Any, Callable

from rie.operator.operator_audit import OperatorAuditError
from rie.operator.operator_audit import audit_preview
from rie.operator.operator_audit import find_audit
from rie.operator.operator_audit import persist_audit
from rie.operator.operator_configuration import OperatorConfiguration
from rie.operator.operator_contract import ExitCode
from rie.operator.operator_contract import OperatorRequest
from rie.operator.operator_contract import OperatorResult
from rie.operator.operator_contract import OperatorStatus
from rie.operator.operator_contract import freeze_mapping
from rie.operator.operator_contract import make_result
from rie.operator.operator_recovery import recovery_for

ARTIFACT_SCHEMA_VERSION = "rie_operator_artifact_v1"


class OperatorConflict(ValueError):
    pass


class OperatorInputError(ValueError):
    pass


class OperatorPersistenceError(OSError):
    pass


class OperatorService:
    def __init__(self, configuration: OperatorConfiguration) -> None:
        if not isinstance(configuration, OperatorConfiguration):
            raise TypeError("configuration must be OperatorConfiguration.")
        self.configuration = configuration
        self._handlers: dict[str, Callable[[OperatorRequest], OperatorResult]] = {
            "registry validate": self._registry_validate,
            "source inspect": self._source_inspect,
            "ingest pdf": self._ingest_pdf,
            "evidence build": self._evidence_build,
            "evidence inspect": self._evidence_inspect,
            "knowledge build": self._knowledge_build,
            "knowledge inspect": self._knowledge_inspect,
            "prompt-candidate build": self._prompt_candidate_build,
            "audit job": self._audit_job,
            "export": self._export,
        }

    def execute(self, request: OperatorRequest) -> OperatorResult:
        if not isinstance(request, OperatorRequest):
            raise TypeError("request must be OperatorRequest.")
        try:
            result = self._handlers[request.command](request)
        except OperatorConflict as exc:
            result = self._failure(
                request,
                status=OperatorStatus.REJECTED,
                exit_code=ExitCode.STATE_CONFLICT_OR_IDEMPOTENCY_VIOLATION,
                issue_code="STATE_CONFLICT_OR_IDEMPOTENCY_VIOLATION",
                message=str(exc),
            )
        except OperatorInputError as exc:
            result = self._failure(
                request,
                status=OperatorStatus.REJECTED,
                exit_code=ExitCode.SOURCE_OR_INPUT_INVALID,
                issue_code="SOURCE_OR_INPUT_INVALID",
                message=str(exc),
            )
        except OperatorPersistenceError as exc:
            result = self._failure(
                request,
                status=OperatorStatus.FAILED,
                exit_code=ExitCode.PERSISTENCE_OR_IO_FAILURE,
                issue_code="PERSISTENCE_OR_IO_FAILURE",
                message=str(exc),
            )
        except Exception as exc:
            result = self._failure(
                request,
                status=OperatorStatus.FAILED,
                exit_code=ExitCode.UNEXPECTED_INTERNAL_FAILURE,
                issue_code="UNEXPECTED_INTERNAL_FAILURE",
                message=f"Unexpected operator failure: {type(exc).__name__}.",
            )

        preview = audit_preview(
            request=request,
            configuration=self.configuration,
            result=result,
        )
        if request.dry_run:
            return replace(result, audit=freeze_mapping(preview))
        try:
            audit = persist_audit(
                request=request,
                configuration=self.configuration,
                result=result,
            )
        except OperatorAuditError:
            return make_result(
                command=request.command,
                status=OperatorStatus.FAILED,
                exit_code=ExitCode.AUDIT_OR_EXPORT_FAILURE,
                issue_code="AUDIT_OR_EXPORT_FAILURE",
                message="Operator audit persistence failed.",
                dry_run=request.dry_run,
                identifiers=dict(result.identifiers),
                provenance=dict(result.provenance),
                audit=preview,
                outputs=dict(result.outputs),
                recovery=recovery_for("AUDIT_OR_EXPORT_FAILURE"),
            )
        return replace(result, audit=freeze_mapping(audit))

    def _registry_validate(self, request: OperatorRequest) -> OperatorResult:
        registry_path = self._required_path(request, "registry")
        result = _validate_registry(registry_path)
        if result.status.value != "valid":
            issue = result.issues[0]
            return self._failure(
                request,
                status=OperatorStatus.REJECTED,
                exit_code=ExitCode.SOURCE_OR_INPUT_INVALID,
                issue_code=issue.code.value,
                message=issue.message,
                provenance={"registry_path": registry_path},
            )
        return make_result(
            command=request.command,
            status=OperatorStatus.SUCCEEDED,
            exit_code=ExitCode.SUCCESS,
            issue_code="",
            message="Official Source registry is valid.",
            dry_run=request.dry_run,
            identifiers={
                "registry_digest": _file_sha256(Path(registry_path)),
                "source_count": len(result.sources),
            },
            provenance={"registry_path": registry_path},
        )

    def _source_inspect(self, request: OperatorRequest) -> OperatorResult:
        registry_path = self._required_path(request, "registry")
        source_id = self._required(request, "source_id")
        validation = _validate_registry(registry_path)
        if validation.status.value != "valid":
            issue = validation.issues[0]
            return self._failure(
                request,
                status=OperatorStatus.REJECTED,
                exit_code=ExitCode.SOURCE_OR_INPUT_INVALID,
                issue_code=issue.code.value,
                message=issue.message,
                provenance={"registry_path": registry_path},
            )
        source = next(
            (value for value in validation.sources if value.source_id == source_id),
            None,
        )
        if source is None:
            return self._failure(
                request,
                status=OperatorStatus.REJECTED,
                exit_code=ExitCode.SOURCE_OR_INPUT_INVALID,
                issue_code="SOURCE_ID_UNKNOWN",
                message="Source identifier is not present in the registry.",
                provenance={"registry_path": registry_path},
            )
        source_path = Path(source.source_path)
        if not source_path.is_absolute():
            source_path = Path(registry_path).resolve().parent / source_path
        return make_result(
            command=request.command,
            status=OperatorStatus.SUCCEEDED,
            exit_code=ExitCode.SUCCESS,
            issue_code="",
            message="Official Source inspected.",
            dry_run=request.dry_run,
            identifiers={
                "source_id": source.source_id,
                "source_type": source.source_type.value,
                "authority_status": source.authority_status.value,
                "lifecycle_status": source.lifecycle_status.value,
                "evidence_eligibility": source.evidence_eligibility.value,
            },
            provenance={
                "registry_path": registry_path,
                "source_path": str(source_path.resolve()),
            },
        )

    def _ingest_pdf(self, request: OperatorRequest) -> OperatorResult:
        registry_path = self._required_path(request, "registry")
        source_id = self._required(request, "source_id")
        output_path = self._required_output(request)
        validation = _validate_registry(registry_path)
        if validation.status.value != "valid":
            issue = validation.issues[0]
            return self._failure(
                request,
                status=OperatorStatus.REJECTED,
                exit_code=ExitCode.SOURCE_OR_INPUT_INVALID,
                issue_code=issue.code.value,
                message=issue.message,
                provenance={"registry_path": registry_path},
            )
        source = next(
            (value for value in validation.sources if value.source_id == source_id),
            None,
        )
        if source is None:
            raise OperatorInputError("Source identifier is not present in the registry.")
        source_path = Path(source.source_path)
        if not source_path.is_absolute():
            source_path = Path(registry_path).resolve().parent / source_path
        source_path = source_path.resolve()
        if source.source_type.value != "pdf":
            raise OperatorInputError("Selected source is not a PDF.")
        if not source_path.is_file():
            raise OperatorInputError("Selected PDF source does not exist.")
        source_digest = _file_sha256(source_path)
        existing = _load_optional_json(output_path)
        if existing is not None:
            if (
                existing.get("schema_version") == "rie_pdf_ingestion_artifact_v1"
                and existing.get("source_id") == source_id
                and existing.get("source_checksum") == source_digest
            ):
                return self._artifact_result(
                    request,
                    status=OperatorStatus.REUSED_EXISTING,
                    message="Exact PDF ingestion artifact already exists.",
                    output_path=output_path,
                    payload=existing,
                    identifiers={"source_id": source_id},
                    provenance={
                        "registry_path": registry_path,
                        "source_path": str(source_path),
                    },
                )
            raise OperatorConflict("PDF ingestion output already exists with different governed identity.")
        if request.dry_run:
            return make_result(
                command=request.command,
                status=OperatorStatus.DRY_RUN_VALID,
                exit_code=ExitCode.SUCCESS,
                issue_code="",
                message="PDF ingestion plan is valid.",
                dry_run=True,
                identifiers={
                    "source_id": source_id,
                    "source_checksum": source_digest,
                },
                provenance={
                    "registry_path": registry_path,
                    "source_path": str(source_path),
                },
                outputs={"planned_output_path": str(output_path)},
            )
        self.configuration.workspace_path.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        job_path = self.configuration.workspace_path / f"{source_id}.ingestion-job.json"
        execution_path = self.configuration.workspace_path / f"{source_id}.ingestion-execution.json"
        if job_path.exists() or execution_path.exists():
            raise OperatorConflict(
                "Prior partial ingestion state exists; inspect the exact job and execution report before retrying."
            )
        from rie.ingestion.controlled_source_admission_job_contract import (
            ControlledSourceAdmissionRequest,
            ControlledSourceAdmissionStatus,
        )
        from rie.ingestion.controlled_source_admission_service import (
            admit_controlled_source,
        )
        admission = admit_controlled_source(
            ControlledSourceAdmissionRequest(
                registry_path=registry_path,
                source_id=source_id,
                output_location=job_path,
            )
        )
        if admission.status is not ControlledSourceAdmissionStatus.ADMITTED:
            issue = admission.issue
            return self._failure(
                request,
                status=OperatorStatus.REJECTED,
                exit_code=ExitCode.CONTRACT_OR_ELIGIBILITY_REJECTED,
                issue_code=issue.code.value,
                message=issue.message,
                identifiers={"source_id": source_id},
                provenance={
                    "registry_path": registry_path,
                    "source_path": str(source_path),
                },
                outputs={"job_path": str(job_path)},
            )
        from rie.ingestion.pdf_ingestion_orchestrator_contract import (
            PdfIngestionOrchestratorRequest,
            PdfIngestionOrchestratorStatus,
        )
        from rie.ingestion.pdf_ingestion_orchestrator_service import (
            PdfIngestionOrchestratorService,
        )
        orchestration = PdfIngestionOrchestratorService().execute(
            PdfIngestionOrchestratorRequest(
                job=admission.job,
                execution_report_location=execution_path,
            )
        )
        if orchestration.status is not PdfIngestionOrchestratorStatus.COMPLETED:
            issue = orchestration.issue
            return self._failure(
                request,
                status=OperatorStatus.FAILED,
                exit_code=ExitCode.PERSISTENCE_OR_IO_FAILURE,
                issue_code=issue.code.value,
                message=issue.message,
                identifiers={
                    "source_id": source_id,
                    "job_id": orchestration.job_id,
                },
                provenance={
                    "registry_path": registry_path,
                    "source_path": str(source_path),
                },
                outputs={
                    "job_path": str(job_path),
                    "execution_report_path": str(execution_path),
                },
            )
        page_extractions = [
            {
                "source_path": item.source_path,
                "size_bytes": item.size_bytes,
                "page_number": item.page_number,
                "extraction_index": item.extraction_index,
                "extraction_method": item.extraction_method,
                "content": item.content,
                "warnings": list(item.warnings),
            }
            for item in orchestration.page_extractions
        ]
        payload = {
            "schema_version": "rie_pdf_ingestion_artifact_v1",
            "job_id": orchestration.job_id,
            "source_id": orchestration.source_id,
            "source_path": orchestration.source_path,
            "source_checksum": orchestration.source_checksum,
            "execution_report_path": orchestration.execution_report_location,
            "page_extractions": page_extractions,
        }
        status = _write_json_artifact(output_path, payload)
        return self._artifact_result(
            request,
            status=status,
            message="PDF ingestion completed.",
            output_path=output_path,
            payload=payload,
            identifiers={
                "source_id": source_id,
                "job_id": orchestration.job_id,
                "page_count": len(page_extractions),
            },
            provenance={
                "registry_path": registry_path,
                "source_path": str(source_path),
                "source_checksum": orchestration.source_checksum,
            },
            extra_outputs={
                "job_path": str(job_path),
                "execution_report_path": str(execution_path),
            },
        )

    def _evidence_build(self, request: OperatorRequest) -> OperatorResult:
        input_path = self._required_path(request, "input")
        output_path = self._required_output(request)
        source = _load_json(Path(input_path))
        pages = source.get("page_extractions")
        if not isinstance(pages, list):
            raise OperatorInputError("PDF ingestion artifact page_extractions must be a list.")
        from evidence.pdf_text_extraction_evidence_builder import (
            PdfTextExtractionEvidenceBuilder,
        )
        full_records = []
        generic_records = []
        for index, record in enumerate(pages):
            evidence = PdfTextExtractionEvidenceBuilder.build(record, index)
            full_records.append(asdict(evidence))
            generic_records.append(
                {
                    "source_path": evidence.source_path,
                    "content": evidence.content,
                    "size_bytes": evidence.size_bytes,
                }
            )
        payload = {
            "schema_version": "rie_evidence_artifact_v1",
            "source_artifact_sha256": _file_sha256(Path(input_path)),
            "pdf_text_evidences": full_records,
            "evidences": generic_records,
        }
        return self._build_json_result(
            request,
            input_path=Path(input_path),
            output_path=output_path,
            payload=payload,
            item_key="evidences",
            item_count=len(generic_records),
            message="Evidence artifact built.",
        )

    def _evidence_inspect(self, request: OperatorRequest) -> OperatorResult:
        path = Path(self._required_path(request, "input"))
        artifact = _load_json(path)
        values = artifact.get("evidences")
        if not isinstance(values, list):
            raise OperatorInputError("Evidence artifact evidences must be a list.")
        return self._inspection_result(
            request,
            path=path,
            kind="evidence",
            count=len(values),
        )

    def _knowledge_build(self, request: OperatorRequest) -> OperatorResult:
        input_path = Path(self._required_path(request, "input"))
        output_path = self._required_output(request)
        artifact = _load_json(input_path)
        from knowledge.text_knowledge_collector import TextKnowledgeCollector
        from knowledge.text_knowledge_collection_serializer import to_dict
        collection = TextKnowledgeCollector.collect(artifact)
        payload = {
            "schema_version": "rie_knowledge_artifact_v1",
            "source_artifact_sha256": _file_sha256(input_path),
            **to_dict(collection),
        }
        return self._build_json_result(
            request,
            input_path=input_path,
            output_path=output_path,
            payload=payload,
            item_key="knowledge_items",
            item_count=len(payload["knowledge_items"]),
            message="Knowledge artifact built.",
        )

    def _knowledge_inspect(self, request: OperatorRequest) -> OperatorResult:
        path = Path(self._required_path(request, "input"))
        artifact = _load_json(path)
        values = artifact.get("knowledge_items")
        if not isinstance(values, list):
            raise OperatorInputError("Knowledge artifact knowledge_items must be a list.")
        return self._inspection_result(
            request,
            path=path,
            kind="knowledge",
            count=len(values),
        )

    def _prompt_candidate_build(self, request: OperatorRequest) -> OperatorResult:
        input_path = Path(self._required_path(request, "input"))
        output_path = self._required_output(request)
        artifact = _load_json(input_path)
        from prompting.text_prompt_candidate_collector import (
            TextPromptCandidateCollector,
        )
        from prompting.text_prompt_candidate_collection_serializer import (
            TextPromptCandidateCollectionSerializer,
        )
        collection = TextPromptCandidateCollector.collect(artifact)
        payload = {
            "schema_version": "rie_prompt_candidate_artifact_v1",
            "source_artifact_sha256": _file_sha256(input_path),
            **TextPromptCandidateCollectionSerializer.to_dict(collection),
        }
        return self._build_json_result(
            request,
            input_path=input_path,
            output_path=output_path,
            payload=payload,
            item_key="prompt_candidates",
            item_count=len(payload["prompt_candidates"]),
            message="Prompt Candidate artifact built.",
        )

    def _audit_job(self, request: OperatorRequest) -> OperatorResult:
        audit_id = self._required(request, "audit_id")
        record = find_audit(self.configuration.audit_path, audit_id)
        if record is None:
            raise OperatorInputError("Audit identifier was not found.")
        return make_result(
            command=request.command,
            status=OperatorStatus.SUCCEEDED,
            exit_code=ExitCode.SUCCESS,
            issue_code="",
            message="Audit record inspected.",
            dry_run=request.dry_run,
            identifiers={
                "audit_id": audit_id,
                "operation_id": record.get("operation_id", ""),
                "sequence": record.get("sequence", ""),
                "recorded_command": record.get("command", ""),
            },
            provenance={"audit_path": str(self.configuration.audit_path)},
        )

    def _export(self, request: OperatorRequest) -> OperatorResult:
        input_path = Path(self._required_path(request, "input")).resolve()
        output_path = self._required_output(request)
        overwrite = request.argument_map.get("overwrite", "false") == "true"
        if not input_path.is_file():
            raise OperatorInputError("Export input does not exist.")
        source_bytes = input_path.read_bytes()
        source_digest = sha256(source_bytes).hexdigest()
        if output_path.exists():
            if output_path.read_bytes() == source_bytes:
                return make_result(
                    command=request.command,
                    status=OperatorStatus.NO_CHANGE,
                    exit_code=ExitCode.SUCCESS,
                    issue_code="",
                    message="Export output already matches the exact input.",
                    dry_run=request.dry_run,
                    identifiers={"artifact_digest": source_digest},
                    provenance={"input_path": str(input_path)},
                    outputs={"output_path": str(output_path)},
                )
            if not overwrite:
                raise OperatorConflict("Export output exists and explicit overwrite was not requested.")
        if request.dry_run:
            return make_result(
                command=request.command,
                status=OperatorStatus.DRY_RUN_VALID,
                exit_code=ExitCode.SUCCESS,
                issue_code="",
                message="Export plan is valid.",
                dry_run=True,
                identifiers={"artifact_digest": source_digest},
                provenance={"input_path": str(input_path)},
                outputs={"planned_output_path": str(output_path)},
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_path.with_name("." + output_path.name + ".tmp")
        if temporary.exists():
            raise OperatorConflict("Export temporary path already exists.")
        try:
            temporary.write_bytes(source_bytes)
            temporary.replace(output_path)
        except OSError as exc:
            raise OperatorPersistenceError("Export persistence failed.") from exc
        return make_result(
            command=request.command,
            status=OperatorStatus.SUCCEEDED,
            exit_code=ExitCode.SUCCESS,
            issue_code="",
            message="Artifact exported.",
            dry_run=False,
            identifiers={"artifact_digest": source_digest},
            provenance={"input_path": str(input_path)},
            outputs={
                "output_path": str(output_path),
                "bytes": len(source_bytes),
                "sha256": source_digest,
            },
        )

    def _build_json_result(
        self,
        request: OperatorRequest,
        *,
        input_path: Path,
        output_path: Path,
        payload: dict[str, Any],
        item_key: str,
        item_count: int,
        message: str,
    ) -> OperatorResult:
        existing = _load_optional_json(output_path)
        if existing is not None:
            if _canonical_json(existing) == _canonical_json(payload):
                status = OperatorStatus.REUSED_EXISTING
            else:
                raise OperatorConflict("Output exists with different governed content.")
        elif request.dry_run:
            return make_result(
                command=request.command,
                status=OperatorStatus.DRY_RUN_VALID,
                exit_code=ExitCode.SUCCESS,
                issue_code="",
                message=f"{message} Dry-run plan is valid.",
                dry_run=True,
                identifiers={f"{item_key}_count": item_count},
                provenance={
                    "input_path": str(input_path),
                    "input_sha256": _file_sha256(input_path),
                },
                outputs={"planned_output_path": str(output_path)},
            )
        else:
            status = _write_json_artifact(output_path, payload)
        return self._artifact_result(
            request,
            status=status,
            message=message,
            output_path=output_path,
            payload=payload,
            identifiers={f"{item_key}_count": item_count},
            provenance={
                "input_path": str(input_path),
                "input_sha256": _file_sha256(input_path),
            },
        )

    def _inspection_result(
        self,
        request: OperatorRequest,
        *,
        path: Path,
        kind: str,
        count: int,
    ) -> OperatorResult:
        return make_result(
            command=request.command,
            status=OperatorStatus.SUCCEEDED,
            exit_code=ExitCode.SUCCESS,
            issue_code="",
            message=f"{kind.capitalize()} artifact inspected.",
            dry_run=request.dry_run,
            identifiers={
                "artifact_kind": kind,
                "item_count": count,
                "artifact_sha256": _file_sha256(path),
            },
            provenance={"input_path": str(path.resolve())},
        )

    def _artifact_result(
        self,
        request: OperatorRequest,
        *,
        status: OperatorStatus,
        message: str,
        output_path: Path,
        payload: dict[str, Any],
        identifiers: dict[str, object],
        provenance: dict[str, object],
        extra_outputs: dict[str, object] | None = None,
    ) -> OperatorResult:
        payload_bytes = _canonical_json(payload)
        outputs: dict[str, object] = {
            "output_path": str(output_path),
            "sha256": sha256(payload_bytes).hexdigest(),
            "bytes": len(payload_bytes),
        }
        if extra_outputs:
            outputs.update(extra_outputs)
        return make_result(
            command=request.command,
            status=status,
            exit_code=ExitCode.SUCCESS,
            issue_code="",
            message=message,
            dry_run=request.dry_run,
            identifiers=identifiers,
            provenance=provenance,
            outputs=outputs,
        )

    def _failure(
        self,
        request: OperatorRequest,
        *,
        status: OperatorStatus,
        exit_code: ExitCode,
        issue_code: str,
        message: str,
        identifiers: dict[str, object] | None = None,
        provenance: dict[str, object] | None = None,
        outputs: dict[str, object] | None = None,
    ) -> OperatorResult:
        return make_result(
            command=request.command,
            status=status,
            exit_code=exit_code,
            issue_code=issue_code,
            message=message,
            dry_run=request.dry_run,
            identifiers=identifiers,
            provenance=provenance,
            outputs=outputs,
            recovery=recovery_for(issue_code),
        )

    @staticmethod
    def _required(request: OperatorRequest, name: str) -> str:
        value = request.argument_map.get(name, "")
        if value.strip() == "":
            raise OperatorInputError(f"{name} is required.")
        return value

    def _required_path(self, request: OperatorRequest, name: str) -> str:
        value = self._required(request, name)
        path = Path(value).resolve()
        if not path.is_file():
            raise OperatorInputError(f"{name} does not identify a file.")
        return str(path)

    @staticmethod
    def _required_output(request: OperatorRequest) -> Path:
        if request.output_path is None or request.output_path.strip() == "":
            raise OperatorInputError("An explicit output path is required.")
        return Path(request.output_path).resolve()


def _validate_registry(registry_path: str):
    from official_source.official_source_registry_validation import (
        OfficialSourceRegistryValidationRequest,
        validate_official_source_registry,
    )
    return validate_official_source_registry(
        OfficialSourceRegistryValidationRequest(registry_path=registry_path)
    )


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
        )
        + "\n"
    ).encode("ascii")


def _write_json_artifact(
    output_path: Path,
    payload: dict[str, Any],
) -> OperatorStatus:
    data = _canonical_json(payload)
    if output_path.exists():
        if output_path.read_bytes() == data:
            return OperatorStatus.REUSED_EXISTING
        raise OperatorConflict("Output path already exists with different content.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name("." + output_path.name + ".tmp")
    if temporary.exists():
        raise OperatorConflict("Output temporary path already exists.")
    try:
        temporary.write_bytes(data)
        temporary.replace(output_path)
    except OSError as exc:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass
        raise OperatorPersistenceError("Artifact persistence failed.") from exc
    return OperatorStatus.SUCCEEDED


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OperatorInputError("Input artifact is unreadable or invalid JSON.") from exc
    if not isinstance(value, dict):
        raise OperatorInputError("Input artifact must be a JSON object.")
    return value


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _file_sha256(path: Path) -> str:
    digest = sha256()
    try:
        with path.open("rb") as stream:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        raise OperatorInputError("Input file is unreadable.") from exc
    return digest.hexdigest()


__all__ = (
    "ARTIFACT_SCHEMA_VERSION",
    "OperatorConflict",
    "OperatorInputError",
    "OperatorPersistenceError",
    "OperatorService",
)
