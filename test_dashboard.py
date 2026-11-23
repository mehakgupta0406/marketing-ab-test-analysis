"""Run with: python -m unittest test_dashboard -v"""

import unittest

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from dashboard_data import aggregate, comparisons, overall_metrics, read_users, roi_table, saved_results


class Calculations(unittest.TestCase):
    def test_saved_segments_reconcile_and_reproduce_report(self):
        data = saved_results()
        expected = data["overall"].set_index("test_group")[["users", "conversions"]].sort_index()
        for key in ["day", "hour", "exposure"]:
            totals = data[key].groupby("test_group")[["users", "conversions"]].sum().sort_index()
            pd.testing.assert_frame_equal(totals, expected)
        metrics = overall_metrics(data["overall"])
        self.assertAlmostEqual(metrics["additional"], 4342.98214589, places=6)
        self.assertAlmostEqual(metrics["lift"], 43.0850640222, places=6)
        values = roi_table(metrics["additional"], 400000, 150)["Estimated ROI (%)"]
        np.testing.assert_allclose(values[:3], [-27.61696424, 62.86183047, 334.29821459])

    def test_zero_baselines_missing_groups_and_zero_spend(self):
        table = pd.DataFrame({"hour": [0, 0], "test_group": ["ad", "psa"], "users": [100, 100], "conversions": [1, 0]})
        self.assertTrue(pd.isna(comparisons(table, "hour", [0]).loc[0, "relative_lift_pct"]))
        self.assertIsNone(overall_metrics(table.iloc[:1]))
        self.assertTrue(pd.isna(roi_table(100, 0, 10).iloc[-1]["Estimated ROI (%)"]))
        self.assertTrue(roi_table(-10, 100, 10)["Break-even spend (INR)"].isna().all())

    def test_upload_validation_and_sql_preserve_users(self):
        content = b'user id,test group,converted,total ads,most ads day,most ads hour\n1,ad,True,13,Monday,0\n2,psa,False,14,Monday,0\n'
        users = read_users(content)
        data = aggregate(users, 13)
        self.assertEqual(data["overall"]["users"].sum(), 2)
        self.assertEqual(data["overall"]["conversions"].sum(), 1)
        self.assertEqual(data["exposure"].set_index("test_group").loc["ad", "exposure"], "Light")
        for bad in [content.replace(b'False', b'unknown'), content.replace(b'2,psa', b'1,psa'), content.replace(b'Monday,0', b'Monday,24')]:
            with self.assertRaises(ValueError):
                read_users(bad)


class Interface(unittest.TestCase):
    def test_default_dashboard_and_controls(self):
        app = AppTest.from_file("app.py", default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, "588,101")
        app.selectbox[0].select("Most ads hour").run()
        self.assertEqual(len(app.exception), 0)
        app.selectbox[0].select("Ad exposure").run()
        self.assertEqual(len(app.exception), 0)
        app.number_input[0].set_value(0.0).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("undefined" in item.value for item in app.warning))
        app.radio[0].set_value("Upload CSV").run()
        self.assertEqual(len(app.exception), 0)
        content = b'user id,test group,converted,total ads,most ads day,most ads hour\n1,ad,True,13,Monday,0\n2,psa,False,14,Monday,0\n'
        app.file_uploader[0].upload("sample.csv", content).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, "2")
        app.multiselect[0].set_value([]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("No users" in item.value for item in app.warning))


if __name__ == "__main__":
    unittest.main()
