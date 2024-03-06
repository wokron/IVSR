from typing import Any
from pydantic import BaseModel, Field


class Permission(BaseModel):
    status: str
    info: str
    description: str


class MalwarePermissions(BaseModel):
    top_malware_permissions: list[str]
    other_abused_permissions: list[str]
    total_malware_permissions: int
    total_other_permissions: int


class Metadata(BaseModel):
    description: str
    severity: str


class AndroidAPI(BaseModel):
    files: dict[str, str]
    metadata: Metadata


class CertificateAnalysis(BaseModel):
    certificate_info: str
    certificate_findings: list[list[str]]


class ManifestFinding(BaseModel):
    rule: str
    title: str
    severity: str
    description: str
    name: str
    component: list[str]


class ManifestAnalysis(BaseModel):
    manifest_findings: list[ManifestFinding]


class NetworkFinding(BaseModel):
    scope: list[str]
    description: str
    severity: str


class NetworkSecurity(BaseModel):
    network_findings: list[NetworkFinding]


class BinaryAnalysisAttr(BaseModel):
    severity: str
    description: str
    is_nx: bool | None = Field(None)
    has_canary: bool | None = Field(None)
    relro: str | None = Field(None)
    rpath: str | None = Field(None)
    runpath: str | None = Field(None)
    is_fortified: bool | None = Field(None)
    is_stripped: bool | None = Field(None)


class BinaryAnalysis(BaseModel):
    name: str
    nx: BinaryAnalysisAttr
    stack_canary: BinaryAnalysisAttr
    relocation_readonly: BinaryAnalysisAttr
    rpath: BinaryAnalysisAttr
    runpath: BinaryAnalysisAttr
    fortify: BinaryAnalysisAttr
    symbol: BinaryAnalysisAttr


class CodeAnalysisMetadata(Metadata):
    cvss: float
    cwe: str
    masvs: str
    ref: str | None = Field(None)


class CodeAnalysisFinding(BaseModel):
    metadata: CodeAnalysisMetadata
    files: dict[str, str]


class CodeAnalysis(BaseModel):
    findings: dict[str, CodeAnalysisFinding]


class ScanResponse(BaseModel):
    file_name: str
    app_name: str
    size: str
    package_name: str
    main_activity: str

    activities: list[str]
    receivers: list[str]
    providers: list[str]
    services: list[str]
    permissions: dict[str, Permission]
    malware_permissions: MalwarePermissions
    permission_mapping: dict[str, dict[str, str]]
    android_api: dict[str, AndroidAPI]

    certificate_analysis: CertificateAnalysis
    manifest_analysis: ManifestAnalysis
    network_security: NetworkSecurity
    binary_analysis: list[BinaryAnalysis]
    code_analysis: CodeAnalysis
    secrets: list[str]


class UploadResponse(BaseModel):
    file_name: str
    hash: str
    scan_type: str


class Error(BaseModel):
    error: Any


class DownloadSourceResponse(BaseModel):
    file: str
    data: str
    type: str
