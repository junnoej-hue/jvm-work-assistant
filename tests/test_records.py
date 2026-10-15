import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from jvm_assistant import records
from jvm_assistant.common import UserError

class RecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name).resolve()
        self.workspace=self.root/'private-work'
        self.config=patch.object(records,'load_config',return_value={'workspace_dir':str(self.workspace)})
        self.config.start()
    def tearDown(self):
        self.config.stop();self.tmp.cleanup()
    def test_save_read_idempotence_and_revisions(self):
        a=records.save('20261015-example','Synthetic record','Draft only. Not sent.')
        self.assertTrue(a['created']);self.assertFalse(a['notion_updated'])
        self.assertEqual(records.read(a['filename'])['content'],'# Synthetic record\n\nDraft only. Not sent.\n')
        self.assertFalse(records.save('20261015-example','Synthetic record','Draft only. Not sent.')['created'])
        b=records.save('20261015-example','Synthetic record','Synthetic revision.')
        self.assertNotEqual(a['filename'],b['filename'])
        self.assertTrue(Path(a['path']).exists());self.assertEqual(len(records.read()['files']),2)
        self.assertEqual(Path(a['path']).stat().st_mode & 0o777,0o600)
        self.assertEqual(Path(a['path']).parent.stat().st_mode & 0o777,0o700)
    def test_reject_path_traversal_and_bad_input(self):
        for bad in ['../out','/tmp/out','a/b','', 'x'*81]:
            with self.assertRaises(UserError):records.save(bad,'Title','Content')
        for bad in ['../settings.json','/tmp/secret','not-a-record.md']:
            with self.assertRaises(UserError):records.read(bad)
        with self.assertRaises(UserError):records.save('valid','bad\ntitle','Body')
        with self.assertRaises(UserError):records.save('valid','Title','x'*500001)
    def test_refuse_git_workspace(self):
        self.workspace.mkdir();(self.workspace/'.git').mkdir()
        with self.assertRaises(UserError):records.save('example','Title','Body')
    def test_refuse_symlink_directory(self):
        target=self.root/'elsewhere';target.mkdir()
        self.workspace.symlink_to(target,target_is_directory=True)
        with self.assertRaises(UserError):records.save('example','Title','Body')
    def test_refuse_symlink_local_subfolder(self):
        self.workspace.mkdir();target=self.root/'elsewhere';target.mkdir()
        (self.workspace/'local').symlink_to(target,target_is_directory=True)
        with self.assertRaises(UserError):records.save('example','Title','Body')
    def test_refuse_symlink_record_and_preserve_target(self):
        a=records.save('example','Title','Body');p=Path(a['path']);p.unlink()
        target=self.root/'target';target.write_text('DO NOT MODIFY')
        p.symlink_to(target)
        with self.assertRaises((OSError,UserError)):records.save('example','Title','Body')
        with self.assertRaises(UserError):records.read(a['filename'])
        self.assertEqual(target.read_text(),'DO NOT MODIFY')
    def test_corruption_is_reported_without_overwrite(self):
        a=records.save('example','Title','Body');p=Path(a['path']);p.write_text('Changed by user')
        with self.assertRaises(UserError):records.read(a['filename'])
        with self.assertRaises(UserError):records.save('example','Title','Body')
        self.assertEqual(p.read_text(),'Changed by user')
    def test_list_bounded_and_no_unknown_files(self):
        for i in range(3):records.save('example'+str(i),'Title','Body')
        (records.records_dir()/'unrelated.md').write_text('not returned')
        r=records.read(limit=2)
        self.assertEqual(len(r['files']),2);self.assertTrue(r['has_more'])
        with self.assertRaises(UserError):records.read(limit=0)
    def test_default_workspace_is_current_users(self):
        with patch.object(records,'load_config',return_value={}),patch.object(records.Path,'home',return_value=self.root):
            a=records.save('example','Title','Body')
            self.assertTrue(a['path'].startswith(str(self.root/'Documents/JvM Workspace/local/private-work-history')))

if __name__=='__main__':unittest.main()
