# Brand Overview Generator

Vous allez recevoir un brief et des tendances, et vous devez produire un **objet JSON** strictement conforme à ce schéma :

\`\`\`json
{
  "description_paragraphs": ["…"],
  "competitive_positioning": {
    "axes": ["…"],
    "brands": ["…"]
  },
  "persona": {
    "heading": ["…"],
    "bullets": ["…"]
  },
  "top3_competitor_actions": ["…"]
}
\`\`\`

**Instructions**
1. **description_paragraphs** :  
   1 à 3 paragraphes décrivant la marque, ses atouts et son positionnement.  
2. **competitive_positioning** :  
   - \`axes\` : 2 ou 3 axes (ex. « Prix », « Innovation », « Durabilité »).  
   - \`brands\` : pour chaque axe, 2 ou 3 concurrents clés.  
3. **persona** :  
   - \`heading\` : titre(s) court(s) décrivant le client-type (ex. « Millennial urbain »).  
   - \`bullets\` : 3 à 5 traits ou besoins de ce persona.  
4. **top3_competitor_actions** :  
   3 actions récentes et marquantes des concurrents.

**Exemple de sortie**
\`\`\`json
{
  "description_paragraphs": [
    "Marque X, implantée depuis 50 ans sur le segment premium…",
    "Elle se différencie par une forte orientation RSE…"
  ],
  "competitive_positioning": {
    "axes": ["Prix", "Innovation"],
    "brands": ["Marque A", "Marque B", "Marque C"]
  },
  "persona": {
    "heading": ["Millennial urbain"],
    "bullets": [
      "Recherche de qualité",
      "Sensibilité éco-responsable",
      "Actif sur les réseaux sociaux"
    ]
  },
  "top3_competitor_actions": [
    "Lancement d’une gamme bio par Marque A",
    "Campagne digitale immersive de Marque B",
    "Partenariat durable de Marque C"
  ]
}
\`\`\`
