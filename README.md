# Simulateur de Crédit

Projet simple en **Python + XML + XSD + XSLT + HTML/CSS/JS**.

## Fichiers principaux
- `generate_clients.py` : génère 25 clients aléatoires
- `clients.xml` : base de données XML
- `clients.xsd` : validation du XML
- `simulateur_credit.py` : calcul du crédit + génération XML/HTML
- `index.html` : frontend simple
- `app.js` : logique de simulation dans le navigateur
- `style.css` : design simple
- `rapport_credit.xslt` : transformation HTML du résultat XML

## Lancer le projet
1. Générer les clients :
```bash
py generate_clients.py
```

2. Ouvrir `index.html` dans le navigateur ou avec Live Server.

3. Lancer le simulateur Python :
```bash
py simulateur_credit.py --client-id 1 --montant 120000 --type Immobilier
```

4. Lancer les tests :
```bash
py -m unittest tests_simulateur_credit.py
```

## Sorties générées
- `outputs/resultat_credit.xml`
- `outputs/rapport_credit.html`
- `outputs/resultat_credit.csv`
