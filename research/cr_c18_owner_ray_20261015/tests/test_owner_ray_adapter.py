"""Native Rust AXBI checkpoint and photon/thermal reaction parity regression."""
import json,os,hashlib
from pathlib import Path
import numpy as np
import pytest
from owner_adapter import read_native_export,local_photo_step,EV_ERG
from owner_age_bridge import owner_namespace

HERE=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get("REI_BIANCHI_ROOT","/home/cosmosapjw/Dropbox/bianchi/rei_bianchi"))
FILES={"ZERO":"research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO/checkpoint.txt",
 "PLUS":"research/axbi_goal_20261014/report/full_progress_32d11e733155/snapshot_20261014T083357015083Z/SHEAR_PLUS/checkpoint.txt"}

def native(name):
 return read_native_export(HERE/"results"/f"AXBI_{name}_native.tsv")

def test_owner_sha_pin():
 lock=json.loads((HERE/"OWNER_LOCK.json").read_text())
 for rel,h in lock["refs"].items():
  f=ROOT/rel
  assert f.is_file(),rel
  assert hashlib.sha256(f.read_bytes()).hexdigest()==h,rel

@pytest.mark.parametrize("name,q,amount",[("ZERO",0.,1.649933353054249e-6),
                                           ("PLUS",.01,2.7963611369316e-7)])
def test_real_Axbi_Rust_checkpoint_and_photon_counts(name,q,amount):
 x=native(name)
 assert x.q==q and x.stocks.shape==(8,49) and x.sigma.shape==(49,3)
 np.testing.assert_allclose(x.rust_N,amount,rtol=2e-14)
 assert abs(x.rust_NR)<1e-12
 assert abs(x.rust_UR)<1e-9
 original=(ROOT/FILES[name]).read_text().splitlines()
 assert original[0]=="AXBI_CHECKPOINT_V2" and len(original)==6
 np.testing.assert_array_equal(x.stocks.ravel(),
     np.array([float(z) for z in original[4].split()]))

def test_RJ_jacobian_and_native_source_deposition():
 a=native("ZERO");b=native("PLUS")
 np.testing.assert_allclose(a.rays[:,2],1,atol=1e-14,rtol=0)
 assert b.rays[:,2].min()<.995 and b.rays[:,2].max()>1.01
 for d in (a,b):
  assert d.stocks.min()>=0 and d.source.min()>=0
  np.testing.assert_allclose(d.rays[:,5].sum(),1,atol=2e-14,rtol=0)
  np.testing.assert_allclose(d.source.sum(),d.emission_rate,
         atol=1e-30,rtol=1e-12)

@pytest.mark.parametrize("name",["ZERO","PLUS"])
def test_Rust_Verner_native_Python_fit_all_energy_nodes(name):
 d=native(name);ns=owner_namespace(ROOT)
 s=np.array([[ns["sigma"](float(e),f) for f in ns["fit"]]
          for e in d.energies])
 np.testing.assert_allclose(s,d.sigma,rtol=3e-15,atol=0)

@pytest.mark.parametrize("name",["ZERO","PLUS"])
def test_C17_positive_event_heating_and_ledger(name):
 d=native(name)
 out=local_photo_step(d,1e10)
 assert min(out["species_photoevents_per_H"])>=0
 assert min(out["species_heat_eV_per_H"])>=0
 assert abs(out["photon_number_residual"])<1e-17
 assert abs(out["local_photon_energy_residual_eV_per_H"])<1e-15
 assert out["last_photons_per_H"]>0
 assert out["native_RJ_angular_fraction_sum"]==pytest.approx(1.,abs=2e-14)
 short=local_photo_step(d,1e8)
 assert sum(short["species_photoevents_per_H"])<sum(out["species_photoevents_per_H"])

@pytest.mark.parametrize("name",["ZERO","PLUS"])
def test_actual_Rust_point_RHS_photo_input_unit_contract(name):
 d=native(name);result=local_photo_step(d,1e10)
 rows={}
 rhs_name="SHEAR_PLUS" if name=="PLUS" else name
 text=(HERE/"results"/f"AXBI_{rhs_name}_rust_point_rhs.tsv").read_text().splitlines()
 assert text[0]=="C18_OWNER_POINT_RHS_V1"
 for line in text[1:]:
  a=line.split("\t")
  rows[a[0]]=np.array([float(z) for z in a[1:]])
 expected=np.asarray(result["species_photoevents_per_H"])*d.nH/1e10
 np.testing.assert_allclose(rows["PHOTO_EVENT_RATE_CM3_S"],expected,
                        rtol=2e-13,atol=1e-28)
 heat=sum(result["species_heat_eV_per_H"])
 binding=sum(result["species_binding_eV_per_H"])
 np.testing.assert_allclose(rows["PHOTO_INPUT_ERG_CM3_S"],
             [d.nH*(heat+binding)*EV_ERG/1e10],rtol=2e-13,atol=1e-35)
 assert np.all(np.isfinite(rows["FRACTION_DT_S"]))

def test_tampered_native_export_rejected(tmp_path):
 original=(HERE/"results/AXBI_ZERO_native.tsv").read_text()
 f=tmp_path/"tampered.tsv"
 f.write_text(original.replace("C18_RUST_AUTHORIZED_AXBI_RAY_STOCK_V1","BAD",1))
 with pytest.raises(ValueError):
  read_native_export(f)
 f.write_text(original.replace("STOCK\t0\t0\t","STOCK\t0\t0\t9",1))
 with pytest.raises((AssertionError,ValueError)):
  read_native_export(f)
