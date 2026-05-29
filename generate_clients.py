import json
import random
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

# Petit générateur simple de clients pour le projet
# On garde un style étudiant et facile à lire.

SEED = 2026

PRENOMS = [
    "Amine", "Ilyas", "Yassine", "Sara", "Aya", "Lina", "Khadija", "Omar",
    "Hajar", "Salma", "Youssef", "Nadia", "Rania", "Imane", "Aymane", "Meryem"
]

NOMS = [
    "El Idrissi", "Alaoui", "Bennani", "Boulahya", "Chafik", "Zerouali",
    "Amrani", "Lahlou", "Daoudi", "Mouline", "Rifi", "Kabbaj", "Mansouri"
]

PROFESSIONS = [
    "Etudiant", "Ingenieur", "Enseignant", "Commercant", "Fonctionnaire",
    "Medecin", "Developpeur", "Architecte", "Chef de projet", "Technicien"
]

def generer_client(numero: int) -> dict:
    """Créer un client aléatoire mais cohérent."""
    prenom = random.choice(PRENOMS)
    nom = random.choice(NOMS)
    age = random.randint(21, 60)

    profession = random.choice(PROFESSIONS)

    # Revenu simple selon le métier
    if profession == "Etudiant":
        revenu = random.randint(2500, 4500)
    elif profession in ("Technicien", "Commercant"):
        revenu = random.randint(4500, 7500)
    elif profession in ("Enseignant", "Fonctionnaire", "Developpeur"):
        revenu = random.randint(7000, 12000)
    else:
        revenu = random.randint(10000, 18000)

    charges = random.randint(500, int(revenu * 0.28))

    return {
        "id": numero,
        "nom": f"{prenom} {nom}",
        "age": age,
        "revenu_mensuel": revenu,
        "charges_mensuelles": charges,
        "profession": profession
    }

def generer_xml(clients: list[dict], chemin: Path) -> None:
    """Créer le fichier XML des clients."""
    racine = Element("clients")

    for client in clients:
        noeud = SubElement(racine, "client", {"id": str(client["id"])})
        SubElement(noeud, "nom").text = client["nom"]
        SubElement(noeud, "age").text = str(client["age"])
        SubElement(noeud, "revenu_mensuel").text = str(client["revenu_mensuel"])
        SubElement(noeud, "charges_mensuelles").text = str(client["charges_mensuelles"])
        SubElement(noeud, "profession").text = client["profession"]

    tree = ElementTree(racine)
    tree.write(chemin, encoding="utf-8", xml_declaration=True)

def generer_js(clients: list[dict], chemin: Path) -> None:
    """Créer un petit fichier JS pour le frontend."""
    texte = "const clientsData = " + json.dumps(clients, ensure_ascii=False, indent=2) + ";\n"
    chemin.write_text(texte, encoding="utf-8")

def main():
    random.seed(SEED)
    clients = [generer_client(i) for i in range(1, 26)]

    base_dir = Path(__file__).resolve().parent
    generer_xml(clients, base_dir / "clients.xml")
    generer_js(clients, base_dir / "clients_data.js")

    print("OK - clients.xml et clients_data.js générés")
    print("Nombre de clients :", len(clients))

if __name__ == "__main__":
    main()
