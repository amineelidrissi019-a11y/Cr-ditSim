import shutil
import tempfile
from pathlib import Path
import unittest

import simulateur_credit as sc
import generate_clients as gc


class TestSimulateurCredit(unittest.TestCase):

    def test_mensualite(self):
        m = sc.mensualite(120000, 6.5, 180)
        self.assertAlmostEqual(m, 1045.33, places=1)

    def test_endettement(self):
        client = {"revenu_mensuel": 8500, "charges_mensuelles": 500, "age": 25}
        ratio = sc.taux_endettement(client, 1500)
        self.assertAlmostEqual(ratio, 23.53, places=2)

    def test_decision(self):
        client = {"revenu_mensuel": 8500, "charges_mensuelles": 500, "age": 25}
        self.assertEqual(sc.decision_credit(client, 1500), "Accepte")

    def test_tableau_amortissement(self):
        tab = sc.tableau_amortissement(10000, 6, 24)
        self.assertGreaterEqual(len(tab), 3)
        self.assertEqual(tab[0]["capital_restant"], 10000)

    def test_generation_clients(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            clients = [gc.generer_client(i) for i in range(1, 26)]
            gc.generer_xml(clients, tmp_path / "clients.xml")
            gc.generer_js(clients, tmp_path / "clients_data.js")
            self.assertTrue((tmp_path / "clients.xml").exists())
            self.assertTrue((tmp_path / "clients_data.js").exists())

    def test_validation_xsd(self):
        # Teste le couple XML/XSD dans le projet
        self.assertTrue(sc.valider_xsd(Path(sc.PROJECT_DIR / "clients.xml"), Path(sc.PROJECT_DIR / "clients.xsd")))

    def test_run_simulation(self):
        res = sc.run_simulation(1, 120000, "Immobilier")
        self.assertIn("resultats", res)
        self.assertIn(res["resultats"]["decision"], ["Accepte", "Refuse"])


if __name__ == "__main__":
    unittest.main()
