import csv, json, math, tempfile, unittest, zipfile
from pathlib import Path
import numpy as np
import phys14_compete as m

class TestPhysicalEventNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent=m.ROOT/'sources/PR138_ORIGINAL_SOURCE.zip'
        cls.nist_path=m.ROOT/'nist_h_2p_cross_sections.csv'
        cls.phys13,cls.original,cls.shah,cls.parent_result=m.load_parent(cls.parent)
        cls.rows,cls.en,cls.be=m.load_nist(cls.nist_path)
        with (m.ROOT/'results/SOURCE_ATOM_NIST_SHAH_CROSSWALK.csv').open(newline='') as f:
            cls.micro=list(csv.DictReader(f))
        with (m.ROOT/'results/TIME_TOTAL_COMPETITION.csv').open(newline='') as f:
            cls.tot=list(csv.DictReader(f))
        cls.result=json.loads((m.ROOT/'results/RESULT.json').read_text())
    def test_parent_sha(self): self.assertEqual(m.sha(self.parent.read_bytes()),m.PARENT_SHA)
    def test_original_owner_6400(self): self.assertEqual(sum(len(x['energy']) for x in self.original[2]),6400)
    def test_nist_sha(self): self.assertEqual(m.sha(self.nist_path.read_bytes()),m.NIST_CSV_SHA)
    def test_nist_source_points(self):self.assertEqual((len(self.en),self.en[0],self.en[-1]),(12,11.,21.))
    def test_nist_units(self):self.assertAlmostEqual(m.NIST_SIGMA_UNIT,1e-20)
    def test_nist_be_positive(self):self.assertTrue(np.all(self.be>0))
    def test_nist_ccc_comparison(self):
        with (m.ROOT/'results/NIST_BE_VS_CCC_CROSSCHECK.csv').open(newline='') as f: c=list(csv.DictReader(f))
        self.assertEqual(len(c),4)
        self.assertTrue(all(abs(float(x['BE_div_CCC'])-1)<0.15 for x in c))
    def test_source_max_e(self):self.assertAlmostEqual(self.result['max_primary_e_eV'],20.99)
    def test_source_coverage(self):self.assertEqual(len(self.micro),6400)
    def test_h_origin_exclusion(self):self.assertTrue(all(x['NIST_2p_table_covered']=='0' for x in self.micro if x['source']=='H'))
    def test_source_channel_classes(self):self.assertEqual(sum(self.result['source_census'].values()),6400)
    def test_double2p_energetic_support(self):self.assertEqual(self.result['double_2p_energy_atoms'],192)
    def test_h_impact_after_2p_unavailable(self):self.assertLess(self.result['max_primary_e_eV']-m.E_LYA,13.6)
    def test_2p_after_h_impact_unavailable(self):self.assertLess(self.result['max_primary_e_eV']-13.6,m.E_LYA)
    def test_stage_event_count(self):self.assertEqual(len(self.tot),27)
    def test_nonnegative_events(self):
        keys=['H_ion_first_inelastic_measured_overlap_m3','H_2p_first_inelastic_measured_overlap_m3','H_ion_no_exc_measured_overlap_m3']
        self.assertTrue(all(float(r[k])>=0 for r in self.tot for k in keys))
    def test_ion_competition_monotone(self):
        self.assertTrue(all(float(r['H_ion_no_exc_measured_overlap_m3'])+1e-70>=float(r['H_ion_first_inelastic_measured_overlap_m3']) for r in self.tot))
    def test_energy_resolved_budget(self):
        for r in self.tot:
            ion=float(r['H_ion_first_inelastic_measured_overlap_m3']);exc=float(r['H_2p_first_inelastic_measured_overlap_m3'])
            self.assertLessEqual(abs(float(r['secondary_H_binding_energy_J_m3'])-ion*13.6*m.EV_J),1e-64)
            self.assertLessEqual(abs(float(r['Lya_2p_first_event_candidate_energy_J_m3'])-exc*m.E_LYA*m.EV_J),1e-64)
    def test_parent_27_firstabs_parity(self):
        prefix='research/cr_phys13_shah1987_experiment_20261030/results/TIME_TOTAL_OBSERVED_COVERAGE.csv'
        with zipfile.ZipFile(self.parent) as z: parent_rows=list(csv.DictReader(z.read(prefix).decode().splitlines()))
        self.assertEqual(len(parent_rows),27)
        for a,b in zip(parent_rows,self.tot):
            self.assertEqual((a['observation_s'],a['birth_policy']),(b['observation_s'],b['birth_policy']))
            self.assertTrue(math.isclose(float(a['first_H_target_m3']),float(b['first_H_photoabsorption_m3']),rel_tol=2e-14,abs_tol=1e-70))
            self.assertTrue(math.isclose(float(a['Shah_central_observed_coverage_second_m3']),float(b['H_ion_no_exc_measured_overlap_m3']),rel_tol=2e-14,abs_tol=1e-70))
    def test_two_event_vacuum(self):
        p=m.second_first_event(np.array([1.e-10]),np.array([1e-10]),np.array([0.]),np.array([0.]),1e8)
        self.assertEqual(tuple(float(x[0]) for x in p),(0.,0.))
    def test_two_event_no_time(self):
        a,b=m.second_first_event(np.array([1.e-10]),np.array([1e-10]),np.array([1e-11]),np.array([2e-11]),0.)
        self.assertEqual((float(a[0]),float(b[0])),(0.,0.))
    def test_branch_proportionality(self):
        a,b=m.second_first_event(np.array([1e-12]),np.array([4e-12]),np.array([3e-13]),np.array([6e-13]),1e9)
        self.assertAlmostEqual(float(b[0]/a[0]),2.,places=12)
    def test_short_clock_two_event_scaling(self):
        kH=3.e-12;K=4.e-12;nu1=1.e-12;nu2=2.e-12;dt=1e4
        a,b=m.second_first_event(np.array([kH]),np.array([K]),np.array([nu1]),np.array([nu2]),dt)
        self.assertTrue(math.isclose(a[0],0.5*kH*nu1*dt**2,rel_tol=1e-7))
    def test_nist_tampering_rejected(self):
        content=self.nist_path.read_text().replace('0.15876','0.25876')
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'changed.csv';f.write_text(content)
            with self.assertRaisesRegex(ValueError,'TRANSCRIPTION_SHA'):m.load_nist(f)
    def test_parent_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'fake.zip';f.write_bytes(self.parent.read_bytes()+b'X')
            with self.assertRaisesRegex(ValueError,'PARENT_SHA'):m.load_parent(f)
    def test_lyalpha_energy_unit(self):self.assertTrue(math.isclose(m.E_LYA*m.EV_J,1.63403e-18,rel_tol=2e-5))

if __name__=='__main__':unittest.main(verbosity=1)
