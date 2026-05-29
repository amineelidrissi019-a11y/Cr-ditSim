// Petit frontend en JavaScript simple.
// On charge la base des clients, on calcule le crédit
// et on dessine la courbe dans le canvas.

const typeConfig = {
  "Immobilier": { taux: 6.5, duree: 180 },
  "Auto": { taux: 5.2, duree: 60 },
  "Personnel": { taux: 8.0, duree: 36 },
  "Etudiant": { taux: 3.5, duree: 48 }
};

const seuilEndettement = 40;

const clientSelect = document.getElementById("clientSelect");
const typeSelect = document.getElementById("typeSelect");
const montantInput = document.getElementById("montantInput");
const tauxInput = document.getElementById("tauxInput");
const dureeInput = document.getElementById("dureeInput");
const simulerBtn = document.getElementById("simulerBtn");

const clientInfo = document.getElementById("clientInfo");
const mensualiteValue = document.getElementById("mensualiteValue");
const totalValue = document.getElementById("totalValue");
const endettementValue = document.getElementById("endettementValue");
const decisionValue = document.getElementById("decisionValue");
const amortBody = document.getElementById("amortBody");
const canvas = document.getElementById("chart");
const ctx = canvas.getContext("2d");

// Remplir la liste des clients
function chargerClients() {
  clientSelect.innerHTML = "";
  clientsData.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = `${c.id} - ${c.nom}`;
    clientSelect.appendChild(opt);
  });
}

// Afficher les infos du client sélectionné
function afficherClient() {
  const id = parseInt(clientSelect.value);
  const client = clientsData.find(c => c.id === id);
  if (!client) return;

  clientInfo.innerHTML = `
    <strong>Nom :</strong> ${client.nom}<br>
    <strong>Âge :</strong> ${client.age} ans<br>
    <strong>Profession :</strong> ${client.profession}<br>
    <strong>Revenu mensuel :</strong> ${client.revenu_mensuel} MAD<br>
    <strong>Charges mensuelles :</strong> ${client.charges_mensuelles} MAD
  `;
}

// Mettre les valeurs par défaut selon le type
function mettreTypeDefaut() {
  const type = typeSelect.value;
  tauxInput.value = typeConfig[type].taux;
  dureeInput.value = typeConfig[type].duree;
}

// Calcul de la mensualité
function calculMensualite(capital, tauxAnnuel, dureeMois) {
  if (capital <= 0 || dureeMois <= 0) return 0;

  const tauxMensuel = tauxAnnuel / 12 / 100;
  if (tauxMensuel === 0) return capital / dureeMois;

  return capital * tauxMensuel / (1 - Math.pow(1 + tauxMensuel, -dureeMois));
}

// Calcul du tableau d'amortissement annuel
function calculAmortissement(capital, tauxAnnuel, dureeMois) {
  const mensualite = calculMensualite(capital, tauxAnnuel, dureeMois);
  const tauxMensuel = tauxAnnuel / 12 / 100;
  let restant = capital;
  const tableau = [{ annee: 0, capital: capital }];

  for (let mois = 1; mois <= dureeMois; mois++) {
    const interet = restant * tauxMensuel;
    const principal = mensualite - interet;
    restant = restant - principal;

    if (restant < 0) restant = 0;

    if (mois % 12 === 0 || mois === dureeMois) {
      tableau.push({
        annee: Math.ceil(mois / 12),
        capital: Number(restant.toFixed(2))
      });
    }
  }

  return tableau;
}

// Taux d'endettement
function calculEndettement(client, mensualite) {
  return ((client.charges_mensuelles + mensualite) / client.revenu_mensuel) * 100;
}

// Décision simple
function decisionCredit(client, mensualite) {
  const ratio = calculEndettement(client, mensualite);
  if (ratio <= seuilEndettement && client.age >= 21) return "Accepté";
  return "Refusé";
}

// Dessiner la courbe dans le canvas
function dessinerCourbe(labels, valeurs) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const pad = 45;
  const w = canvas.width - pad * 2;
  const h = canvas.height - pad * 2;

  const max = Math.max(...valeurs);
  const min = 0;
  const range = max - min === 0 ? 1 : max - min;

  // Axes
  ctx.strokeStyle = "#94a3b8";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(pad, pad);
  ctx.lineTo(pad, pad + h);
  ctx.lineTo(pad + w, pad + h);
  ctx.stroke();

  // Ligne de la courbe
  ctx.strokeStyle = "#0f172a";
  ctx.lineWidth = 2;
  ctx.beginPath();

  valeurs.forEach((v, i) => {
    const x = pad + (i * w) / (valeurs.length - 1);
    const y = pad + h - ((v - min) / range) * h;

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);

    // Point
    ctx.fillStyle = "#c9a84c";
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.stroke();

  // Petites étiquettes pour lire la courbe
  ctx.fillStyle = "#475569";
  ctx.font = "12px Arial";
  labels.forEach((lab, i) => {
    const x = pad + (i * w) / (labels.length - 1);
    ctx.fillText(lab, x - 10, pad + h + 18);
  });
}

// Afficher le tableau
function afficherTableau(tableau) {
  amortBody.innerHTML = "";
  tableau.forEach((ligne, index) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${index === 0 ? "Départ" : "Année " + ligne.annee}</td>
      <td>${ligne.capital.toFixed(2)}</td>
    `;
    amortBody.appendChild(tr);
  });
}

// Lancer la simulation
function simuler() {
  const client = clientsData.find(c => c.id === parseInt(clientSelect.value));
  const montant = parseFloat(montantInput.value);
  const taux = parseFloat(tauxInput.value);
  const duree = parseInt(dureeInput.value);

  if (!client || isNaN(montant) || isNaN(taux) || isNaN(duree) || montant <= 0 || duree <= 0) {
    alert("Merci de remplir les champs correctement.");
    return;
  }

  const mensualite = calculMensualite(montant, taux, duree);
  const total = mensualite * duree;
  const ratio = calculEndettement(client, mensualite);
  const decision = decisionCredit(client, mensualite);

  const tableau = calculAmortissement(montant, taux, duree);
  const labels = tableau.map(l => l.annee === 0 ? "Départ" : "Année " + l.annee);
  const valeurs = tableau.map(l => l.capital);

  mensualiteValue.textContent = mensualite.toFixed(2) + " MAD";
  totalValue.textContent = total.toFixed(2) + " MAD";
  endettementValue.textContent = ratio.toFixed(2) + " %";

  decisionValue.textContent = decision;

  afficherTableau(tableau);
  dessinerCourbe(labels, valeurs);
}

// Events
clientSelect.addEventListener("change", afficherClient);
typeSelect.addEventListener("change", () => {
  mettreTypeDefaut();
});
simulerBtn.addEventListener("click", simuler);

// Initialisation
chargerClients();
mettreTypeDefaut();
afficherClient();
simuler();
