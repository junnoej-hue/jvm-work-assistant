import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from jvm_assistant.common import ROOT
spec=importlib.util.spec_from_file_location('connect_client',ROOT/'scripts/connect_client.py')
connect=importlib.util.module_from_spec(spec);spec.loader.exec_module(connect)

class InstallTests(unittest.TestCase):
    def test_claude_preserves_settings_and_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'config.json';original={'theme':'dark','mcpServers':{'existing':{'command':'kept'}}}
            p.write_text(json.dumps(original))
            self.assertTrue(connect.merge_claude(p))
            result=json.loads(p.read_text());self.assertEqual(result['theme'],'dark');self.assertEqual(result['mcpServers']['existing'],original['mcpServers']['existing'])
            backups=list(p.parent.glob('*.jvm-backup-*'));self.assertEqual(len(backups),1)
            self.assertEqual(json.loads(backups[0].read_text()),original)
            self.assertFalse(connect.merge_claude(p));self.assertEqual(len(list(p.parent.glob('*.jvm-backup-*'))),1)
    def test_claude_existing_different_entry_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'config.json';body='{"mcpServers":{"jvm-work-assistant":{"command":"other"}}}';p.write_text(body)
            with self.assertRaises(ValueError):connect.merge_claude(p)
            self.assertEqual(p.read_text(),body)
    def test_broken_config_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'config.json';p.write_text('{bad')
            with self.assertRaises(ValueError):connect.merge_claude(p)
            self.assertEqual(p.read_text(),'{bad')
    def test_version_manifests(self):
        root=json.loads((ROOT/'plugin.json').read_text());compat=json.loads((ROOT/'.codex-plugin/plugin.json').read_text())
        self.assertEqual(root['name'],compat['name']);self.assertEqual(root['version'],compat['version'])
        self.assertLessEqual(len(root['extensions']['com.openai']['interface']['shortDescription']),30)
        mcp=json.loads((ROOT/'mcp.json').read_text());self.assertEqual(mcp['mcpServers']['jvm-work-assistant']['args'],['${PLUGIN_ROOT}/scripts/run-mcp.sh'])

if __name__=='__main__':unittest.main()
