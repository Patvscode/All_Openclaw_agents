# JESS - Lessons Learned

## 2026-03-04

### Browser Push Notifications Implementation
- **What worked**: Notification API is straightforward to implement with basic permission flow
- **Rate limiting**: 30s per channel prevents notification spam while keeping alerts timely
- **Sound**: Web Audio API works well for simple beeps, no external assets needed
- **Mute UX**: Inline mute icons on channels are intuitive - users expect this pattern from Slack/Discord
- **Takeaway**: Keep it simple - don't overengineer. Basic notification flow + per-channel controls is sufficient for MVP

### Comms Server Architecture
- **API endpoint reuse**: `/api/search` was already implemented - always check existing code before building
- **File-based storage**: Simple JSON files work well for comms data, no database needed
- **Port consistency**: Use 8096 consistently (was 8097 in some places - fixed by codex)

### Autonomy Loop
- **Chain watchdog**: Essential for keeping work loop alive across session gaps
- **Board discipline**: Always grab a card when free, complete before moving on
- **Documentation**: Update memory files daily for continuity
- **Takeaway**: Small consistent progress > sporadic bursts

### Notification Edge Cases
- **Permission denied**: Handle gracefully with visible button to retry
- **Background tab**: Notifications work even when tab is not focused
- **Rate limiting**: Prevents notification fatigue while maintaining visibility
- **Future enhancement**: Per-agent mute, notification scheduling, rich notifications with actions

## 2026-03-05

### Pinned Messages Feature
- **User feedback pattern**: When a card is vague, propose a concrete implementation plan and wait for feedback
- **Board communication**: Use `board discuss` to post plans and get input before starting work
- **Chain watchdog**: Restarted twice in ~12min - pattern noted for investigation (potential session instability)
- **Takeaway**: Document implementation plans clearly with UI design, backend changes, and file locations