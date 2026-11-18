import unittest
from pathlib import Path
from modelo import DEFAULT,PROFILES, evaluate,validate
from lectura import read_profiles
class FinOpsTest(unittest.TestCase):
 def test_base(self):
  r=evaluate(DEFAULT);d=r['calcs'];self.assertEqual(r['manual'],504e6);self.assertEqual(d['staff_r'],2);self.assertEqual(d['loads'],108000);self.assertEqual(d['manual_loads'],144000);self.assertAlmostEqual(r['econ'],493122395.99311423,places=2);self.assertAlmostEqual(r['cash'],471522395.99311423,places=2);self.assertEqual(r['payback_sustained'],25)
 def test_seasonal(self):
  r=evaluate(DEFAULT);f=r['flow'];self.assertEqual([v['month'] for v in f if v['active']][:4],[1,2,7,8]);self.assertEqual(sum(v['active'] for v in f),12);self.assertEqual(sum(v['loads'] for v in f),324000);self.assertAlmostEqual(f[-1]['bal_c'],r['cash_saving'],places=2);self.assertAlmostEqual(f[-1]['bal_e'],r['saving'],places=2)
 def test_rework(self):
  a=evaluate(DEFAULT);b=evaluate(dict(DEFAULT,re=.4));self.assertEqual(a['manual'],b['manual']);self.assertEqual(a['calcs']['manual_loads'],b['calcs']['manual_loads']);self.assertGreater(b['calcs']['loads'],a['calcs']['loads']);self.assertGreater(b['calcs']['variable'],a['calcs']['variable'])
 def test_productivity(self):
  a=evaluate(DEFAULT);b=evaluate(dict(DEFAULT,prod_r=.4));self.assertGreater(b['calcs']['staff_r'],a['calcs']['staff_r']);self.assertEqual(b['calcs']['staff_a'],a['calcs']['staff_a'])
 def test_validation(self):
  for overrides in [{'cycles':12,'months':2},{'admit':.99},{'re':-1},{'n':0},{'prod_r':0},{'safe':1,'pre_pass':.98},{'months':1,'mau':2}]:
   with self.subTest(overrides=overrides),self.assertRaises(ValueError):validate(dict(DEFAULT,**overrides))
 def test_calendar(self):
  for c in range(1,13):
   for m in range(1,12//c+1):
    p=dict(DEFAULT,cycles=c,months=m,days=min(40,31*m),mau=min(1.25,m));r=evaluate(p);self.assertEqual(sum(x['active'] for x in r['flow']),3*c*m)
 def test_storage(self):
  r=evaluate(dict(DEFAULT,retention=1));f=r['flow'];self.assertAlmostEqual(f[-1]['stock'],0);self.assertAlmostEqual(f[0]['stock'],f[0]['new'])
 def test_cash(self):
  r=evaluate(dict(DEFAULT,release=1));self.assertLessEqual(r['cash'],r['econ']);self.assertTrue(r['budget_ok'])
 def test_routes(self):
  r=evaluate(DEFAULT)['routes'];self.assertLess(r['PDF rechazado en prevalidación'],r['PDF no RUT (seguro)']);self.assertLess(r['RUT ordinario (1 ejecución, sin revisión)'],r['RUT con 1 reintento OCR adicional']);self.assertLess(r['RUT ordinario (1 ejecución, sin revisión)'],r['Subsanación: 1 carga no RUT + 1 RUT'])
 def test_workbook_inputs(self):
  file=Path(__file__).parent/'Finanzas_ICFES.xlsx'
  if not file.exists():self.skipTest('Copiar Excel actualizado para contraste')
  p=read_profiles(file);self.assertEqual(p,PROFILES)
 def test_channels(self):
  r=evaluate(DEFAULT);d=r['calcs'];self.assertAlmostEqual(d['wa']*d['fx'],863654.4,places=2);self.assertAlmostEqual(d['ses']*d['fx'],56548.8,places=2);self.assertGreater(evaluate(dict(DEFAULT,wa_marketing_n=1))['cash'],r['cash'])
 def test_alerts(self):
  self.assertEqual(evaluate(DEFAULT)['calcs']['alerts'],7200)
  self.assertEqual(evaluate(dict(DEFAULT,alert_eligible=0))['calcs']['alerts'],0)
 def test_retention_and_budget(self):
  r=evaluate(DEFAULT);self.assertAlmostEqual(r['custody_tail'],7594097.7168,places=2);self.assertTrue(r['budget_ok']);self.assertFalse(evaluate(dict(DEFAULT,budget=1))['budget_ok'])
if __name__=='__main__':unittest.main(verbosity=2)
