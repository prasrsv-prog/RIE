from dataclasses import dataclass


@dataclass(frozen=True)
class RealFilesystemMetadataAdapterSafetyDecision:
    allowed: bool
    reason: str
    max_items: int
    allow_recursive: bool
    allow_content_reads: bool
    allow_mutation: bool
    allow_symlinks: bool
    require_stable_ordering: bool


class RealFilesystemMetadataAdapterSafetyContract:
    MAX_ITEMS_LIMIT = 100

    @staticmethod
    def evaluate(
        max_items: int = 100,
        allow_recursive: bool = False,
        allow_content_reads: bool = False,
        allow_mutation: bool = False,
        allow_symlinks: bool = False,
        require_stable_ordering: bool = True,
    ) -> RealFilesystemMetadataAdapterSafetyDecision:
        allowed = False

        if max_items <= 0:
            reason = "Positive max_items is required."
        elif max_items > RealFilesystemMetadataAdapterSafetyContract.MAX_ITEMS_LIMIT:
            reason = "Metadata adapter max_items limit exceeded."
        elif allow_recursive is True:
            reason = "Recursive metadata collection is forbidden."
        elif allow_content_reads is True:
            reason = "Content reads are forbidden."
        elif allow_mutation is True:
            reason = "Metadata adapter mutation is forbidden."
        elif allow_symlinks is True:
            reason = "Symlink traversal is not approved yet."
        elif require_stable_ordering is False:
            reason = "Stable ordering is required before smoke flow."
        else:
            allowed = True
            reason = "Filesystem metadata adapter safety contract passed."

        return RealFilesystemMetadataAdapterSafetyDecision(
            allowed=allowed,
            reason=reason,
            max_items=max_items,
            allow_recursive=allow_recursive,
            allow_content_reads=allow_content_reads,
            allow_mutation=allow_mutation,
            allow_symlinks=allow_symlinks,
            require_stable_ordering=require_stable_ordering,
        )
