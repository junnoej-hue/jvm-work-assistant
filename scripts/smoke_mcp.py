"""No credentials, network or business data. Exercise the real stdio protocol."""
import asyncio
import json
import os
import tempfile
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    root=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='jvm-smoke-') as tmp:
        (Path(tmp)/'settings.json').write_text(json.dumps({'workspace_dir':str(Path(tmp).resolve()/'private-work')}))
        params=StdioServerParameters(command='/bin/bash',args=[str(root/'scripts/run-mcp.sh')],env={**os.environ,'JVM_ASSISTANT_STATE_DIR':tmp})
        async with stdio_client(params) as (r,w):
            async with ClientSession(r,w) as session:
                await session.initialize()
                tools=(await session.list_tools()).tools
                expected={'jvm_workflow_guide','jvm_hub_schema','jvm_mail_search','jvm_mail_read','jvm_webex_rooms','jvm_webex_messages','jvm_webex_read_message','jvm_save_private_record','jvm_read_private_record'}
                assert {t.name for t in tools}==expected
                assert all(t.annotations.readOnlyHint for t in tools if t.name!='jvm_save_private_record')
                writer=next(t for t in tools if t.name=='jvm_save_private_record')
                assert not writer.annotations.readOnlyHint and not writer.annotations.openWorldHint
                schema=await session.call_tool('jvm_hub_schema',{})
                assert not schema.isError and 'b2c35e9c-b9ee-83e1-82c1-018feed05f4b' in str(schema)
                denied=await session.call_tool('jvm_webex_messages',{'room_id':'not_allowed'})
                assert 'Room is not allowed' in str(denied)
                invalid=await session.call_tool('jvm_mail_search',{})
                assert 'Provide a subject' in str(invalid)
                guide=await session.call_tool('jvm_workflow_guide',{})
                assert 'JvM 업무 도우미' in str(guide)
                saved=await session.call_tool('jvm_save_private_record',{'record_id':'smoke-example','title':'Synthetic test','content':'Private draft only.'})
                data=json.loads(saved.content[0].text)
                assert data['ok'] and not data['notion_updated']
                read=await session.call_tool('jvm_read_private_record',{'filename':data['filename']})
                assert 'Private draft only.' in str(read)
                print(json.dumps({'stdio':'passed','tool_count':len(tools),'safe_calls':6,'credentials_used':False,'external_network':False}))

asyncio.run(main())
