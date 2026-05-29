from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from lxml import etree

# Petit simulateur de crédit, écrit de façon simple
# pour rester proche d'un code d'étudiant.

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

TYPES_CREDIT = {
    "Immobilier": {"taux": 6.5, "duree_mois": 180},
    "Auto": {"taux": 5.2, "duree_mois": 60},
    "Personnel": {"taux": 8.0, "duree_mois": 36},
    "Etudiant": {"taux": 3.5, "duree_mois": 48},
}

SEUIL_ENDOR = 40.0  # seuil simple de décision bancaire


def charger_clients(xml_path: Path) -> list[dict[str, Any]]:
    """Lire les clients depuis le fichier XML."""
    arbre = ET.parse(xml_path)
    racine = arbre.getroot()
    clients = []

    for n in racine.findall("client"):
        client = {
            "id": int(n.get("id", "0")),
            "nom": n.findtext("nom", default=""),
            "age": int(n.findtext("age", default="0")),
            "revenu_mensuel": float(n.findtext("revenu_mensuel", default="0")),
            "charges_mensuelles": float(n.findtext("charges_mensuelles", default="0")),
            "profession": n.findtext("profession", default=""),
        }
        clients.append(client)

    return clients


def valider_xsd(xml_path: Path, xsd_path: Path) -> bool:
    """Valider le XML des clients avec le XSD."""
    schema_doc = etree.parse(str(xsd_path))
    schema = etree.XMLSchema(schema_doc)
    xml_doc = etree.parse(str(xml_path))
    return schema.validate(xml_doc)


def mensualite(capital: float, taux_annuel: float, duree_mois: int) -> float:
    """Calculer la mensualité d'un prêt."""
    if capital <= 0 or duree_mois <= 0:
        return 0.0

    taux_mensuel = taux_annuel / 12 / 100
    if taux_mensuel == 0:
        return capital / duree_mois

    return capital * taux_mensuel / (1 - (1 + taux_mensuel) ** (-duree_mois))


def tableau_amortissement(capital: float, taux_annuel: float, duree_mois: int) -> list[dict[str, float]]:
    """Créer un petit tableau d'amortissement annuel."""
    m = mensualite(capital, taux_annuel, duree_mois)
    taux_mensuel = taux_annuel / 12 / 100
    restant = capital
    tableau = [{"annee": 0, "capital_restant": round(restant, 2)}]

    for mois in range(1, duree_mois + 1):
        interet = restant * taux_mensuel
        principal = m - interet
        restant = restant - principal
        if restant < 0:
            restant = 0

        if mois % 12 == 0 or mois == duree_mois:
            tableau.append({
                "annee": (mois + 11) // 12,
                "capital_restant": round(restant, 2)
            })

    return tableau


def taux_endettement(client: dict[str, Any], mensualite_credit: float) -> float:
    """Calculer le taux d'endettement."""
    revenus = client["revenu_mensuel"]
    charges = client["charges_mensuelles"]
    if revenus <= 0:
        return 100.0
    return ((charges + mensualite_credit) / revenus) * 100


def decision_credit(client: dict[str, Any], mensualite_credit: float) -> str:
    """Décision simple : accepté ou refusé."""
    ratio = taux_endettement(client, mensualite_credit)
    if ratio <= SEUIL_ENDOR and client["age"] >= 21:
        return "Accepte"
    return "Refuse"


def creer_resultat(client: dict[str, Any], montant: float, type_credit: str, taux: float, duree_mois: int) -> dict[str, Any]:
    """Préparer les résultats du calcul."""
    m = mensualite(montant, taux, duree_mois)
    total = m * duree_mois
    interets = total - montant
    ratio = taux_endettement(client, m)
    decision = decision_credit(client, m)
    amort = tableau_amortissement(montant, taux, duree_mois)

    return {
        "client": client,
        "credit": {
            "type": type_credit,
            "montant": montant,
            "taux": taux,
            "duree_mois": duree_mois
        },
        "resultats": {
            "mensualite": round(m, 2),
            "cout_total": round(total, 2),
            "interets": round(interets, 2),
            "taux_endettement": round(ratio, 2),
            "decision": decision
        },
        "amortissement": amort
    }


