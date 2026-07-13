from __future__ import annotations

from app.services.feature_store.schema import (
    DEFAULT_FEATURE_DEFINITIONS,
    FeatureDefinition,
)


class FeatureDefinitionRegistry:
    def __init__(self) -> None:
        self._definitions: dict[
            str,
            FeatureDefinition,
        ] = {}

    def register(
        self,
        definition: FeatureDefinition,
    ) -> None:
        self._definitions[
            definition.name
        ] = definition

    def get(
        self,
        feature_name: str,
    ) -> FeatureDefinition:
        try:
            return self._definitions[
                feature_name
            ]
        except KeyError as exc:
            raise KeyError(
                f"Feature '{feature_name}' is not registered."
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(
            sorted(self._definitions)
        )


def create_default_feature_registry(
) -> FeatureDefinitionRegistry:
    registry = FeatureDefinitionRegistry()

    for definition in DEFAULT_FEATURE_DEFINITIONS.values():
        registry.register(definition)

    return registry
