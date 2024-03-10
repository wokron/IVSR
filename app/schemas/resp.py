from pydantic import BaseModel, Field

from app.schemas import mobsf


class AppInfo(BaseModel):
    app_name: str
    package_name: str
    size: str
    package_name: str
    cert_info: str

    @staticmethod
    def from_mobsf(resp: mobsf.ScanResponse):
        return AppInfo(
            app_name=resp.app_name,
            package_name=resp.package_name,
            size=resp.size,
            cert_info=resp.certificate_analysis.certificate_info,
        )


class AppComps(BaseModel):
    main_activity: str
    activities: list[str]
    receivers: list[str]
    providers: list[str]
    services: list[str]

    @staticmethod
    def from_mobsf(resp: mobsf.ScanResponse):
        return AppComps(
            main_activity=resp.main_activity,
            activities=resp.activities,
            receivers=resp.receivers,
            providers=resp.providers,
            services=resp.services,
        )


class CodeLines(BaseModel):
    file: str
    lines_no: list[int]

    @staticmethod
    def from_mobsf(file_name, lines_no_str):
        return CodeLines(
            file=file_name,
            lines_no=[int(no) for no in lines_no_str.split(",")],
        )


class ResultBase(BaseModel):
    name: str
    severity: str
    description: str


class CertResult(ResultBase):
    @staticmethod
    def from_mobsf(finding: list[str]):
        return CertResult(name=finding[2], severity=finding[0], description=finding[1])


class MalwarePermsStat(BaseModel):
    top_malware_perms: list[str]
    other_abused_perms: list[str]
    total_malware_perms: int
    total_other_perms: int

    @staticmethod
    def from_mobsf(result: mobsf.MalwarePermissions):
        return MalwarePermsStat(
            top_malware_perms=result.top_malware_permissions,
            other_abused_perms=result.other_abused_permissions,
            total_malware_perms=result.total_malware_permissions,
            total_other_perms=result.total_other_permissions,
        )


class PermResult(ResultBase):
    info: str
    sources: list[CodeLines]

    @staticmethod
    def from_mobsf(name: str, perm: mobsf.Permission, perm_mapping: dict[str, str]):
        severity_map = {"normal": "info", "dangerous": "warning", "unknown": "warning"}
        severity = severity_map[perm.status]
        sources = [
            CodeLines.from_mobsf(file_name, lines_no)
            for file_name, lines_no in perm_mapping.items()
        ]

        return PermResult(
            name=name,
            severity=severity,
            description=perm.description,
            info=perm.info,
            sources=sources,
        )


class PermResults(BaseModel):
    perms: list[PermResult]
    malware_perms_stat: MalwarePermsStat

    @staticmethod
    def from_mobsf(resp: mobsf.ScanResponse):
        return PermResults(
            perms=[
                PermResult.from_mobsf(name, perm, resp.permission_mapping.get(name, {}))
                for name, perm in resp.permissions.items()
            ],
            malware_perms_stat=MalwarePermsStat.from_mobsf(resp.malware_permissions),
        )


class ManifestResult(ResultBase):
    rule: str
    component: list[str]

    @staticmethod
    def from_mobsf(result: mobsf.ManifestFinding):
        return ManifestResult(
            name=result.name,
            severity=result.severity,
            description=result.description,
            rule=result.rule,
            component=result.component,
        )


class NetworkResult(ResultBase):
    @staticmethod
    def from_mobsf(result: mobsf.NetworkFinding):
        return NetworkResult(
            name=f"Scope '{', '.join(result.scope)}'",
            severity=result.severity,
            description=result.description,
        )


class NXResult(ResultBase):
    is_nx: bool

    @staticmethod
    def from_mobsf(result: mobsf.BinaryAnalysisAttr):
        return NXResult(
            name="nx",
            severity=result.severity,
            description=result.description,
            is_nx=result.is_nx,
        )


class HasCanaryResult(ResultBase):
    has_canary: bool

    @staticmethod
    def from_mobsf(result: mobsf.BinaryAnalysisAttr):
        return HasCanaryResult(
            name="stack_canary",
            severity=result.severity,
            description=result.description,
            has_canary=result.has_canary,
        )


class RELROResult(ResultBase):
    relro: str | None

    @staticmethod
    def from_mobsf(result: mobsf.BinaryAnalysisAttr):
        return RELROResult(
            name="relocation_readonly",
            severity=result.severity,
            description=result.description,
            relro=result.relro,
        )


class RPathResult(ResultBase):
    rpath: str | None

    @staticmethod
    def from_mobsf(result: mobsf.BinaryAnalysisAttr):
        return RPathResult(
            name="rpath",
            severity=result.severity,
            description=result.description,
            rpath=result.rpath,
        )