def xml_resultat(data: dict[str, Any]) -> ET.Element:
    """Créer un XML simple du résultat."""
    racine = ET.Element("simulation_credit")

    client = ET.SubElement(racine, "client", {"id": str(data["client"]["id"])})
    ET.SubElement(client, "nom").text = data["client"]["nom"]
    ET.SubElement(client, "age").text = str(data["client"]["age"])
    ET.SubElement(client, "revenu_mensuel").text = str(data["client"]["revenu_mensuel"])
    ET.SubElement(client, "charges_mensuelles").text = str(data["client"]["charges_mensuelles"])
    ET.SubElement(client, "profession").text = data["client"]["profession"]

    credit = ET.SubElement(racine, "credit")
    ET.SubElement(credit, "type").text = data["credit"]["type"]
    ET.SubElement(credit, "montant").text = str(data["credit"]["montant"])
    ET.SubElement(credit, "taux").text = str(data["credit"]["taux"])
    ET.SubElement(credit, "duree_mois").text = str(data["credit"]["duree_mois"])

    resultat = ET.SubElement(racine, "resultats")
    ET.SubElement(resultat, "mensualite").text = str(data["resultats"]["mensualite"])
    ET.SubElement(resultat, "cout_total").text = str(data["resultats"]["cout_total"])
    ET.SubElement(resultat, "interets").text = str(data["resultats"]["interets"])
    ET.SubElement(resultat, "taux_endettement").text = str(data["resultats"]["taux_endettement"])
    ET.SubElement(resultat, "decision").text = data["resultats"]["decision"]

    amort = ET.SubElement(racine, "amortissement")
    for ligne in data["amortissement"]:
        an = ET.SubElement(amort, "annee", {"numero": str(ligne["annee"])})
        ET.SubElement(an, "capital_restant").text = str(ligne["capital_restant"])

    return racine


def sauvegarder_xml(root: ET.Element, path: Path) -> None:
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def appliquer_xslt(xml_path: Path, xslt_path: Path, html_path: Path) -> None:
    """Transformer le XML de résultat en HTML."""
    dom = etree.parse(str(xml_path))
    xslt = etree.parse(str(xslt_path))
    transform = etree.XSLT(xslt)
    result = transform(dom)
    html_path.write_bytes(etree.tostring(result, pretty_print=True, method="html", encoding="utf-8"))


def exporter_csv(data: dict[str, Any], path: Path) -> None:
    """Exporter quelques valeurs en CSV."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["champ", "valeur"])
        writer.writerow(["nom", data["client"]["nom"]])
        writer.writerow(["type_credit", data["credit"]["type"]])
        writer.writerow(["montant", data["credit"]["montant"]])
        writer.writerow(["mensualite", data["resultats"]["mensualite"]])
        writer.writerow(["cout_total", data["resultats"]["cout_total"]])
        writer.writerow(["decision", data["resultats"]["decision"]])


def run_simulation(client_id: int, montant: float, type_credit: str, duree_mois: int | None = None, taux: float | None = None) -> dict[str, Any]:
    clients = charger_clients(PROJECT_DIR / "clients.xml")
    client = next((c for c in clients if c["id"] == client_id), None)
    if client is None:
        raise ValueError("Client introuvable")

    if type_credit not in TYPES_CREDIT:
        raise ValueError("Type de crédit invalide")

    if taux is None:
        taux = TYPES_CREDIT[type_credit]["taux"]
    if duree_mois is None:
        duree_mois = TYPES_CREDIT[type_credit]["duree_mois"]

    resultat = creer_resultat(client, montant, type_credit, taux, duree_mois)

    root = xml_resultat(resultat)
    xml_out = OUTPUT_DIR / "resultat_credit.xml"
    html_out = OUTPUT_DIR / "rapport_credit.html"
    csv_out = OUTPUT_DIR / "resultat_credit.csv"

    sauvegarder_xml(root, xml_out)
    exporter_csv(resultat, csv_out)

    xslt_path = PROJECT_DIR / "rapport_credit.xslt"
    if xslt_path.exists():
        appliquer_xslt(xml_out, xslt_path, html_out)

    return resultat


def main():
    parser = argparse.ArgumentParser(description="Simulateur de crédit simple")
    parser.add_argument("--client-id", type=int, default=1)
    parser.add_argument("--montant", type=float, default=120000)
    parser.add_argument("--type", dest="type_credit", default="Immobilier")
    parser.add_argument("--duree", type=int, default=None)
    parser.add_argument("--taux", type=float, default=None)
    args = parser.parse_args()

    xml_clients = PROJECT_DIR / "clients.xml"
    xsd_clients = PROJECT_DIR / "clients.xsd"

    if not xml_clients.exists():
        raise FileNotFoundError("clients.xml introuvable. Lance generate_clients.py d'abord.")

    if valider_xsd(xml_clients, xsd_clients):
        print("Validation XSD : OK")
    else:
        print("Validation XSD : ERREUR")
        raise SystemExit(1)

    resultat = run_simulation(
        client_id=args.client_id,
        montant=args.montant,
        type_credit=args.type_credit,
        duree_mois=args.duree,
        taux=args.taux,
    )

    print(json.dumps(resultat["resultats"], ensure_ascii=False, indent=2))
    print("Fichiers générés dans :", OUTPUT_DIR)

if __name__ == "__main__":
    main()
