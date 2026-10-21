import unittest
import contextlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import make_campaign as m
from scheduler import AdmissionError


class CampaignTests(unittest.TestCase):
    def test_exact_count_and_dependencies(self):
        result=m.build()
        self.assertEqual(len(result['jobs']),41)
        self.assertEqual(result['maximum_raw_attempt_units'],49)
        self.assertEqual(result['science_jobs_accounting']['logical_slots'],52)
        self.assertEqual(sum(j.get('kind')=='external_complete' for j in result['jobs']),3)
        self.assertEqual(sum(j.get('variant')=='fd_half' for j in result['jobs']),19)
        self.assertEqual(sum(j.get('raw_attempt_units',0) for j in result['jobs']),49)
        for job in result['jobs']:
            if job.get('variant')=='fd_half':
                self.assertIn('--base-job',job['command'])
                self.assertTrue(job['dependencies'])

    def test_k_and_i_paths_remain_separate(self):
        jobs=m.build()['jobs']
        k=next(j for j in jobs if j.get('lane')=='K')
        i=next(j for j in jobs if j.get('lane')=='I')
        self.assertTrue(any('${k_checkout}/research/' in a for a in k['command']))
        self.assertTrue(any('${i_checkout}/research/' in a for a in i['command']))
        self.assertIn('--c21i-unit',k['command'])

    def test_original_g_is_one_container_with_twelve_units(self):
        g=next(j for j in m.build()['jobs'] if j['kind']=='standalone_g_campaign')
        self.assertEqual(g['raw_attempt_units'],12)
        self.assertEqual(g['timeout_seconds'],3660)
        self.assertEqual(g['dependencies'],[])
        self.assertNotIn('--job',g['command'])

    def test_path_repair_is_prelaunch_identity_difference(self):
        old={'input_identity':{'manifest_path':'/old/g/EXECUTION_MANIFEST.json'},
             'bridge_identity':{'path':'/old/bridge'},'native_identity':{'path':'/old/native'}}
        same={'I_G_UNIT':'/old/g','BRIDGE':'/old/bridge','NATIVE':'/old/native'}
        self.assertEqual(m.original_h_context_changes(old,same),[])
        same['I_G_UNIT']='/new/g'
        differences=m.original_h_context_changes(old,same)
        self.assertEqual(len(differences),1)
        self.assertEqual(differences[0]['field'],'input_identity.manifest_path')

    def test_missing_real_bindings_fail_before_execution(self):
        with self.assertRaises(AdmissionError):m.build({'python':'relative'})

    def bound_fixture(self, directory, *, changed=False, relocated=False):
        """Preverified admission doubles isolate matrix wiring; no Git/native run."""
        root=Path(directory)
        binding={key:str(root/key) for key in ['python','i_checkout','k_checkout',
            'bridge_binary','bridge_build_receipt','native_binary','h_publication_receipt',
            'i_publication_receipt','k_publication_receipt','native_return_evidence']}
        Path(binding['k_publication_receipt']).write_text(json.dumps({'status':'PUBLISHED','content_commit':'a'*40}))
        values=m.paths(binding)
        record={'input_identity':{'manifest_path':str(Path(values['I_G_UNIT'])/'EXECUTION_MANIFEST.json')},
            'bridge_identity':{'path':values['BRIDGE']},'native_identity':{'path':values['NATIVE']}}
        if relocated:record['bridge_identity']['path']=str(root/'old_bridge')
        inventory=m.read_json(m.HERE/'BACKLOG_INVENTORY.json')
        old=next(j for j in inventory['completed_external_nodes'] if j['job_id'].startswith('H_'))
        rp=Path(binding['native_return_evidence'])/old['original_return_directory_name']/'JOB_RECEIPT.json'
        rp.parent.mkdir(parents=True);rp.write_text(json.dumps(record))
        admission={'native':{'sha256':'b'*64 if changed else m.KNOWN_NATIVE,'bytes':1},
            'bridge':{'sha256':m.KNOWN_BRIDGE,'bytes':1},'publication':{'test_double':True}}
        with contextlib.ExitStack() as stack:
            for name in ['verify_checkout','verify_external']:stack.enter_context(patch.object(m,name))
            stack.enter_context(patch.object(m,'closure_records',return_value=[]))
            stack.enter_context(patch.object(m,'verify_publication_and_build',return_value=admission))
            return m.build(binding)

    def test_matching_bound_context_adds_zero_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=self.bound_fixture(tmp)
        self.assertEqual(result['maximum_raw_attempt_units'],49)
        self.assertEqual(result['context_repair_jobs'],[])
        self.assertEqual(len(result['jobs']),41)
        self.assertTrue(all(j['current_context_compatible'] for j in result['jobs'] if j['kind']=='external_complete'))

    def test_path_only_adds_one_h_control_only_for_pending_fd(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=self.bound_fixture(tmp,relocated=True)
        self.assertEqual(result['maximum_raw_attempt_units'],50)
        self.assertEqual(len(result['context_repair_jobs']),1)
        control=result['context_repair_jobs'][0]['job_id']
        self.assertEqual(control,'H_common_ic_vigilode_rodas5p_base_context_control')
        children=[j for j in result['jobs'] if control in j.get('dependencies',[])]
        self.assertEqual([j['job_id'] for j in children],['H_common_ic_vigilode_rodas5p_fd_half'])
        self.assertTrue(all(j['current_context_compatible'] for j in result['jobs'] if j['kind']=='external_complete'))

    def test_valid_changed_build_adds_three_controls_not_four(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=self.bound_fixture(tmp,changed=True,relocated=True)
        self.assertEqual(result['maximum_raw_attempt_units'],52)
        self.assertEqual(len(result['context_repair_jobs']),3)
        self.assertEqual(result['science_jobs_accounting']['top_level_pending_processes'],41)
        old=[j for j in result['jobs'] if j['kind']=='external_complete']
        self.assertTrue(all(j['historical_only'] and not j['current_context_compatible'] for j in old))
        fd=next(j for j in result['jobs'] if j['job_id']=='I_common_ic_vigilode_rodas5p_vectorized_fd_half_context_control')
        self.assertEqual(fd['dependencies'],['I_common_ic_vigilode_rodas5p_vectorized_base_context_control'])
        self.assertIn('${job:I_common_ic_vigilode_rodas5p_vectorized_base_context_control}',fd['command'])
        self.assertFalse(any(dep in {j['job_id'] for j in old} for j in result['jobs'] for dep in j.get('dependencies',[])))

    def test_cross_lane_comparison_never_becomes_hard_gate(self):
        for job in m.build()['jobs']:
            if job.get('lane') in ('I','K') and job.get('variant')=='base':
                self.assertEqual(job['dependencies'],[])
                self.assertTrue(job['comparison_dependency_is_soft'])

    def test_path_aliases_do_not_create_repair(self):
        old={'input_identity':{'manifest_path':'/tmp/a/../g/EXECUTION_MANIFEST.json'},
             'bridge_identity':{'path':'/tmp/./bridge'},'native_identity':{'path':'/tmp/native'}}
        current={'I_G_UNIT':'/tmp/g/','BRIDGE':'/tmp/bridge','NATIVE':'/tmp/x/../native'}
        self.assertEqual(m.original_h_context_changes(old,current),[])

    def test_dirty_manifest_is_not_its_own_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);mp=root/'i/research'/m.H/'EXECUTION_MANIFEST.json'
            mp.parent.mkdir(parents=True);mp.write_text('{"runtime_files":{}}')
            receipt=root/'published.json';receipt.write_text('{}')
            binding={'i_checkout':str(root/'i'),'k_checkout':str(root/'k'),'k_publication_receipt':str(receipt)}
            with self.assertRaisesRegex(AdmissionError,'PINNED_MANIFEST_REQUIRED'):
                m.closure_records(binding,m.paths(binding))


if __name__=='__main__':unittest.main(verbosity=2)
