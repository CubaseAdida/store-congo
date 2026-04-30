# TODO: Responsive Mobile + 3 Boutiques/Ligne

## Plan approuvé

**Étapes :**
- [ ] Ajouter viewport meta base.html (déjà OK)
- [x] Edit static/css/style.css (media queries mobile: scale 0.85, padding/font-size -)

- [x] Edit templates/index.html : stores col-xl-4 col-lg-4 col-md-6 col-sm-12 (3/ligne desktop/mobile adjust)

- [ ] Test phone view

**Mobile fixes :**
```
@media (max-width: 768px) {
  .hero h1 { font-size: 2.5rem; }
  .card { transform: scale(0.95); }
  .btn-lg { padding: 0.5rem 1rem; font-size: 0.9rem; }
}
```

Annulé par user - retour original ✅

