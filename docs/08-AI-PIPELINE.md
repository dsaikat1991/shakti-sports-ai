# 08 — AI Pipeline

Version: 1.0

Status: Planning

Project: Shakti Sports AI

AI Stack

- Python
- MediaPipe
- OpenCV
- Firebase Storage
- Firebase Functions
- Firestore

Related Documents

- 04-DATABASE.md
- 05-ARCHITECTURE.md
- 09-API.md

---

# 1. Purpose

The AI Pipeline transforms an athlete's uploaded performance video into an objective, structured, and interpretable performance report.

The AI system is designed to assist coaches and scouts by providing standardized performance insights. It is not intended to replace professional coaching or human judgment.

---

# 2. AI Philosophy

The AI engine should be:

- Explainable
- Objective
- Consistent
- Fair
- Transparent
- Continuously improvable

Every AI-generated score must be supported by measurable observations.

---

# 3. End-to-End Pipeline

```

Athlete Uploads Video
│
▼

Firebase Storage

│

▼

Video Validation

│

▼

Frame Extraction

│

▼

Pose Estimation

│

▼

Movement Tracking

│

▼

Biomechanics Engine

│

▼

Performance Metrics

│

▼

AI Scoring Engine

│

▼

Report Generator

│

▼

Firestore

│

▼

Athlete Dashboard

```

---

# 4. Upload Stage

Accepted Formats

- MP4
- MOV

Maximum Size

500 MB

Maximum Duration

60 seconds

Preferred Resolution

1080p

Minimum Resolution

720p

Validation

- Supported format
- File size
- Duration
- Resolution
- Corruption check

Invalid uploads are rejected before processing.

---

# 5. Firebase Storage

Video location

```

videos/{uid}/{videoId}.mp4

```

Metadata stored in Firestore

```

videos/{videoId}

```

Status

```

uploaded

processing

completed

failed

```

---

# 6. AI Trigger

A successful upload triggers processing.

Trigger

Firebase Function

Future

Cloud Tasks

Pub/Sub Queue

The frontend never directly starts AI processing.

---

# 7. Video Preprocessing

The preprocessing stage performs:

Frame extraction

Frame normalization

Rotation correction

Resolution normalization

Frame sampling

Noise reduction

The objective is to provide clean input to the AI engine.

---

# 8. Frame Extraction

Target FPS

30 FPS

Future

Dynamic frame sampling based on event type.

Frames are stored temporarily during processing.

---

# 9. Pose Estimation

Technology

MediaPipe Pose

Keypoints

33 body landmarks

Examples

Head

Shoulders

Elbows

Wrists

Hip

Knees

Ankles

Heel

Foot Index

Output

Joint coordinates

Visibility score

Confidence score

---

# 10. Movement Tracking

The engine tracks movement across frames.

Examples

Running direction

Body center

Joint trajectories

Velocity

Acceleration

Stride cycles

This data forms the basis for biomechanics analysis.

---

# 11. Biomechanics Engine

The biomechanics engine derives meaningful measurements.

Examples

Stride Length

Stride Frequency

Ground Contact Time

Hip Stability

Torso Angle

Arm Swing

Knee Lift

Foot Strike Pattern

Balance

Posture

---

# 12. Event-Specific Analysis

Sprint

Acceleration

Maximum Velocity

Stride

Posture

Reaction

Long Jump

Run-up

Take-off Angle

Flight Path

Landing

High Jump

Approach

Take-off

Body Clearance

Landing

Each event has a dedicated evaluation model.

---

# 13. Performance Metrics

The AI generates standardized metrics.

Examples

Speed

Acceleration

Technique

Balance

Posture

Consistency

Reaction

Efficiency

Mobility

Power

These metrics become reusable across reports.

---

# 14. AI Scoring Engine

Each metric receives a normalized score.

Range

0–100

Example

Overall Score

92

Technique

90

Balance

88

Acceleration

94

Confidence

96

Scores are weighted based on event type.

---

# 15. Confidence Score

Every report includes an AI confidence score.

Factors

Video quality

Lighting

Occlusion

Pose detection quality

Frame consistency

The confidence score informs the user how reliable the analysis is.

---

# 16. Recommendation Engine

The AI generates coaching recommendations.

Example

Increase knee drive.

Improve torso stability.

Reduce lateral movement.

Increase stride frequency.

Recommendations are educational rather than prescriptive.

---

# 17. Report Generator

The report includes:

Athlete information

Video metadata

Performance summary

Metric breakdown

Strengths

Areas for improvement

Confidence score

AI disclaimer

Timestamp

Model version

---

# 18. Report Storage

Reports are stored in Firestore.

```

reports/{reportId}

```

The athlete profile stores only a reference to the latest report.

Historical reports remain available.

---

# 19. Report Versioning

Every report records:

AI model version

Processing version

Timestamp

Future model improvements must not overwrite historical reports.

---

# 20. Error Handling

Possible failures

Unsupported format

Corrupt video

Low confidence

Pose detection failure

Timeout

Each failure receives a human-readable message.

---

# 21. Processing Status

States

Uploaded

Queued

Processing

Analyzing

Generating Report

Completed

Failed

These statuses are displayed in the athlete dashboard.

---

# 22. Future Human Review

Future versions may allow certified coaches to review AI reports.

Coach Review

↓

Coach Comments

↓

Verified Report

This creates a hybrid AI + human workflow.

---

# 23. Benchmarking

Future AI models will compare performance against:

Age group

Gender

Region

National average

Elite benchmark

The athlete receives contextual insights rather than isolated scores.

---

# 24. AI Learning Strategy

The MVP uses rule-based analysis and computer vision.

Future versions may incorporate:

Machine Learning

Deep Learning

Video classification

Predictive performance models

The system should remain modular to accommodate new models.

---

# 25. Explainability

Every score should be explainable.

Example

Technique Score: 88

Reason:

Stable torso

Consistent stride

Good knee lift

Minor arm swing asymmetry

Avoid "black-box" outputs wherever possible.

---

# 26. Privacy

Videos remain private by default.

Athletes choose whether to make reports publicly shareable.

AI processing complies with platform privacy policies.

---

# 27. Scalability

The AI pipeline should support:

Parallel processing

Queued workloads

GPU acceleration

Cloud-based workers

Multiple AI models

Future sports

---

# 28. Monitoring

Track

Processing time

Failure rate

Average confidence

Queue length

Average report generation time

Model accuracy

These metrics help improve system performance.

---

# 29. Future AI Roadmap

Phase 1

Sprint Analysis

Phase 2

Jump Events

Phase 3

Throwing Events

Phase 4

Team Sports

Phase 5

Custom ML Models

Phase 6

Predictive Talent Index

---

# 30. AI Principles

The AI exists to assist—not replace—human expertise.

Its role is to:

- Standardize analysis
- Improve accessibility
- Accelerate talent discovery
- Support evidence-based coaching

Human judgment remains essential.

---

# 31. Final Principle

Every AI decision should increase trust.

If the AI cannot confidently evaluate a performance, it should communicate uncertainty rather than provide misleading precision.

Shakti Sports AI is built on the belief that technology should expand opportunity while remaining transparent, responsible, and fair.