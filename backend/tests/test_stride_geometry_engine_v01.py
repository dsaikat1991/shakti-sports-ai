"""
Tests for stride_geometry_engine.py.

**Substantially expanded in the 2026-07-17 §stride-geometry correction
pass** (docs/ENGINEERING_HANDOFF.md) - the original test fixtures used
`confidence` on a [0, 1] scale (e.g. `confidence=0.94`), which is why
the confidence-scale bug found in this pass (`confidence_percent`'s
`clamp()` silently saturating any value >1.0 to exactly 1.0) was
invisible here but immediately apparent on real footage, whose
`FootContactEvent.confidence` values come from
`biomechanics/contact_events.py` on a 0-100 scale. `contact()`'s
default below is now 0-100, matching the real, documented contract on
`FootContactEvent` (see that dataclass's docstring).
"""

import unittest

from app.services.sprint.stride_geometry_engine import (
    analyze_stride_geometry,
)
from app.services.sprint.stride_geometry_models import (
    FootContactEvent,
    StrideGeometryContext,
)
from app.services.sprint.stride_geometry_report import (
    build_stride_geometry_report,
)


def contact(
    index: int,
    *,
    side: str,
    foot_x: float,
    foot_y: float,
    com_x: float | None = None,
    com_y: float = 0.50,
    confidence: float = 92.0,
    toe_x: float | None = None,
    toe_y: float | None = None,
    heel_x: float | None = None,
    heel_y: float | None = None,
) -> FootContactEvent:
    if com_x is None:
        com_x = foot_x - 0.02

    return FootContactEvent(
        side=side,
        frame_index=index,
        timestamp_ms=index * 120,
        foot_x=foot_x,
        foot_y=foot_y,
        com_x=com_x,
        com_y=com_y,
        toe_x=foot_x + 0.03 if toe_x is None else toe_x,
        toe_y=foot_y if toe_y is None else toe_y,
        heel_x=foot_x - 0.03 if heel_x is None else heel_x,
        heel_y=foot_y if heel_y is None else heel_y,
        confidence=confidence,
    )


def alternating_contacts(
    count: int,
    *,
    step_x: float = 0.48,
    left_y: float = 0.44,
    right_y: float = 0.56,
    confidence: float = 92.0,
    jitter: float = 0.0,
) -> list[FootContactEvent]:
    """A clean, alternating-side contact sequence - the well-behaved
    baseline most tests start from. `jitter` adds a small deterministic
    per-contact offset to step_x to simulate real-world noise without
    randomness (keeps tests reproducible)."""
    contacts = []
    for index in range(count):
        side = "left" if index % 2 == 0 else "right"
        wobble = jitter * (1 if index % 3 == 0 else -1)
        contacts.append(
            contact(
                index,
                side=side,
                foot_x=index * step_x + wobble,
                foot_y=left_y if side == "left" else right_y,
                confidence=confidence,
            )
        )
    return contacts


