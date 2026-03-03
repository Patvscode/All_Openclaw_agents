# Lessons Learned

## 2026-03-02

### Card-002: Message Priority Tags
- Built a reusable Python module for visual priority tagging
- Supports 3 output formats: ANSI (terminal colors), HTML (web rendering), plain text
- Color scheme: Critical=Red, High=Yellow, Normal=Green, Low=Gray
- Can be integrated into messaging systems for visual priority indication

### Autonomy Engine
- Script has syntax errors in line 24 (`[[: 5\n0:`) - should be investigated
- Chain watchdog also has similar syntax issue in line 8
- These are minor but worth fixing for clean operation