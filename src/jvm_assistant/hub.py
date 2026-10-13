from __future__ import annotations
import json
from .common import ROOT, UserError

def contract(entity: str=''):
    data=json.loads((ROOT/'skills/jvm-workflow/references/hub-schema.json').read_text())
    if entity:
        if entity not in data['sources']:raise UserError('Choose Team, Clients, Projects, Tasks or Notes')
        data['sources']={entity:data['sources'][entity]}
    else:
        data['sources']={name:{'url':item['url'],'fields':{key:value['type'] for key,value in item['schema'].items()}} for name,item in data['sources'].items()}
    return {**data,'use':'Use the host AI official Notion connector authenticated to the company workspace. Re-fetch live schemas before writes. This local tool does not authenticate to or write Notion.','completion_rule':'Only 상태 == 완료 means completed. 보류 and 중단 are NOT completed, even when grouped as complete.'}
