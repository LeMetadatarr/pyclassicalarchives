"""Example 09 — metadatarr provider integration.

Importing ``pyclassicalarchives._provider`` registers a MetadataProvider
that resolves a classical composer to Classical Archives ids and a
canonical composer entity. Requires ``metadatarr`` + ``mediavocab``.

This drives the provider directly so the example is self-contained. In a
real pipeline you would call ``metadatarr.resolve.base.resolve(signals)``,
which fans the same signals out across every registered provider and
merges the results.

Run::

    python examples/09_metadatarr.py
"""
import pyclassicalarchives._provider as provider_mod  # registers the provider


def main() -> None:
    from mediavocab.models.signals import Signals
    from mediavocab import PlaybackType
    from metadatarr.resolve.entities import EntityRole, allocate_entity_id

    provider = provider_mod.ClassicalArchivesProvider()

    signals = Signals(
        title="Goldberg Variations",
        artist="Johann Sebastian Bach",
        playback_type=PlaybackType.AUDIO,
        content_genres=["classical"],
    )

    match = provider.lookup(signals)
    print(f"provider   : {match.provider}")
    print(f"confidence : {match.confidence}")
    print(f"external ids: {match.external_ids.extra}")

    composers = match.relations.get(EntityRole.COMPOSER, [])
    print(f"\n{len(composers)} composer entity(ies):")
    for e in composers:
        canonical = allocate_entity_id(
            EntityRole.COMPOSER, name=e.name, external_ids=e.external_ids
        )
        print(f"   {e.name}")
        print(f"     kind          : {e.kind}")
        print(f"     external ids  : {e.external_ids.extra}")
        print(f"     canonical id  : {canonical}")

    # The provider only fires for AUDIO + 'classical'; other signals are skipped.
    other = Signals(title="Inception", playback_type=PlaybackType.VIDEO)
    print("\nClassical AUDIO signal matches provider?", provider.matches(signals))
    print("Non-classical VIDEO signal matches provider?", provider.matches(other))


if __name__ == "__main__":
    main()
