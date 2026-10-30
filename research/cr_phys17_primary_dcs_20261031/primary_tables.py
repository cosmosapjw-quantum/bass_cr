#!/usr/bin/env python3
"""Manual transcription from the supplied *original PDF pages* (not OCR).
Kingston/Fon/Burke 1976 printed p613 Table 5: 2p unitarized Born DCS.
Kingston/Fon/Burke 1976 printed p612 Table 4: 2s unitarized Born DCS.
Kingston/Fon/Burke 1976 printed p616 Table 6/7: corresponding total cross sections.
Williams 1976 printed p1526 Table 1: MEASURED n=2 = 2s+2p inclusive DCS.
We do NOT attribute these to close-coupling DCS or 2p-resolved measured DCS.
Units DCS = a0^2/sr, totals = pi*a0^2 (as printed).
"""
import csv
from pathlib import Path
import numpy as np

# k^2 in Rydbergs: 1.00, 1.44, 2.25. Energies 13.6, 19.6, 30.6 eV as printed in their Table 7.
K2=np.array([1.00,1.44,2.25])
K_TH=np.array([0,10,20,30,40,50,60,70,80,90,100,120,140,160,180])
# Columns follow k²=1.00,1.44,2.25 and rows follow K_TH.
K2P=np.array([
[1.67,6.47,17.5],
[1.40,4.42,7.75],
[.854,1.81,1.91],
[.415,.662,.531],
[.188,.277,.181],
[.0990,.140,.0713],
[.0674,.0786,.0314],
[.0528,.0457,.0154],
[.0418,.0275,.00829],
[.0323,.0174,.00475],
[.0250,.0118,.00282],
[.0184,.00660,.00106],
[.0200,.00436,.000434],
[.0243,.00331,.000221],
[.0264,.00300,.000171]
]);
K2S=np.array([
[.443,1.28,2.29],
[.355,.791,.856],
[.183,.216,.122],
[.0597,.0334,.0288],
[.0102,.00665,.0138],
[.00466,.00479,.00756],
[.00133,.00394,.00487],
[.00212,.00336,.00382],
[.00168,.00331,.00335],
[.00113,.00355,.00301],
[.00124,.00389,.00268],
[.00400,.00456,.00201],
[.00895,.00517,.00150],
[.0136,.00567,.00120],
[.0156,.00587,.00111]
]);
# KFB Table 6/7 printed unit pi*a0^2. 'Unitarized Born' row only.
K2P_UB_TOTAL_PI=np.array([.439,.801,.973]);K2S_UB_TOTAL_PI=np.array([.0712,.102,.0987])
K2P_CC_TOTAL_PI=np.array([.800,1.18,1.10]);K2S_CC_TOTAL_PI=np.array([.362,.264,.160])

W_ENERGIES=np.array([13.87,16.46,19.58]);W_TH=np.array([15,20,25,30,40,50,60,70,80,90,100,110,120,130,140,150]);
# 'numbers in parentheses' interpreted as uncertainties in last significant digits.
# E columns correspond 13.87, 16.46, 19.58 eV, ALL inclusive 2s+2p.
W_N2=np.array([
[1.18,1.81,2.19],
[1.11,1.19,1.57],
[.632,.760,.972],
[.447,.528,.598],
[.195,.234,.217],
[.106,.141,.108],
[.0673,.0930,.0798],
[.0609,.0562,.0511],
[.0551,.0507,.0463],
[.0550,.0508,.0465],
[.0532,.0503,.0460],
[.0588,.0596,.0502],
[.0709,.0650,.0525],
[.0865,.0867,.0682],
[.126,.119,.0748],
[.169,.142,.0821]
]);
W_ERR=np.array([
[.26,.43,.47],
[.18,.15,.19],
[.072,.088,.114],
[.049,.057,.064],
[.023,.026,.027],
[.014,.015,.013],
[.0077,.0118,.0102],
[.0072,.0062,.0065],
[.0066,.0059,.0055],
[.0071,.0062,.0056],
[.0069,.0059,.0056],
[.0072,.0072,.0058],
[.0086,.0078,.0060],
[.0098,.0098,.0070],
[.017,.021,.0081],
[.021,.016,.0178]
]);

def write_csv(fp,records):
    records=list(records)
    with open(fp,'w',newline='',encoding='utf8') as f:
      w=csv.DictWriter(f,fieldnames=records[0].keys(),lineterminator='\n');w.writeheader();w.writerows(records)

def export_tables(dest):
  dest=Path(dest);dest.mkdir(exist_ok=True,parents=True)
  rec=[]
  for j,k in enumerate(K2):
    for i,angle in enumerate(K_TH):
      for channel,arr,table in [('2p',K2P,'5'),('2s',K2S,'4')]:
       rec.append(dict(source='Kingston_Fon_Burke_1976',printed_page=613 if channel=='2p' else 612,table=table,approximation='UNITARIZED_BORN_NOT_CLOSE_COUPLING',channel=channel,k_squared_Ryd=float(k),energy_eV_printed={1.00:13.6,1.44:19.6,2.25:30.6}[float(k)],electron_angle_degree=float(angle),DCS_a0_sq_per_sr=float(arr[i,j])))
  write_csv(dest/'KINGSTON_1976_TABLE4_TABLE5_UB_DCS.csv',rec)
  rec=[]
  for j,e in enumerate(W_ENERGIES):
    for i,angle in enumerate(W_TH):
      rec.append(dict(source='Williams_1976',printed_page=1526,table='1',data_type='EXPERIMENT_N2_2s_PLUS_2p_UNRESOLVED',incident_electron_energy_eV=float(e),electron_angle_degree=float(angle),DCS_a0_sq_per_sr=float(W_N2[i,j]),absolute_uncertainty_a0_sq_per_sr=float(W_ERR[i,j])))
  write_csv(dest/'WILLIAMS_1976_TABLE1_MEASURED_N2_DCS.csv',rec)
  rec=[]
  for j,k in enumerate(K2):
    for state,ub,cc in [('2p',K2P_UB_TOTAL_PI,K2P_CC_TOTAL_PI),('2s',K2S_UB_TOTAL_PI,K2S_CC_TOTAL_PI)]:
      rec.append(dict(source='Kingston_Fon_Burke_1976',printed_page=616,table='7' if state=='2p' else '6',k_squared_Ryd=float(k),channel=state,unit='pi*a0^2',unitarized_Born_total=float(ub[j]),close_coupling_total=float(cc[j])))
  write_csv(dest/'KINGSTON_1976_TABLE6_TABLE7_TOTALS.csv',rec)
  return 90,48,6

if __name__=='__main__':print('PRIMARY_ROWS',export_tables(Path(__file__).resolve().parent/'results'))
