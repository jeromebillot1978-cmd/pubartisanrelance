# Pub Artisan Relance — 15 s — 9:16

## Ce que contient le dossier

| Fichier | Rôle |
| --- | --- |
| `pub-artisan-relance.html` | Toute l'animation (5 scènes). Double-cliquez dessus pour la regarder dans le navigateur. |
| `bande-son.m4a` | Le son, lu par la page HTML s'il est dans le même dossier. |
| `bande_son.py` | Le programme qui fabrique la musique et les effets sonores (tout est synthétisé, donc libre de droits). |
| `render.js` | Le programme qui exporte la vidéo MP4. |
| `pub-artisan-relance-15s.mp4` | La vidéo finale, prête à publier. |
| `integration-site.html` | Le code à coller sur un site pour que la vidéo démarre toute seule, en boucle. |

## Regarder la pub

Ouvrez `pub-artisan-relance.html` dans Chrome : la pub démarre toute seule et tourne en boucle. Si le navigateur bloque le son, un bouton « Activer le son » apparaît en haut à droite. Un clic n'importe où sur la page active aussi le son.
- Espace : pause / lecture
- Flèches ← → : avancer ou reculer d'une image
- R : rejouer depuis le début

## Modifier un texte ou ajouter la vraie capture

En haut du fichier HTML, le bloc `CONFIG` regroupe tous les textes.
- Pour mettre une vraie capture de votre tableau de bord dans la scène 4, placez `capture.png` dans le dossier, puis écrivez `capture: "capture.png"`. Utilisez une capture au format portrait, sans aucun chiffre visible.
- Le jour où l'offre devient payante, videz la ligne `mention: ""` pour retirer « Gratuit · Sans carte bancaire ».

## Refaire la vidéo après une modification

Il faut Node.js, ffmpeg, Google Chrome et Python 3 (avec numpy et scipy).

```
npm install playwright
python3 bande_son.py        # seulement si vous changez le son
node render.js              # refait les 5 scènes puis la vidéo finale
node render.js 4            # ne refait que la scène 4, puis la vidéo finale
```

## Faire démarrer la vidéo toute seule sur un site

Un fichier MP4 ne peut pas se lancer seul : c'est le lecteur qui décide. Sur TikTok, Reels et Shorts, la vidéo démarre automatiquement dans le fil. Sur votre site, utilisez le code de `integration-site.html` avec `autoplay muted loop playsinline`. Le son est coupé au départ, car les navigateurs bloquent toute lecture automatique avec le son.
