# ADR-057: Operations Platform

## Status
Accepted

## Context
AgentSphere needs a professional administrative interface to let users manage, deploy, evaluate, and sandbox multi-tenant conversational and RAG workflows. Directly querying databases or editing text-file configurations in production is error-prone, insecure, and non-collaborative.

## Decision
We implement a high-fidelity Next.js-based **AI Operations Platform**:
* **Enterprise Tech Stack:** Next.js 15 (App Router), React 19, TypeScript, TailwindCSS, shadcn/ui, TanStack Query, and Zustand.
* **Administrative Navigation Shell:** Houses unified sidebars, notifications counters, responsive dark/light theme providers, and dynamic breadcrumbs.

## Consequences
* **Pros:** Professional enterprise administrative interface, rapid setup of agents and templates, and zero direct schema exposures.
* **Cons:** Requires a separate frontend compilation and deployment lifecycle.
