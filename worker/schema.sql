-- La table du compteur d'audience.
--
--   wrangler d1 execute boussole-celeste --remote --file=schema.sql
--
-- Quatre colonnes, et rien de plus : un jour, un nom d'événement, l'adresse d'une
-- page du guide le cas échéant, et un nombre. Aucune colonne ne peut désigner une
-- personne — il n'y a ni adresse IP, ni identifiant de visite, ni horodatage à la
-- seconde, qui permettrait de recouper deux événements entre eux.
--
-- La clé primaire porte sur les trois premières colonnes : une seule ligne par
-- jour et par événement, qu'on incrémente. La base reste minuscule — de l'ordre
-- de sept lignes par jour, quelques milliers par an.

CREATE TABLE IF NOT EXISTS compteur (
  jour      TEXT    NOT NULL,           -- AAAA-MM-JJ
  evenement TEXT    NOT NULL,           -- accueil · article · test-debut · test-fin · paywall · stripe
  page      TEXT    NOT NULL DEFAULT '',-- /guide/xxx.html, vide pour les autres événements
  n         INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (jour, evenement, page)
);

-- Les lectures se font toujours sur une plage de dates, jamais sur la table entière.
CREATE INDEX IF NOT EXISTS compteur_jour ON compteur (jour);

-- Les codes cadeaux. Un acheteur du dossier peut en engendrer UN, qu'il offre à
-- quelqu'un : celui-ci obtient les résultats détaillés, jamais le dossier.
--
-- Trois garde-fous, et ils tiennent tous dans cette table :
--   · un seul code par achat        → la contrainte UNIQUE sur session
--   · un seul usage                 → utilise_le, écrit au moment où il sert
--   · vingt-quatre heures           → expire_le, posé à la création
--
-- Un achat, un code, une fois pour toutes : la contrainte UNIQUE sur session
-- vaut aussi après la péremption. Un code oublié est perdu, sans réédition.
--
-- Rien ici ne désigne personne : une référence d'achat Stripe, deux dates.
CREATE TABLE IF NOT EXISTS cadeau (
  code       TEXT PRIMARY KEY,
  session    TEXT NOT NULL UNIQUE,   -- l'achat qui l'a engendré
  cree_le    TEXT NOT NULL,
  expire_le  TEXT NOT NULL,
  utilise_le TEXT                    -- NULL tant qu'il n'a pas servi
);