class RunPathResult(ResultBase):
    runpath: str | None

    @staticmethod
    def from_mobsf(result: mobsf.BinaryAnalysisAttr):
        return RunPathResult(
            name="runpath",
            severity=result.severity,
            description=result.description,
            runpath=result.runpath,
        )


class IsFortifiedResult(ResultBase):
    is_fortified: bool

    @staticmethod
    def from_mobsf(result: mobsf.BinaryAnalysisAttr):
        return IsFortifiedResult(
            name="fortify",
            severity=result.severity,
            description=result.description,
            is_fortified=result.is_fortified,
        )


class IsStrippedResult(ResultBase):
    is_stripped: bool

    @staticmethod
    def from_mobsf(result: mobsf.BinaryAnalysisAttr):
        return IsStrippedResult(
            name="symbol",
            severity=result.severity,
            description=result.description,
            is_stripped=result.is_stripped,
        )


class BinaryResults(BaseModel):
    name: str
    is_nx: NXResult
    has_canary: HasCanaryResult
    relro: RELROResult
    rpath: RPathResult
    runpath: RunPathResult
    is_fortified: IsFortifiedResult
    is_stripped: IsStrippedResult

    @staticmethod
    def from_mobsf(result: mobsf.BinaryAnalysis):
        return BinaryResults(
            name=result.name,
            is_nx=NXResult.from_mobsf(result.nx),
            has_canary=HasCanaryResult.from_mobsf(result.stack_canary),
            relro=RELROResult.from_mobsf(result.relocation_readonly),
            rpath=RPathResult.from_mobsf(result.rpath),
            runpath=RunPathResult.from_mobsf(result.runpath),
            is_fortified=IsFortifiedResult.from_mobsf(result.fortify),
            is_stripped=IsStrippedResult.from_mobsf(result.symbol),
        )


class CodeResult(ResultBase):
    cvss: float
    cwe: str
    masvs: str
    ref: str | None = Field(None)
    sources: list[CodeLines]

    @staticmethod
    def from_mobsf(name: str, result: mobsf.CodeAnalysisFinding):
        return CodeResult(
            name=name,
            severity=result.metadata.severity,
            description=result.metadata.description,
            cvss=result.metadata.cvss,
            cwe=result.metadata.cwe,
            masvs=result.metadata.masvs,
            ref=result.metadata.ref,
            sources=[
                CodeLines.from_mobsf(file_name, lines_no)
                for file_name, lines_no in result.files.items()
            ],
        )


class SecretResult(ResultBase):
    possible_secrets: list[str]

    @staticmethod
    def from_mobsf(secrets: list[str]):
        return SecretResult(
            name="This app may contain hardcoded secrets",
            severity="warning",
            description="The following secrets were identified from the app. Ensure that these are not secrets or private information.",
            possible_secrets=secrets,
        )


class StaticScanResult(BaseModel):
    app_info: AppInfo
    app_comps: AppComps

    cert_results: list[CertResult]
    prem_results: PermResults
    manifest_results: list[ManifestResult]
    network_results: list[NetworkResult]
    binary_results: list[BinaryResults]
    code_results: list[CodeResult]
    secrets_results: SecretResult | None = Field(None)

    @staticmethod
    def from_mobsf(resp: mobsf.ScanResponse):
        return StaticScanResult(
            app_info=AppInfo.from_mobsf(resp),
            app_comps=AppComps.from_mobsf(resp),
            cert_results=[
                CertResult.from_mobsf(finding)
                for finding in resp.certificate_analysis.certificate_findings
            ],
            prem_results=PermResults.from_mobsf(resp),
            manifest_results=[
                ManifestResult.from_mobsf(result)
                for result in resp.manifest_analysis.manifest_findings
            ],
            network_results=[
                NetworkResult.from_mobsf(result)
                for result in resp.network_security.network_findings
            ],
            binary_results=[
                BinaryResults.from_mobsf(result) for result in resp.binary_analysis
            ],
            code_results=[
                CodeResult.from_mobsf(name, result)
                for name, result in resp.code_analysis.findings.items()
            ],
            secrets_results=(
                SecretResult.from_mobsf(resp.secrets)
                if len(resp.secrets) != 0
                else None
            ),
        )


class MLScanFeature(BaseModel):
    feature: str
    associate_features: list[str]


class MLScanResult(BaseModel):
    apk_name: str
    malware_score: float
    key_features: list[MLScanFeature]


class SourceFile(BaseModel):
    file: str
    data: str
    type: str
