# 06 — Design System

Version: 1.0

Status: Planning

Project: Shakti Sports AI

---

# 1. Purpose

The Design System defines the visual language of Shakti Sports AI.

Its purpose is to ensure every screen, component, animation, and interaction follows a consistent, scalable design philosophy.

The design system should support:

- Marketing website
- Athlete portal
- Coach dashboard
- Scout dashboard
- Admin console
- Future mobile applications

---

# 2. Design Philosophy

Our design is guided by three principles.

## Intelligent

The interface should feel modern, data-driven, and trustworthy.

## Minimal

Every element must have a purpose.

Avoid clutter.

## Inspiring

Athletes should feel motivated, confident, and optimistic while using the platform.

---

# 3. Visual Personality

The visual identity combines:

Apple
+
Stripe
+
Linear
+
Modern Sports Technology

Characteristics:

- Premium
- Calm
- Professional
- High contrast
- Minimal
- Fast
- Clean

---

# 4. Color Philosophy

Every color has meaning.

## Cyan

AI

Analytics

Technology

Discovery

## Gold

Achievement

Awards

Verified Talent

Success

## Green

Completed

Healthy

Positive

## Red

Errors

Rejected

Critical

## Purple

Innovation

Future Features

Premium Experiences

---

# 5. Primary Palette

Primary

#22D3EE

Hover

#06B6D4

Dark

#0891B2

Background

#050816

Surface

#0B1224

Card

#121826

Glass

rgba(255,255,255,0.05)

Border

rgba(255,255,255,0.10)

---

# 6. Typography

Primary Font

Inter

Fallback

system-ui

Headings

Weight

700–900

Body

400–500

Buttons

600

---

# 7. Typography Scale

Display

72px

Hero

60px

H1

48px

H2

36px

H3

30px

H4

24px

Body Large

20px

Body

16px

Small

14px

Caption

12px

---

# 8. Spacing System

Base Unit

8px

Scale

8

16

24

32

40

48

64

96

128

Never invent spacing values outside the system unless necessary.

---

# 9. Border Radius

Small

8px

Medium

12px

Large

20px

Card

24px

Hero Cards

32px

Pill

999px

---

# 10. Shadows

Soft

Cards

Medium

Hover

Strong

Hero

Glow

Cyan AI Glow

Gold Achievement Glow

---

# 11. Glassmorphism

Background

5% white

Blur

20px

Border

10% white

Shadow

Soft cyan

Opacity should never exceed 12%.

---

# 12. Icons

Library

Lucide React

Sizes

16

20

24

32

48

Default Stroke

2

---

# 13. Buttons

Primary

Filled Cyan

Secondary

Outline

Ghost

Transparent

Danger

Red

Success

Green

Buttons should animate subtly on hover.

---

# 14. Cards

Every card should include:

Padding

Rounded corners

Glass background

Soft border

Hover elevation

Optional glow

Cards should never appear flat.

---

# 15. Forms

Large inputs

Visible labels

Helpful validation

Clear error messages

Accessible focus states

---

# 16. Animations

Library

Framer Motion

Entrance

Fade Up

Fade Left

Fade Right

Scale

Hover

Lift

Glow

Tilt

Loading

Pulse

Skeleton

Progress

Animations must communicate purpose.

Avoid decorative motion.

---

# 17. Responsive Breakpoints

Mobile

<640px

Tablet

640–1023px

Laptop

1024–1439px

Desktop

1440px+

Ultra-wide

1920px+

Design mobile first.

---

# 18. Layout Grid

Container

Max Width

1280px

Section Padding

96px

Content Gap

32px

Card Gap

24px

---

# 19. Accessibility

Minimum contrast

WCAG AA

Keyboard navigation

Required

Focus indicators

Required

Touch targets

Minimum 44px

---

# 20. Data Visualization

Charts

Minimal

Dark background

Cyan highlights

Simple legends

Avoid unnecessary decoration.

---

# 21. Dashboard Design

Every dashboard should contain:

Overview

Quick Actions

Recent Activity

Performance Cards

Charts

Notifications

The dashboard should prioritize clarity over density.

---

# 22. Empty States

Every empty screen should include:

Illustration

Helpful message

Primary CTA

Example:

"No reports yet."

Upload your first performance video.

---

# 23. Loading States

Skeleton loading preferred.

Avoid spinners unless waiting exceeds two seconds.

---

# 24. Motion Timing

Fast

150ms

Normal

250ms

Slow

400ms

Page Transition

500ms

---

# 25. Sound

No automatic sounds.

Future:

Optional notification sounds.

---

# 26. Mobile Principles

One-handed usage.

Large tap targets.

Bottom actions where appropriate.

Fast loading.

Offline resilience where possible.

---

# 27. Design Tokens

Every visual property should map to reusable tokens.

Example:

Primary Color

Border Radius

Shadow

Spacing

Typography

These tokens should later be implemented in Tailwind configuration.

---

# 28. Future Expansion

The design system should support:

Native Mobile Apps

Coach Tablets

Scout Dashboards

Large Desktop Analytics

Federation Portals

Without redesigning the visual language.

---

# 29. Final Principle

The interface should never make an athlete feel overwhelmed.

It should make them feel:

"I can do this."

Every screen should reinforce confidence, trust, and opportunity.