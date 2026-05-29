<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <html lang="fr">
      <head>
        <meta charset="UTF-8"/>
        <title>Rapport de crédit</title>
        <style>
          body { font-family: Arial, sans-serif; background:#f6f7fb; color:#1f2937; padding:30px; }
          .box { max-width: 900px; margin:auto; background:white; padding:24px; border-radius:12px; }
          h1 { color:#0f172a; }
          table { width:100%; border-collapse: collapse; margin-top:16px; }
          th, td { border:1px solid #ddd; padding:10px; text-align:left; }
          th { background:#0f172a; color:white; }
          .ok { color:green; font-weight:bold; }
          .no { color:#b91c1c; font-weight:bold; }
        </style>
      </head>
      <body>
        <div class="box">
          <h1>Rapport de simulation de crédit</h1>

          <h2>Client</h2>
          <p><strong>Nom :</strong> <xsl:value-of select="simulation_credit/client/nom"/></p>
          <p><strong>Profession :</strong> <xsl:value-of select="simulation_credit/client/profession"/></p>

          <h2>Crédit</h2>
          <table>
            <tr><th>Type</th><th>Montant</th><th>Taux</th><th>Durée (mois)</th></tr>
            <tr>
              <td><xsl:value-of select="simulation_credit/credit/type"/></td>
              <td><xsl:value-of select="simulation_credit/credit/montant"/></td>
              <td><xsl:value-of select="simulation_credit/credit/taux"/></td>
              <td><xsl:value-of select="simulation_credit/credit/duree_mois"/></td>
            </tr>
          </table>

          <h2>Résultat</h2>
          <table>
            <tr><th>Mensualité</th><th>Coût total</th><th>Intérêts</th><th>Taux d'endettement</th><th>Décision</th></tr>
            <tr>
              <td><xsl:value-of select="simulation_credit/resultats/mensualite"/></td>
              <td><xsl:value-of select="simulation_credit/resultats/cout_total"/></td>
              <td><xsl:value-of select="simulation_credit/resultats/interets"/></td>
              <td><xsl:value-of select="simulation_credit/resultats/taux_endettement"/> %</td>
              <td>
                <xsl:choose>
                  <xsl:when test="simulation_credit/resultats/decision='Accepte'">
                    <span class="ok">Accepté</span>
                  </xsl:when>
                  <xsl:otherwise>
                    <span class="no">Refusé</span>
                  </xsl:otherwise>
                </xsl:choose>
              </td>
            </tr>
          </table>

          <h2>Capital restant dû</h2>
          <table>
            <tr><th>Année</th><th>Capital restant</th></tr>
            <xsl:for-each select="simulation_credit/amortissement/annee">
              <tr>
                <td><xsl:value-of select="@numero"/></td>
                <td><xsl:value-of select="capital_restant"/></td>
              </tr>
            </xsl:for-each>
          </table>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
