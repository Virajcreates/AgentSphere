# Phase 5 — Voice AI with Pipecat

## Objectives

Integrate Pipecat for voice call orchestration. Implement STT (Deepgram), TTS (ElevenLabs), and WebRTC transport. The voice transport calls the same Shared AI Core as chat — no duplicate logic.

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| STT Provider Port | `STTProvider(Protocol)` — async `transcribe()` streaming and single-utterance |
| Deepgram STT Implementation | Streaming speech-to-text via WebSocket |
| TTS Provider Port | `TTSProvider(Protocol)` — async `synthesize()` streaming and single-utterance |
| ElevenLabs TTS Implementation | Text-to-speech via streaming REST or WebSocket |
| Pipecat Pipeline Setup | AudioInput → VAD → STT → AICoreService → TTS → AudioOutput |
| AICoreService (Pipecat) | Pipecat service bridge that calls Shared AI Core gRPC |
| WebRTC Handler | WebRTC connection management via Daily, LiveKit, or direct |
| Voice Call Lifecycle | Start call, manage session, end call, persist conversation |
| Voice Transport API | `POST /api/v1/calls` (initiate), `POST /api/v1/calls/{id}/end` |
| Turn-Based Processing | Each utterance triggers the same AI workflow as a chat message |
| Interruption Handling | Customer speech during TTS → stop TTS → process new utterance |
| Unit Tests | STT/TTS abstractions, Pipecat pipeline configuration, call lifecycle |
| Integration Tests | End-to-end voice call with mocked STT/TTS |

## Dependencies

- Phase 1 (DB, auth, middleware)
- Phase 2 (Shared AI Core for all business logic)
- Phase 4 (integration tools for voice-eligible actions)
- `pipecat-ai` framework
- Deepgram API key (STT)
- ElevenLabs API key (TTS)
- WebRTC infrastructure (Daily, LiveKit, or custom TURN server)

## Risks

| Risk | Mitigation |
|------|------------|
| Real-time audio latency | Keep Pipecat pipeline on same host; use WebRTC instead of SIP relay |
| Pipecat API instability | Pin pipecat-ai version; isolate in voice transport layer |
| Provider dependency | Abstract STT/TTS behind ports; Deepgram and ElevenLabs are initial only |
| Audio quality degraded by network | Implement adaptive bitrate; fallback to audio-only WebRTC |

## Acceptance Criteria

- [ ] STT correctly transcribes a test audio file to text
- [ ] TTS correctly synthesizes text to audio in the configured voice
- [ ] Pipecat pipeline starts, processes one turn, and shuts down
- [ ] Voice turn triggers the same LangGraph workflow as a chat message
- [ ] Customer can interrupt and the system responds to the new utterance
- [ ] Call conversation is persisted in the same `conversation` + `message` tables
- [ ] Voice transport never contains business logic — all decisions in AI Core