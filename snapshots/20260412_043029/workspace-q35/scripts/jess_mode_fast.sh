#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import json
p='/home/pmello/.openclaw/openclaw.json'
obj=json.load(open(p))
for a in obj.get('agents',{}).get('list',[]):
    if a.get('id')=='q35':
        a['compaction']={
          'mode':'safeguard',
          'reserveTokensFloor':8192,
          'memoryFlush':{
            'enabled':True,
            'softThresholdTokens':6000,
            'systemPrompt':'Session nearing compaction. Store durable memories now.',
            'prompt':'Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store.'
          }
        }
        a['contextPruning']={
          'mode':'cache-ttl',
          'ttl':'45m',
          'keepLastAssistants':4,
          'softTrimRatio':0.25,
          'hardClearRatio':0.45,
          'minPrunableToolChars':20000,
          'softTrim':{'maxChars':3000,'headChars':1200,'tailChars':1200},
          'hardClear':{'enabled':True,'placeholder':'[Old tool result content cleared]'}
        }
open(p,'w').write(json.dumps(obj,indent=2)+'\n')
print('Applied FAST mode for q35')
PY
openclaw gateway restart >/dev/null 2>&1 || true
echo "Jess mode: FAST"
