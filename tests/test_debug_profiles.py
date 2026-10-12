import unittest
from server import debug_capability, normalize_debug_mode

class DebugProfilesTest(unittest.TestCase):
    def test_project_and_department_boundaries(self):
        for mode in ('global_admin','xii_admin','xii_secretary_member'):
            self.assertTrue(debug_capability(mode,'xii.certificates.access'))
            self.assertTrue(debug_capability(mode,'xii.certificates.issue'))
        for mode in ('caecomp_admin','events_director','events_member','products_member','xii_sports_member','real'):
            self.assertFalse(debug_capability(mode,'xii.certificates.access'))
        self.assertFalse(debug_capability('xii_admin','access.manage'))
        self.assertEqual(normalize_debug_mode('admin'),'global_admin')
        self.assertEqual(normalize_debug_mode('member'),'events_member')
