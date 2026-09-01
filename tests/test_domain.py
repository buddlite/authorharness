from writer_harness.domain import (
    Beat,
    CharacterState,
    IntentCard,
    SceneContract,
    SceneParticipant,
    SceneTier,
)


def test_scene_contract_keeps_multi_character_state_explicit() -> None:
    scene = SceneContract(
        scene_id="scene-1",
        pov_character_id="mara",
        purpose="Force Mara to choose whether to reveal the map.",
        entry_state="The group believes the bridge is safe.",
        exit_state="The group knows the bridge is watched.",
        participants=[
            SceneParticipant(character_id="mara", tier=SceneTier.FOCUS, required_presence=True),
            SceneParticipant(character_id="ivo", tier=SceneTier.ACTIVE),
            SceneParticipant(character_id="senn", tier=SceneTier.ACTIVE),
            SceneParticipant(character_id="guards", tier=SceneTier.AMBIENT),
        ],
        intent_cards=[
            IntentCard(
                character_id="mara",
                public_objective="Keep the group moving.",
                private_objective="Hide that she stole the map.",
            ),
            IntentCard(
                character_id="ivo",
                public_objective="Get an explanation from Mara.",
                knows=["Mara was absent during the alarm."],
            ),
        ],
        beats=[
            Beat(
                id="b1",
                order=0,
                summary="Ivo notices the torn map edge.",
                initiator_id="ivo",
                target_ids=["mara"],
                observer_ids=["senn"],
                required_reactions=["Mara deflects; Senn notices the lie."],
            )
        ],
    )

    assert [p.character_id for p in scene.participants if p.tier == SceneTier.ACTIVE] == [
        "ivo",
        "senn",
    ]
    assert scene.beats[0].observer_ids == ["senn"]


def test_character_state_tracks_knowledge_separately_from_false_beliefs() -> None:
    character = CharacterState(
        id="ivo",
        name="Ivo",
        knows=["The bridge was inspected yesterday."],
        suspects=["Mara hid something."],
        false_beliefs_in_play=["The map was never in Mara's possession."],
    )

    assert character.knows != character.suspects
    assert character.false_beliefs_in_play
