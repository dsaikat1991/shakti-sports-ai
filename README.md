# Shakti Sports AI

AI-powered athlete talent discovery platform built for India.

## Structure

- `frontend/` → React + Vite + Tailwind + Supabase (auth/storage/DB)
- `backend/` → FastAPI backend, pose estimation, and biomechanics analysis (see `backend/README` structure in `docs/ENGINEERING_HANDOFF.md` §2 for the full tree)
- `backend/rtmpose_worker/` → separate GPU-backed pose-inference microservice
- `supabase/migrations/` → hand-run SQL migrations (see `docs/ENGINEERING_HANDOFF.md` §5)
- `docs/` → engineering handoff and workflow documentation

`server/`, `ai-engine/`, `datasets/`, and `models/` are empty placeholders left over from the project's original scaffolding - the real backend and pose-estimation code lives entirely under `backend/`. See `docs/ENGINEERING_HANDOFF.md` for the authoritative, continuously-updated technical record, including which subsystems are actually live versus experimental or unwired.

## Product & design

See `docs/DESIGN_BIBLE.md` for the approved product voice, design tokens, and UX principles every frontend screen should inherit - and for a currently-unresolved finding that the public marketing homepage overstates the product's real capabilities (§9 of that file). That gap should be closed before any further marketing copy is written.