class TestStrideGeometryEngineV01(unittest.TestCase):
    def setUp(self) -> None:
        self.context = StrideGeometryContext(
            body_height_normalized=0.70,
            leg_length_normalized=0.42,
            real_world_scale_m_per_unit=2.2,
            athlete_height_m=1.78,
        )

    # ------------------------------------------------------------------
    # Original behavioral coverage, retained and corrected for scale
    # ------------------------------------------------------------------

    def test_balanced_stride_geometry(self) -> None:
        contacts = alternating_contacts(10)  # 5 per side - clears the imbalance-warning threshold

        result = analyze_stride_geometry(
            contacts,
            context=self.context,
            cadence_spm=280.0,
            horizontal_velocity=2.2,
        )

        self.assertEqual(result["status"], "experimental")

        metrics = result["metrics"]
        self.assertGreater(metrics["step_length_symmetry_score"], 90.0)
        self.assertIsNotNone(metrics["average_step_length_m"])
        self.assertIsNotNone(metrics["overall_stride_geometry_score"])

    def test_asymmetry_reduces_symmetry_score(self) -> None:
        contacts = [
            contact(0, side="left", foot_x=0.00, foot_y=0.44),
            contact(1, side="right", foot_x=0.40, foot_y=0.56),
            contact(2, side="left", foot_x=1.10, foot_y=0.44),
            contact(3, side="right", foot_x=1.50, foot_y=0.56),
            contact(4, side="left", foot_x=2.20, foot_y=0.44),
        ]

        result = analyze_stride_geometry(contacts, context=self.context)

        self.assertLess(result["metrics"]["step_length_symmetry_score"], 80.0)

    def test_requires_minimum_contacts(self) -> None:
        result = analyze_stride_geometry(
            [
                contact(0, side="left", foot_x=0.0, foot_y=0.44),
                contact(1, side="right", foot_x=0.5, foot_y=0.56),
            ],
            context=self.context,
        )

        self.assertEqual(result["status"], "insufficient_data")
        self.assertIsNone(result["metrics"])

    def test_report(self) -> None:
        contacts = alternating_contacts(6)

        result = analyze_stride_geometry(
            contacts,
            context=self.context,
            cadence_spm=280.0,
            horizontal_velocity=2.2,
        )

        report = build_stride_geometry_report(result)

        self.assertEqual(report["status"], "completed")

    # ------------------------------------------------------------------
    # Coordinate / axis tests - the §stride-geometry correction pass's
    # central finding was an axis-selection bug (crossover compared the
    # vertical Y axis instead of a lateral quantity). These tests pin
    # down which axis each metric actually uses, so a future regression
    # of the same kind fails loudly.
    # ------------------------------------------------------------------

    def test_step_length_uses_x_axis_not_y(self) -> None:
        # Two contacts with IDENTICAL x (no real forward progress) but
        # very different y - a correct X-axis step-length measurement
        # must report ~0, not react to the y difference at all.
        contacts = [
            contact(0, side="left", foot_x=0.50, foot_y=0.10),
            contact(1, side="right", foot_x=0.50, foot_y=0.90),
            contact(2, side="left", foot_x=0.50, foot_y=0.10),
            contact(3, side="right", foot_x=0.50, foot_y=0.90),
        ]

        result = analyze_stride_geometry(contacts, context=self.context)
        self.assertAlmostEqual(
            result["metrics"]["average_step_length_normalized"], 0.0, places=6
        )

    def test_foot_offset_uses_x_axis_fore_aft_not_y(self) -> None:
        # COM directly below the foot in y (no vertical offset possible
        # to confuse with) but offset in x - offset-from-COM must react
        # to the x difference, since it's meant to measure fore-aft
        # landing position relative to COM (braking-distance proxy).
        contacts = alternating_contacts(8)
        shifted = [
            FootContactEvent(
                side=c.side,
                frame_index=c.frame_index,
                timestamp_ms=c.timestamp_ms,
                foot_x=c.foot_x,
                foot_y=c.foot_y,
                com_x=c.foot_x - 0.05,  # every contact lands 0.05 ahead of COM in x
                com_y=c.foot_y,  # com_y == foot_y - zero vertical offset by construction
                toe_x=c.toe_x,
                toe_y=c.toe_y,
                heel_x=c.heel_x,
                heel_y=c.heel_y,
                confidence=c.confidence,
            )
            for c in contacts
        ]

        result = analyze_stride_geometry(shifted, context=self.context)
        offset = result["metrics"]["average_foot_offset_from_com_percent_body_height"]
        self.assertIsNotNone(offset)
        self.assertGreater(offset, 0.0)  # must detect the x-axis offset

    def test_crossover_and_step_width_are_not_computed(self) -> None:
        """
        Replaces the old test_crossover_is_detected, which asserted the
        now-confirmed-buggy Y-axis crossover behavior. The corrected
        module reports these as explicitly unavailable rather than
        computing a value from an axis that cannot represent the
        underlying biomechanical quantity - true mediolateral separation
        is not observable from a single side-view 2D camera.
        """
        contacts = [
            contact(0, side="left", foot_x=0.0, foot_y=0.60, com_y=0.50),
            contact(1, side="right", foot_x=0.5, foot_y=0.40, com_y=0.50),
            contact(2, side="left", foot_x=1.0, foot_y=0.62, com_y=0.50),
            contact(3, side="right", foot_x=1.5, foot_y=0.38, com_y=0.50),
        ]

        result = analyze_stride_geometry(contacts, context=self.context)
        metrics = result["metrics"]

        self.assertIsNone(metrics["crossover_contacts"])
        self.assertIsNone(metrics["crossover_rate_percent"])
        self.assertIsNone(metrics["average_step_width_normalized"])
        self.assertIsNone(metrics["average_step_width_m"])
        self.assertIsNotNone(metrics["lateral_metrics_unavailable_reason"])
        self.assertIn("side-view", metrics["lateral_metrics_unavailable_reason"])

        # And the same explanation must be visible in the module-level
        # limitations list, not just buried in one field.
        self.assertTrue(
            any("side-view" in limitation for limitation in result["limitations"])
        )

    def test_overall_score_excludes_removed_metrics(self) -> None:
        # overall_stride_geometry_score's weights must sum through only
        # the five surviving components (step length, foot placement,
        # symmetry, stability, toe direction) - confirmed indirectly by
        # checking a perfect-on-those-five case can still reach a high
        # score without a crossover/width contribution ever being
        # possible again.
        contacts = alternating_contacts(12)
        result = analyze_stride_geometry(
            contacts, context=self.context, cadence_spm=280.0, horizontal_velocity=2.2
        )
        self.assertGreaterEqual(result["metrics"]["overall_stride_geometry_score"], 90.0)

    # ------------------------------------------------------------------
    # Confidence tests - the corrected compute_geometry_confidence must
    # actually vary with output quality, unlike the old formula (which
    # was a mathematical constant of 100.0 on any real-scale input).
    # ------------------------------------------------------------------

    def test_confidence_is_not_a_constant_100_on_real_scale_input(self) -> None:
        # Real-scale (0-100) confidence values, well below the old
        # clamp-to-1.0 saturation point in every meaningful sense - the
        # old formula would still have reported exactly 100.0 here.
        contacts = alternating_contacts(6, confidence=60.0)
        result = analyze_stride_geometry(contacts, context=self.context)
        self.assertLess(result["metrics"]["confidence"], 100.0)

    def test_confidence_decreases_with_low_sample_count(self) -> None:
        few = alternating_contacts(4, confidence=95.0)
        many = alternating_contacts(24, confidence=95.0)

        few_result = analyze_stride_geometry(few, context=self.context)
        many_result = analyze_stride_geometry(many, context=self.context)

        self.assertLess(
            few_result["metrics"]["confidence"],
            many_result["metrics"]["confidence"],
        )

    def test_confidence_decreases_with_left_right_imbalance(self) -> None:
        balanced = alternating_contacts(20, confidence=90.0)  # 10 left, 10 right

        lopsided = [
            contact(index, side="left", foot_x=index * 0.48, foot_y=0.44, confidence=90.0)
            for index in range(18)
        ] + [
            contact(18, side="right", foot_x=18 * 0.48, foot_y=0.56, confidence=90.0),
            contact(19, side="right", foot_x=19 * 0.48, foot_y=0.56, confidence=90.0),
        ]

        balanced_result = analyze_stride_geometry(balanced, context=self.context)
        lopsided_result = analyze_stride_geometry(lopsided, context=self.context)

        self.assertLess(
            lopsided_result["metrics"]["confidence"],
            balanced_result["metrics"]["confidence"],
        )

    def test_confidence_decreases_with_unstable_geometry(self) -> None:
        stable = alternating_contacts(16, jitter=0.0)
        unstable = alternating_contacts(16, jitter=0.35)  # large step-to-step variation

        stable_result = analyze_stride_geometry(stable, context=self.context)
        unstable_result = analyze_stride_geometry(unstable, context=self.context)

        self.assertLess(
            unstable_result["metrics"]["confidence"],
            stable_result["metrics"]["confidence"],
        )

    def test_confidence_reaches_high_band_only_with_good_data_on_every_factor(self) -> None:
        contacts = alternating_contacts(24, confidence=95.0, jitter=0.0)  # 12/side, stable, high-confidence
        result = analyze_stride_geometry(contacts, context=self.context)
        self.assertGreaterEqual(result["metrics"]["confidence"], 75.0)

    def test_confidence_is_none_only_when_no_contacts_at_all(self) -> None:
        # analyze_stride_geometry itself gates below 4 contacts before
        # confidence is ever computed - this test exercises
        # compute_geometry_confidence directly at its own boundary.
        from app.services.sprint.stride_geometry_scoring import (
            compute_geometry_confidence,
        )

        self.assertIsNone(
            compute_geometry_confidence(
                contacts_used=0,
                left_count=0,
                right_count=0,
                input_confidences_0_100=[],
                geometry_stability_score=None,
            )
        )

    # ------------------------------------------------------------------
    # Edge cases / stress testing (Phase 5)
    # ------------------------------------------------------------------

    def test_exactly_four_contacts_boundary(self) -> None:
        # 4 is the documented hard minimum (< 4 -> insufficient_data).
        # Exactly 4 must succeed, not off-by-one fail.
        contacts = alternating_contacts(4)
        result = analyze_stride_geometry(contacts, context=self.context)
        self.assertEqual(result["status"], "experimental")
        self.assertEqual(result["metrics"]["contacts_used"], 4)

    def test_three_contacts_is_insufficient(self) -> None:
        contacts = alternating_contacts(3)
        result = analyze_stride_geometry(contacts, context=self.context)
        self.assertEqual(result["status"], "insufficient_data")

    def test_all_same_side_contacts_degrades_gracefully(self) -> None:
        # A pathological input (every contact detected as the same side -
        # plausible if the contact detector misclassified side, a known
        # unresolved limitation per §11) must not crash; step-length and
        # symmetry become uncomputable (None), not a fabricated value.
        contacts = [
            contact(index, side="left", foot_x=index * 0.5, foot_y=0.44)
            for index in range(6)
        ]
        result = analyze_stride_geometry(contacts, context=self.context)

        self.assertEqual(result["status"], "experimental")
        metrics = result["metrics"]
        self.assertIsNone(metrics["right_step_length_normalized"])
        self.assertIsNone(metrics["step_length_symmetry_score"])
        self.assertEqual(metrics["right_contacts_used"], 0)
        self.assertEqual(metrics["left_contacts_used"], 6)

    def test_duplicated_contacts_do_not_crash(self) -> None:
        base = alternating_contacts(6)
        duplicated = base + base  # same events twice, e.g. a re-run/merge bug upstream
        result = analyze_stride_geometry(duplicated, context=self.context)
        self.assertEqual(result["status"], "experimental")
        self.assertEqual(result["metrics"]["contacts_used"], 12)

    def test_unordered_and_gapped_timestamps_produce_same_result_as_sorted(self) -> None:
        ordered_contacts = alternating_contacts(10)
        shuffled = [
            ordered_contacts[3], ordered_contacts[0], ordered_contacts[7],
            ordered_contacts[1], ordered_contacts[9], ordered_contacts[2],
            ordered_contacts[8], ordered_contacts[4], ordered_contacts[6],
            ordered_contacts[5],
        ]

        result_a = analyze_stride_geometry(ordered_contacts, context=self.context)
        result_b = analyze_stride_geometry(shuffled, context=self.context)

        self.assertEqual(result_a["metrics"], result_b["metrics"])

    def test_missing_toe_heel_landmarks_omit_toe_direction_not_crash(self) -> None:
        # Built directly with FootContactEvent (not the contact() helper,
        # whose own toe/heel defaults would silently paper over an
        # explicit None) so the missing-landmark case is genuine.
        contacts = [
            FootContactEvent(
                side="left" if index % 2 == 0 else "right",
                frame_index=index,
                timestamp_ms=index * 120,
                foot_x=index * 0.48,
                foot_y=0.44 if index % 2 == 0 else 0.56,
                com_x=index * 0.48 - 0.02,
                com_y=0.50,
                toe_x=None,
                toe_y=None,
                heel_x=None,
                heel_y=None,
                confidence=92.0,
            )
            for index in range(6)
        ]

        result = analyze_stride_geometry(contacts, context=self.context)
        metrics = result["metrics"]

        self.assertEqual(result["status"], "experimental")
        self.assertEqual(metrics["toe_in_contacts"], 0)
        self.assertEqual(metrics["neutral_toe_contacts"], 0)
        self.assertEqual(metrics["toe_out_contacts"], 0)

    def test_missing_context_still_produces_normalized_metrics(self) -> None:
        contacts = alternating_contacts(8)
        empty_context = StrideGeometryContext()  # every field defaults to None

        result = analyze_stride_geometry(contacts, context=empty_context)
        metrics = result["metrics"]

        self.assertIsNotNone(metrics["average_step_length_normalized"])
        self.assertIsNone(metrics["average_step_length_m"])  # no scale supplied
        self.assertIsNone(metrics["normalized_step_length_leg_ratio"])  # no leg length supplied

    def test_low_fps_wide_time_gaps_do_not_break_ordering_or_geometry(self) -> None:
        # Same spatial contacts, but with large, irregular timestamp
        # gaps (simulating a low-fps or gappy clip) - timestamps only
        # affect ordering, never the geometry math itself.
        contacts = [
            contact(0, side="left", foot_x=0.0, foot_y=0.44),
            contact(1, side="right", foot_x=0.48, foot_y=0.56),
            contact(2, side="left", foot_x=0.96, foot_y=0.44),
            contact(3, side="right", foot_x=1.44, foot_y=0.56),
        ]
        gapped = [
            FootContactEvent(
                side=c.side, frame_index=c.frame_index,
                timestamp_ms=c.timestamp_ms * 50,  # huge, irregular gaps
                foot_x=c.foot_x, foot_y=c.foot_y, com_x=c.com_x, com_y=c.com_y,
                toe_x=c.toe_x, toe_y=c.toe_y, heel_x=c.heel_x, heel_y=c.heel_y,
                confidence=c.confidence,
            )
            for c in contacts
        ]

        result = analyze_stride_geometry(gapped, context=self.context)
        self.assertEqual(result["status"], "experimental")
        self.assertAlmostEqual(
            result["metrics"]["average_step_length_normalized"], 0.48, places=6
        )

    def test_athlete_leaving_frame_mid_clip_partial_contacts(self) -> None:
        # Simulates the athlete leaving frame partway through - only the
        # first half of an otherwise-normal sequence is detected. Must
        # still analyze whatever real contacts exist, not require the
        # full sequence.
        contacts = alternating_contacts(14)[:5]  # occlusion cuts off after 5 contacts
        result = analyze_stride_geometry(contacts, context=self.context)
        self.assertEqual(result["status"], "experimental")
        self.assertEqual(result["metrics"]["contacts_used"], 5)

    def test_low_confidence_frames_still_compute_but_lower_confidence(self) -> None:
        high_conf = alternating_contacts(10, confidence=95.0)
        low_conf = alternating_contacts(10, confidence=46.0)  # near the detector's own floor of 45.0

        high_result = analyze_stride_geometry(high_conf, context=self.context)
        low_result = analyze_stride_geometry(low_conf, context=self.context)

        self.assertEqual(low_result["status"], "experimental")  # still computes, doesn't refuse
        self.assertLess(
            low_result["metrics"]["confidence"],
            high_result["metrics"]["confidence"],
        )

    # ------------------------------------------------------------------
    # Real-footage-grounded regression fixture (Phase 4/6). Not a live
    # capture (this test suite must run without a GPU/RTMPose worker,
    # matching every other test in backend/tests/) - a static fixture
    # built from the real per-contact statistics measured against
    # my_sprint_2.mp4 during the correction pass's Phase 4 validation
    # (46 real contacts, cadence 187.5 steps/min, confirmed via direct
    # backend-service investigation, see the correction pass's audit
    # report). Guards against a future regression reintroducing
    # implausible crossover/stability/confidence values on realistic
    # step-length/confidence magnitudes.
    # ------------------------------------------------------------------

    def test_real_footage_grounded_fixture_produces_plausible_output(self) -> None:
        contacts = alternating_contacts(
            46,
            step_x=0.045,  # order-of-magnitude match to the real average_step_length_normalized observed
            confidence=78.0,  # within the real observed confidence range (45-100, prominence-based)
            jitter=0.003,  # modest, realistic step-to-step noise (~7% relative)
        )

        result = analyze_stride_geometry(
            contacts, context=self.context, cadence_spm=187.5
        )
        metrics = result["metrics"]

        self.assertEqual(result["status"], "experimental")
        self.assertEqual(metrics["contacts_used"], 46)
        # No crossover/width claims of any kind - the corrected module's
        # central guarantee for this exact real clip's data shape.
        self.assertIsNone(metrics["crossover_rate_percent"])
        self.assertIsNone(metrics["average_step_width_normalized"])
        # A clean, evenly-alternating fixture should not itself trip the
        # implausibility this pass was built to catch.
        self.assertGreaterEqual(metrics["geometry_stability_score"], 50.0)


if __name__ == "__main__":
    unittest.main()
