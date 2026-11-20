# pubartisanrelance

Publicité vidéo verticale (9:16, 15 s) pour [Artisan Relance](https://artisan-relance.jercat.fr/), le logiciel de relance automatique de devis pour les artisans du bâtiment.

- `index.html` : page publique, la vidéo démarre seule (son coupé, bouton pour l'activer).
- `pub-artisan-relance-15s.mp4` : la vidéo finale (1080 × 1920, 30 i/s, son AAC).
- `pub-artisan-relance.html` : la même pub en animation HTML/Canvas, modifiable (bloc `CONFIG`).
- `render.js`, `bande_son.py` : pour régénérer la vidéo et le son. Voir `LISEZMOI.md`.

Site statique : aucun build nécessaire sur Vercel.
