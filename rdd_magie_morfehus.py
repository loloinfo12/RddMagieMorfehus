#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RDD — Haut-Rêve · Morfehus
Application d'aide de jeu pour Rêve de Dragon
Conversion Python/Tkinter depuis le composant React d'origine.
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import json
import os
from pathlib import Path

# ─── Couleurs ───────────────────────────────────────────────────────────────
BG   = "#080D1A"
CD   = "#0D1525"
BO   = "#181F30"
GO   = "#C0913A"
SV   = "#8899AA"
FG   = "#E8DCC8"

VC = {
    "Oniros":  {"color": "#C0913A", "g": "◈"},
    "Hypnos":  {"color": "#9B59B6", "g": "◉"},
    "Narcos":  {"color": "#2ECC71", "g": "◆"},
}
TC = {
    "Cité": "#C9A227", "Désert": "#C87941", "Forêt": "#2A7D2A",
    "Mont": "#7B8D9A", "Sanctuaire": "#8B2FC9", "Nécropole": "#5C2D91",
    "Pont": "#C84315", "Fleuve": "#1565C0", "Lac": "#0288D1",
    "Plaines": "#4CAF50", "Collines": "#8C9B21", "Gouffre": "#283593",
    "Désolation": "#6D4C41", "Marais": "#2E7D32", "Variable": "#607D8B",
}

# Niveaux de fatigue
FN = [
    {"l": "En forme",  "s": 3, "m": 0,  "c": "#22c55e"},
    {"l": "Fatigué −1","s": 3, "m": -1, "c": "#84cc16"},
    {"l": "Fatigué −2","s": 1, "m": -2, "c": "#eab308"},
    {"l": "Fatigué −3","s": 1, "m": -3, "c": "#f97316"},
    {"l": "Fatigué −4","s": 1, "m": -4, "c": "#ef4444"},
    {"l": "Fatigué −5","s": 1, "m": -5, "c": "#dc2626"},
    {"l": "Fatigué −6","s": 1, "m": -6, "c": "#991b1b"},
    {"l": "Épuisé  −7","s": 1, "m": -7, "c": "#450a0a"},
]
SI = []
for n in FN:
    for _ in range(n["s"]):
        SI.append(n)

def get_fn(f):
    r = f
    for n in FN:
        if r <= 0:
            return n
        if r < n["s"]:
            return n
        r -= n["s"]
    return FN[-1]

# ─── Base de sorts ──────────────────────────────────────────────────────────
SORTS = [
  {"id":1,"n":"AIR EN EAU","v":"Oniros","t":"Cité","d":-4,"c":2,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute l'air de la zone en eau pure et potable (Eau Alchimiquement Simple). La quantité d'eau créée est proportionnelle au volume de la zone."},
  {"id":2,"n":"AIR EN FEU","v":"Oniros","t":"Désolation","d":-6,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute l'air de la zone en feu ordinaire, chaud et lumineux. Peut causer des brûlures et provoquer des incendies."},
  {"id":3,"n":"AIR EN BOIS","v":"Oniros","t":"Forêt","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute l'air de la zone en bois ordinaire (chêne ou similaire), dur et compact. Instantanée et permanente."},
  {"id":4,"n":"AIR EN TERRE","v":"Oniros","t":"Collines","d":-9,"c":7,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute l'air de la zone en terre commune. Instantanée et permanente."},
  {"id":5,"n":"AIR EN MÉTAL","v":"Oniros","t":"Mont","d":-11,"c":9,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute l'air de la zone en métal commun (fer ou plomb). Instantanée et permanente."},
  {"id":6,"n":"EAU EN BOIS","v":"Oniros","t":"Forêt","d":-5,"c":3,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute l'eau de la zone en bois ordinaire. Instantanée et permanente."},
  {"id":7,"n":"EAU EN AIR","v":"Oniros","t":"Désert","d":-6,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute l'eau de la zone en air pur. Utile pour assécher un espace ou créer de l'air dans un milieu aquatique."},
  {"id":8,"n":"EAU EN TERRE","v":"Oniros","t":"Pont","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute l'eau de la zone en terre commune. Instantanée et permanente."},
  {"id":9,"n":"EAU EN MÉTAL","v":"Oniros","t":"Gouffre","d":-9,"c":7,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute l'eau de la zone en métal commun. Instantanée et permanente."},
  {"id":10,"n":"EAU EN FEU","v":"Oniros","t":"Mont","d":-10,"c":8,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute l'eau de la zone en feu ordinaire."},
  {"id":11,"n":"TERRE EN MÉTAL","v":"Oniros","t":"Gouffre","d":-4,"c":2,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute la terre de la zone en métal commun. Instantanée et permanente."},
  {"id":12,"n":"TERRE EN BOIS","v":"Oniros","t":"Plaines","d":-6,"c":4,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute la terre de la zone en bois ordinaire. Instantanée et permanente."},
  {"id":13,"n":"TERRE EN FEU","v":"Oniros","t":"Mont","d":-7,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute la terre de la zone en feu ordinaire."},
  {"id":14,"n":"TERRE EN AIR","v":"Oniros","t":"Lac","d":-9,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute la terre de la zone en air. Utile pour creuser des passages ou libérer un espace enseveli."},
  {"id":15,"n":"TERRE EN EAU","v":"Oniros","t":"Forêt","d":-11,"c":9,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute la terre de la zone en eau pure."},
  {"id":16,"n":"BOIS EN TERRE","v":"Oniros","t":"Nécropole","d":-4,"c":2,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute le bois de la zone en terre commune. Instantanée et permanente."},
  {"id":17,"n":"BOIS EN EAU","v":"Oniros","t":"Sanctuaire","d":-7,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute le bois de la zone en eau pure."},
  {"id":18,"n":"BOIS EN MÉTAL","v":"Oniros","t":"Mont","d":-6,"c":4,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute le bois de la zone en métal commun. Instantanée et permanente."},
  {"id":19,"n":"BOIS EN FEU","v":"Oniros","t":"Désert","d":-9,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute le bois de la zone en feu."},
  {"id":20,"n":"BOIS EN AIR","v":"Oniros","t":"Marais","d":-11,"c":9,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute le bois de la zone en air pur."},
  {"id":21,"n":"FEU EN AIR","v":"Oniros","t":"Désolation","d":-4,"c":2,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute le feu de la zone en air pur. Permet d'éteindre rapidement des flammes."},
  {"id":22,"n":"FEU EN MÉTAL","v":"Oniros","t":"Sanctuaire","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute le feu de la zone en métal solide et permanent."},
  {"id":23,"n":"FEU EN EAU","v":"Oniros","t":"Cité","d":-6,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute le feu de la zone en eau (Eau Alchimiquement Simple). Utile pour lutter contre un incendie."},
  {"id":24,"n":"FEU EN BOIS","v":"Oniros","t":"Collines","d":-9,"c":7,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute le feu de la zone en bois ordinaire. Instantanée et permanente."},
  {"id":25,"n":"FEU EN TERRE","v":"Oniros","t":"Désert","d":-11,"c":9,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute le feu de la zone en terre commune. Instantanée et permanente."},
  {"id":26,"n":"MÉTAL EN FEU","v":"Oniros","t":"Lac","d":-5,"c":3,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute le métal de la zone en feu. Le métal prend feu et se transforme en flammes vives."},
  {"id":27,"n":"MÉTAL EN TERRE","v":"Oniros","t":"Plaines","d":-6,"c":4,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute le métal de la zone en terre. Instantanée et permanente."},
  {"id":28,"n":"MÉTAL EN AIR","v":"Oniros","t":"Fleuve","d":-7,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute le métal de la zone en air pur. Le métal disparaît."},
  {"id":29,"n":"MÉTAL EN EAU","v":"Oniros","t":"Fleuve","d":-9,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Transmutation","e":"Transmute le métal de la zone en eau pure."},
  {"id":30,"n":"MÉTAL EN BOIS","v":"Oniros","t":"Collines","d":-10,"c":8,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Transmutation","e":"Transmute le métal de la zone en bois ordinaire. Instantanée et permanente."},
  {"id":31,"n":"ARABESQUES","v":"Oniros","t":"Cité","d":-6,"c":5,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Zone contrôlée","e":"Dans cette zone contrôlée, les forces pures dessinent des formes en 3D selon le désir du magicien. Ces assemblages ne sont pas tangibles mais visibles. Usages multiples : signes, plans, dessins."},
  {"id":32,"n":"ARBRES À ARMES","v":"Oniros","t":"Désolation","d":-10,"c":8,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone offensive","e":"Zone de BOIS EN MÉTAL : les végétaux se transforment partiellement en acier aiguisé. Feuilles → pointes de flèches barbelées, baies → billes pour frondes, tiges → lames de poignards."},
  {"id":33,"n":"BOUCLIER GARDIEN","v":"Oniros","t":"Sanctuaire","d":-8,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Défense","e":"Petite zone mobile et contrôlée de force pure, assez vive et solide pour parer les coups. Le magicien garde les deux mains libres et a une parade supplémentaire avec VUE/Oniros limité par Vigilance. Résistance de 20."},
  {"id":34,"n":"BOULET","v":"Oniros","t":"Mont","d":-8,"c":6,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Zone d'AIR EN TERRE instantanée produisant toujours de la pierre. Résultat : un boulet de taille variable. En pierre. Dur, rond, et lourd."},
  {"id":35,"n":"BOUQUET D'ARMES","v":"Oniros","t":"Sanctuaire","d":-11,"c":9,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone de MÉTAL EN BOIS transformant le métal en fleurs (nature au choix du lanceur, sinon au hasard). Paix et amour..."},
  {"id":36,"n":"BUISSON","v":"Oniros","t":"Collines","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone","e":"Crée un buisson dont la nature (ordinaire) et la forme sont au choix du lanceur. Idéal pour se cacher ou faire une sieste à l'ombre !"},
  {"id":37,"n":"CARAPACE","v":"Oniros","t":"Sanctuaire","d":-11,"c":9,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Défense","e":"Variation d'AIR EN MÉTAL. Produit une sphère creuse en acier aux murs épais, gravée d'écailles, avec une trappe par-dessus (fermée de l'intérieur) et huit meurtrières étroites. Un abri parfait."},
  {"id":38,"n":"CLAQUE","v":"Oniros","t":"Cité","d":-5,"c":3,"p":"E2","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Venue de nulle part, une force invisible soufflette la cible. Peut aussi faire tomber un objet en équilibre, taper dans le dos... Une CLAQUE bien ajustée ne fait pas de dégâts autres que moraux. Au mieux, la cible est en demi-surprise pendant un round."},
  {"id":39,"n":"ÉTOILE","v":"Oniros","t":"Plaines","d":-4,"c":2,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Lumière","e":"Variante d'AIR EN FEU : microzone engendrant un feu blanc, froid et presque stable. Comme une étoile... Pas d'utilité pratique mais très joli."},
  {"id":40,"n":"FAUTEUIL","v":"Oniros","t":"Cité","d":-5,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Confort","e":"Zone créant un siège de forces intangibles qui épousent à merveille les formes de celui qui s'y assoit. Confort absolu. Permet aussi de flotter assis dans rien et d'épater le commun."},
  {"id":41,"n":"FILET DE RACINES","v":"Oniros","t":"Forêt","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Zone d'AIR EN BOIS instantanée créant une cage d'épaisses racines entremêlées. Les créatures dans la zone se retrouvent emprisonnées."},
  {"id":42,"n":"FLAMBOIEMENT","v":"Oniros","t":"Désert","d":-8,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone de feu","e":"Zone mobile de MÉTAL EN FEU n'affectant que d'infimes sphères de métal à la fois. Léger réchauffement du métal, parcouru d'étincelles et de flammèches."},
  {"id":43,"n":"FLÈCHE DE FEU","v":"Oniros","t":"Mont","d":-7,"c":5,"p":"E3","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Variante d'AIR EN FEU mobile, rapide et instantanée. Va en droite ligne là où on l'envoie. Créatures touchées : brûlures (+dom+4) et risque de s'enflammer."},
  {"id":44,"n":"GRÊLE MÉTALLIQUE","v":"Oniros","t":"Gouffre","d":-11,"c":9,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Éphémère zone d'AIR EN MÉTAL créant une multitude de billes de fer. Redoutables si elles tombent d'assez haut (+dom+1 à +9 selon jet de CHANCE ou Dérobée)."},
  {"id":45,"n":"LIT DES EAUX","v":"Oniros","t":"Cité","d":-6,"c":4,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Confort","e":"Variante d'EAU EN BOIS. Les eaux accouchent d'un lit dont les dimensions et la forme sont à la discrétion du haut-rêvant. Généralement garni de couvertures en lin, d'oreillers rembourrés de feuilles."},
  {"id":46,"n":"MAIN GIGANTE","v":"Oniros","t":"Mont","d":-8,"c":"6+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone contrôlée","e":"Zone contrôlée et mobile sculptée en forme de main invisible (force pure, résistance 20). Peut manipuler, étreindre et soulever toute chose de Taille 8 ou moins. Force = 2 × r dépensés."},
  {"id":47,"n":"MARE","v":"Oniros","t":"Plaines","d":-10,"c":8,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone","e":"La Terre prise dans la zone devient aussitôt une jolie mare avec roseaux, nénuphars et lentilles d'eau pour faire vrai. L'eau est bonne à boire."},
  {"id":48,"n":"MORSURE DE LA TERRE","v":"Oniros","t":"Gouffre","d":-11,"c":9,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone offensive","e":"Variante d'AIR EN TERRE créant des stalactites ou stalagmites, tous acérés. Armes cruelles (équivalent gros javelots, +dom+2) ou projectiles redoutables."},
  {"id":49,"n":"PLATEAU","v":"Oniros","t":"Cité","d":-4,"c":3,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Variante ludique de la zone de PONT. Mobile, forme exacte au choix. Diamètre limité à 1,5 mètres."},
  {"id":50,"n":"PLUIE","v":"Oniros","t":"Plaines","d":-7,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone d'AIR EN EAU. La transmutation se fait en multitude de petites sphères de taille variable. Débit réglable de la bruine infime à la bonne averse."},
  {"id":51,"n":"PLUIE DE FLEURS","v":"Oniros","t":"Plaines","d":-9,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone d'AIR EN BOIS créant un nuage de fleurettes bleues charmantes. Leur doux parfum invite au repos : jet de Volonté à -4 ou sommeil irrésistible."},
  {"id":52,"n":"PONT IMMATÉRIEL","v":"Oniros","t":"Pont","d":-6,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Déplacement","e":"Crée un pont de force pure translucide et traversable. Mobile selon le désir du magicien."},
  {"id":53,"n":"RÉCIPIENT","v":"Oniros","t":"Cité","d":-6,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone de forces mobile créant des sphères creuses ouvertes au-dessus. Forme au choix, de la chopine à la baignoire."},
  {"id":54,"n":"TORCHE","v":"Oniros","t":"Cité","d":-7,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Lumière","e":"Micro-zone d'AIR EN FEU (max 10 cm de diamètre), variable et mobile. Réduite à un lumignon : briquet. Plus vive : éclaire comme une flamme ordinaire mais inextinguible."},
  {"id":55,"n":"BROUILLARD","v":"Oniros","t":"Forêt","d":-3,"c":"1+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Crée un brouillard dense dans la zone cible. Débit et densité modulables."},
  {"id":56,"n":"SILENCE","v":"Oniros","t":"Désert","d":-2,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Absorbe tous les sons dans la zone. Silence absolu — aucun son ne peut ni entrer ni sortir. Idéal pour des conversations discrètes."},
  {"id":57,"n":"TÉNÈBRES","v":"Oniros","t":"Gouffre","d":-4,"c":3,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Crée une zone d'obscurité totale. Aucune lumière ne peut pénétrer dans la zone ni en sortir."},
  {"id":58,"n":"ANTI-MAGIE","v":"Oniros","t":"Plaines","d":-2,"c":"1+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone spéciale","e":"Zone annulant les effets magiques actifs présents dans son périmètre. Les sorts permanents ne sont pas affectés."},
  {"id":59,"n":"APESANTEUR","v":"Oniros","t":"Plaines","d":-5,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone d'apesanteur. Objets et créatures flottent librement. Déplacement possible en se propulsant sur les parois."},
  {"id":60,"n":"AIMANTATION","v":"Oniros","t":"Mont","d":-8,"c":"3+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Aimante puissamment les objets métalliques de la zone vers un point central. Peut désarmer des adversaires ou plaquer des armures contre leur porteur."},
  {"id":61,"n":"ALARME","v":"Oniros","t":"Pont","d":-9,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone spéciale","e":"Déclenche une alarme dès qu'une créature entre dans la zone. Le magicien peut définir les types de créatures déclenchantes. Peut être maintenue pendant le sommeil."},
  {"id":62,"n":"ANNULATION","v":"Oniros","t":"Lac","d":-13,"c":12,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone spéciale","e":"Annule toute magie dans la zone, y compris les enchantements permanents. Les effets reprennent dès que la zone disparaît."},
  {"id":63,"n":"QUIÉTUDE","v":"Oniros","t":"Nécropole","d":-3,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone de quiétude absolue. Calme mental et physique total pour les créatures présentes. Utilisé par certains guérisseurs pour favoriser la récupération."},
  {"id":64,"n":"TÉLÉPORTATION","v":"Oniros","t":"Collines","d":-11,"c":9,"p":"Spéciale","du":"Instantanée","jr":"Aucun","ca":"Rituel","e":"Téléporte la cible à un lieu bien connu du lanceur. La précision dépend de la connaissance du lieu."},
  {"id":65,"n":"RÉTROTÉLÉPORTATION","v":"Oniros","t":"Plaines","d":-11,"c":9,"p":"Spéciale","du":"Instantanée","jr":"Aucun","ca":"Rituel","e":"Retour instantané au dernier point de départ d'une téléportation. Utile si la destination s'avère dangereuse ou incorrecte."},
  {"id":66,"n":"PORTAIL","v":"Oniros","t":"Pont","d":-13,"c":13,"p":"E1","du":"Permanent","jr":"Aucun","ca":"Rituel","e":"Crée un portail permanent reliant deux lieux connus du lanceur. Fonctionne dans les deux sens. Reste actif jusqu'à destruction ou fermeture volontaire."},
  {"id":67,"n":"BOIS CHAUFFÉ","v":"Oniros","t":"Forêt","d":-3,"c":"1+","p":"E2","du":"HN magicien","jr":"Aucun","ca":"Chaleur élémentale","e":"Chauffe sélectivement le bois de la zone. +5°C par point de rêve."},
  {"id":68,"n":"EAU CHAUFFÉE","v":"Oniros","t":"Désert","d":-3,"c":"1+","p":"E2","du":"HN magicien","jr":"Aucun","ca":"Chaleur élémentale","e":"Chauffe sélectivement l'eau de la zone. +5°C par point de rêve. Peut être poussé jusqu'à l'ébullition."},
  {"id":69,"n":"MÉTAL CHAUFFÉ","v":"Oniros","t":"Mont","d":-3,"c":"1+","p":"E2","du":"HN magicien","jr":"Aucun","ca":"Chaleur élémentale","e":"Chauffe sélectivement le métal de la zone. +5°C par point de rêve. Un métal suffisamment chaud inflige des brûlures."},
  {"id":70,"n":"TERRE CHAUFFÉE","v":"Oniros","t":"Désolation","d":-3,"c":"1+","p":"E2","du":"HN magicien","jr":"Aucun","ca":"Chaleur élémentale","e":"Chauffe sélectivement la terre de la zone. +5°C par point de rêve."},
  {"id":71,"n":"BOIS LIQUIDE","v":"Oniros","t":"Lac","d":-7,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Liquéfaction élémentale","e":"Rend liquide comme l'Eau le bois de la zone. L'élément retrouve sa solidité dès qu'il sort de la zone ou quand le sort cesse."},
  {"id":72,"n":"FEU LIQUIDE","v":"Oniros","t":"Mont","d":-11,"c":7,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Liquéfaction élémentale","e":"Rend liquide comme l'Eau le feu de la zone."},
  {"id":720,"n":"TERRE LIQUIDE","v":"Oniros","t":"Marais","d":-5,"c":4,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Liquéfaction élémentale","e":"Rend liquide comme l'Eau la terre de la zone. Retrouve sa solidité dès qu'elle sort de la zone."},
  {"id":721,"n":"MÉTAL LIQUIDE","v":"Oniros","t":"Fleuve","d":-4,"c":4,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Liquéfaction élémentale","e":"Rend liquide comme l'Eau le métal de la zone."},
  {"id":73,"n":"BOUCLIER ÉL./AIR","v":"Oniros","t":"Gouffre","d":-8,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Empêche l'élément Air de pénétrer dans la zone. Zone fixe, totalement invisible."},
  {"id":74,"n":"BOUCLIER ÉL./BOIS","v":"Oniros","t":"Désert","d":-8,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Empêche le Bois de pénétrer dans la zone. Flèches, lances, objets de bois s'arrêtent à sa frontière."},
  {"id":75,"n":"BOUCLIER ÉL./EAU","v":"Oniros","t":"Pont","d":-6,"c":4,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"L'eau libre (pluie, rivière) n'entre pas dans la zone mais ruisselle autour."},
  {"id":76,"n":"BOUCLIER ÉL./FEU","v":"Oniros","t":"Sanctuaire","d":-6,"c":4,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Les flammes d'un incendie contournent la zone. Les torches et bougies peuvent pénétrer dans la zone, mais laissent leurs flammes à l'extérieur."},
  {"id":77,"n":"BOUCLIER ÉL./MÉTAL","v":"Oniros","t":"Marais","d":-8,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Empêche le métal de pénétrer dans la zone. Armes, armures, projectiles métalliques s'arrêtent à sa frontière."},
  {"id":78,"n":"BOUCLIER ÉL./TERRE","v":"Oniros","t":"Désolation","d":-8,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Empêche la Terre de pénétrer dans la zone. Pierres, éboulis, objets de terre s'arrêtent à sa frontière."},
  {"id":79,"n":"PYROMANCIE","v":"Oniros","t":"Collines","d":-11,"c":9,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Rituel","e":"Zone d'AIR EN FEU mobile, rapide, sculptable et contrôlée par le magicien. Peut produire une tornade de feu grégeois. Dommages pouvant aller jusqu'à +dom+11."},
  {"id":300,"n":"EMBÛCHE","v":"Oniros","t":"Forêt","d":-5,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone de piège","e":"Zone dans laquelle il devient délicat de marcher sans trébucher. Pour chaque mètre parcouru, jet d'Agilité à -4 ou la créature s'étale de tout son long."},
  {"id":301,"n":"CAGE","v":"Oniros","t":"Gouffre","d":-8,"c":"5+","p":"E2","du":"1 min/5r puis +1min/r","jr":"Aucun","ca":"Zone de capture","e":"Zone emprisonnant toute créature qui entre entièrement dedans. Zone invisible. En sortir : jet de Force à -5."},
  {"id":302,"n":"BRUIT","v":"Oniros","t":"Cité","d":-4,"c":4,"p":"E3","du":"HN magicien","jr":"Aucun","ca":"Zone sonore","e":"Illusion sonore de n'importe quelle nature semblant venir de l'intérieur de la zone."},
  {"id":303,"n":"PETITE CICATRISATION","v":"Oniros","t":"Cité","d":-4,"c":"1+","p":"E1","du":"HN magicien","jr":"r-8","ca":"Zone de soin","e":"Favorise la cicatrisation naturelle des blessures de toute personne qui y dort jusqu'au château dormant."},
  {"id":304,"n":"GRANDE CICATRISATION","v":"Oniros","t":"Sanctuaire","d":-8,"c":"1+","p":"E1","du":"HN magicien","jr":"r-8","ca":"Zone de soin","e":"Toute personne qui y dort au moins une heure peut effectuer un jet de guérison pour faire rétrograder ses blessures."},
  {"id":305,"n":"COAGULATION","v":"Oniros","t":"Nécropole","d":-6,"c":"1+","p":"E1","du":"HN magicien","jr":"r-8","ca":"Zone de soin","e":"N'affecte que les créatures en hémorragie. Tant que la créature reste dans la zone, les pertes d'endurance s'arrêtent."},
  {"id":306,"n":"BULLE VOLANTE","v":"Oniros","t":"Marais","d":-10,"c":"6+","p":"Toucher","du":"Fin HN + 1h/r","jr":"Aucun","ca":"Zone mobile","e":"Zone mobile de Taille standard, souple, adaptable. Vitesse par défaut : 10 km/h draconique (+10 km/h par r, max 60 km/h)."},
  {"id":307,"n":"BARQUE DE RÊVE","v":"Oniros","t":"Lac","d":-8,"c":"5+","p":"E1","du":"Fin HN + 1h/r","jr":"Aucun","ca":"Zone mobile","e":"Zone mobile pour 5 passagers pour 5r. +1r par passager supplémentaire. Vitesse par défaut : 4 km/h draconique (+2 km/h par r, max 14 km/h)."},
  {"id":308,"n":"MANTEAU","v":"Oniros","t":"Sanctuaire","d":-3,"c":"1+","p":"E1","du":"Fin HN + r","jr":"r-8 et 1r cible","ca":"Zone mobile perso.","e":"Zone Mobile Personnelle (ZMP) : se moule sur le corps et se déplace avec la cible. Entoure la cible d'une température de 25°C."},
  {"id":309,"n":"LUISANCE","v":"Oniros","t":"Désolation","d":-3,"c":"2+","p":"E1","du":"Fin HN + r","jr":"r-8 et 1r cible","ca":"Zone mobile perso.","e":"ZMP : la peau de la victime se met à luire et éclaire comme une bougie."},
  {"id":310,"n":"BOUÉE","v":"Oniros","t":"Pont","d":-3,"c":"3+","p":"E1","du":"Fin HN + r","jr":"r-8 et 1r cible","ca":"Zone mobile perso.","e":"ZMP jouant le rôle d'une bouée. Garde automatiquement la tête et les épaules de la cible hors de l'eau."},
  {"id":311,"n":"HAUBERT D'ONIROS","v":"Oniros","t":"Fleuve","d":-8,"c":"7+","p":"Toucher","du":"Fin HN + r","jr":"r-8 et 1r cible","ca":"Zone mobile perso.","e":"ZMP conférant une protection de 5 points (comme un haubert de mailles). Protège aussi contre : Soufflet (Hypnos), Poing de Thanatos et Fléau de Thanatos."},
  {"id":312,"n":"DÉPLACEMENT DE ZONES","v":"Oniros","t":"Variable","d":-5,"c":4,"p":"E2","du":"Instantanée","jr":"Aucun","ca":"Rituel","e":"Déplace le centre d'une zone que le haut-rêvant a créé. N'affecte ni la durée ni la taille de la zone."},
  # Hypnos
  {"id":100,"n":"BIGLE","v":"Hypnos","t":"Désert","d":-8,"c":5,"p":"E3","du":"HN créature","jr":"-6 ou -9","ca":"Sortilège offensif","e":"Au-delà de 3 mètres, la cible voit systématiquement les choses trop à gauche d'environ deux mètres. Très gênant pour le tir, le lancer et le ciblage de sort."},
  {"id":101,"n":"CHATOUILLES","v":"Hypnos","t":"Cité","d":-4,"c":"1+","p":"EMP×1","du":"1 round/r","jr":"Selon HN","ca":"Sortilège","e":"La cible a l'horrible impression d'être chatouillée partout. Empêche de se concentrer sur quoi que ce soit. Jet de Volonté à -3 pour tenter une action."},
  {"id":102,"n":"CONCENTRATION","v":"Hypnos","t":"Mont","d":-6,"c":2,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Permet de conserver la concentration en TMR tout en n'étant qu'à demi libre de ses mouvements."},
  {"id":103,"n":"ÉGAREMENT","v":"Hypnos","t":"Désolation","d":-4,"c":4,"p":"E1","du":"1 heure+","jr":"Selon HN","ca":"Sortilège","e":"Apport massif de pseudo-souvenirs empêchant toute concentration intellectuelle, manuelle ou verbale."},
  {"id":104,"n":"ÉTHYLISME","v":"Hypnos","t":"Cité","d":-5,"c":"1+","p":"EMP×1","du":"Selon HN","jr":"Selon HN","ca":"Sortilège","e":"La cible subit des effets similaires à une ingestion de boisson alcoolisée."},
  {"id":105,"n":"FATIGUE","v":"Hypnos","t":"Nécropole","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Selon HN","ca":"Sortilège","e":"Provoque l'illusion d'une grande fatigue. La victime marque instantanément 6 cases de fatigue."},
  {"id":106,"n":"FAUCHAGE","v":"Hypnos","t":"Plaines","d":-6,"c":5,"p":"E1","du":"Instantanée","jr":"Selon HN","ca":"Sortilège offensif","e":"Provoque chez la cible l'illusion qu'on vient de lui faucher les jambes, si saisissante que le personnage chute sans pouvoir se rattraper."},
  {"id":107,"n":"FAUX-RÊVE","v":"Hypnos","t":"Désert","d":-6,"c":5,"p":"E1","du":"Instantanée","jr":"Selon HN","ca":"Sortilège","e":"Donne le pseudo-souvenir d'une courte séquence de rêve, néanmoins interprétée comme véritable."},
  {"id":108,"n":"FOU-RIRE","v":"Hypnos","t":"Cité","d":-5,"c":5,"p":"E1","du":"Variable","jr":"Selon HN","ca":"Sortilège","e":"La suggestion d'une idée drôlatique cause un irrépressible fou-rire, automatique le premier round."},
  {"id":109,"n":"GIGUE","v":"Hypnos","t":"Forêt","d":-5,"c":"1+","p":"EMP×1","du":"30 sec/r","jr":"Selon HN","ca":"Sortilège","e":"La cible entend une musique entraînante qui la pousse à danser sans pouvoir s'arrêter, jusqu'à épuisement total ou fin du sort."},
  {"id":110,"n":"GRAND SOMMEIL","v":"Hypnos","t":"Marais","d":-11,"c":8,"p":"E1","du":"Spéciale","jr":"Selon HN","ca":"Sortilège","e":"Plonge la victime dans un sommeil magique que rien, absolument rien, ne peut parvenir à réveiller. Le paramétrage du rituel doit inclure un mot de réveil."},
  {"id":111,"n":"INAUDIBILITÉ","v":"Hypnos","t":"Désolation","d":-9,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Illusion strictement auditive. La cible devient inaudible. En combat : complète surprise à la première attaque."},
  {"id":112,"n":"INSENSIBILITÉ","v":"Hypnos","t":"Mont","d":-8,"c":"1+","p":"EMP×1","du":"Jusqu'à fin prochain HN","jr":"Selon HN","ca":"Sortilège","e":"La cible devient en partie insensible à la douleur. Ne protège pas des coups, juste de la douleur."},
  {"id":113,"n":"INVISIBILITÉ","v":"Hypnos","t":"Fleuve","d":-10,"c":8,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Illusion strictement visuelle rendant la cible invisible. En combat : complète surprise à la première attaque, puis localisé par sa brume limbaire."},
  {"id":114,"n":"LANGUE D'HYPNOS","v":"Hypnos","t":"Cité","d":-3,"c":2,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel","e":"Illusion purement gustative s'appliquant aux objets, aliments et boissons."},
  {"id":115,"n":"LUMINESCENCE","v":"Hypnos","t":"Nécropole","d":-5,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Lumière","e":"Illusion visuelle rendant un objet luminescent. L'objet émet une faible luminosité légèrement bleutée et changeante."},
  {"id":116,"n":"MÉTAMORPHOSE","v":"Hypnos","t":"Gouffre","d":-8,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Illusion purement visuelle changeant l'apparence de la cible pour lui donner celle d'une autre catégorie."},
  {"id":117,"n":"NARINE D'HYPNOS","v":"Hypnos","t":"Plaines","d":-4,"c":3,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Illusion purement olfactive. Fonctionnement identique à Tympan d'Hypnos, mais pour les odeurs."},
  {"id":118,"n":"NUDITÉ D'HYPNOS","v":"Hypnos","t":"Lac","d":-8,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Vêtements et équipement de la cible deviennent invisibles."},
  {"id":119,"n":"ROBE D'HYPNOS","v":"Hypnos","t":"Mont","d":-6,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Variante de Transfiguration s'appliquant à l'ensemble des vêtements et pièces d'équipement de la cible."},
  {"id":120,"n":"ROBE FANTASMAGORIQUE","v":"Hypnos","t":"Gouffre","d":-7,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Ne peut être lancée que sur un humanoïde nu ou sous l'effet de Nudité d'Hypnos. Il est alors possible de lui inventer tous les vêtements imaginables."},
  {"id":121,"n":"TYMPAN D'HYPNOS","v":"Hypnos","t":"Collines","d":-5,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Illusion purement auditive. L'illusion doit rester dans la même catégorie que la cible. Sosie vocal parfait : jet d'OUÏE à -8."},
  {"id":122,"n":"TRANSFIGURATION","v":"Hypnos","t":"Mont","d":-6,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Illusion purement visuelle. Comme Métamorphose, mais l'illusion doit rester dans la même catégorie. Sosie parfait : jet de VUE à -8."},
  {"id":123,"n":"SOMMEIL","v":"Hypnos","t":"Marais","d":-9,"c":"1+","p":"E2","du":"Variable","jr":"Selon HN","ca":"Sortilège","e":"Plonge la cible dans le sommeil. Durée proportionnelle aux points de rêve dépensés."},
  {"id":124,"n":"ILLUSION ANIMALE","v":"Hypnos","t":"Forêt","d":-4,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion complexe","e":"Illusion visuelle et sonore complète d'un animal. Seuls les animaux réellement connus du haut-rêvant peuvent être imités."},
  {"id":125,"n":"ILLUSION GÉOGRAPHIQUE","v":"Hypnos","t":"Gouffre","d":-4,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion complexe","e":"Illusion d'un décor géographique complet (forêt, falaise, rivière...). Très utile pour dissimuler un passage ou créer un leurre."},
  {"id":126,"n":"ILLUSION HUMANOÏDE","v":"Hypnos","t":"Cité","d":-6,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion complexe","e":"Illusion complète d'un humanoïde. Peut être statique ou dotée de mouvements simples (+1r)."},
  {"id":127,"n":"ALLONGEMENT D'ILLUSION","v":"Hypnos","t":"Variable","d":-6,"c":"1+","p":"—","du":"Variable","jr":"Aucun","ca":"Modif. illusion","e":"Prolonge la durée d'une illusion existante. Chaque r supplémentaire : +1 heure de naissance complète."},
  {"id":128,"n":"ÉLOIGNEMENT D'ILLUSION","v":"Hypnos","t":"Variable","d":-5,"c":"1+","p":"—","du":"Variable","jr":"Aucun","ca":"Modif. illusion","e":"Déplace le point d'ancrage d'une illusion existante à une distance choisie."},
  {"id":129,"n":"ANNUL. SES ILLUSIONS","v":"Hypnos","t":"Variable","d":-4,"c":2,"p":"—","du":"Instantanée","jr":"Aucun","ca":"Modif. illusion","e":"Annule toutes ses propres illusions actives instantanément."},
  {"id":130,"n":"PERMANENCE D'ILLUSION","v":"Hypnos","t":"Variable","d":-13,"c":13,"p":"—","du":"Permanente","jr":"Aucun","ca":"Modif. illusion","e":"Rend une illusion permanente, sans maintien actif. L'illusion persistera même après la mort du haut-rêvant."},
  {"id":131,"n":"AURA D'ANGOISSE","v":"Hypnos","t":"Désolation","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"Aura affectant une zone de E1 m autour de la cible. Toute créature entrant dans la zone doit faire un JR r-8 ou ressentir l'angoisse et la peur instinctives."},
  {"id":132,"n":"AURA D'ANTIPATHIE","v":"Hypnos","t":"Nécropole","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Génère l'antipathie instinctive envers la cible."},
  {"id":133,"n":"AURA DE BRAVOURE","v":"Hypnos","t":"Plaines","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Inspire le courage et la bravoure."},
  {"id":134,"n":"AURA DE CONFIANCE","v":"Hypnos","t":"Sanctuaire","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Inspire confiance et sentiment de sécurité. Réduit la méfiance et les doutes."},
  {"id":135,"n":"AURA D'INDOLENCE","v":"Hypnos","t":"Sanctuaire","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Provoque paresse et indolence. Réduit la combativité et la motivation."},
  {"id":136,"n":"AURA DE JOIE","v":"Hypnos","t":"Cité","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Communique la joie et l'allégresse."},
  {"id":137,"n":"AURA DE MÉFIANCE","v":"Hypnos","t":"Marais","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Génère méfiance et suspicion."},
  {"id":138,"n":"AURA DE SYMPATHIE","v":"Hypnos","t":"Collines","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Provoque sympathie et bienveillance spontanées."},
  {"id":139,"n":"AURA DE TRISTESSE","v":"Hypnos","t":"Gouffre","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Communique tristesse et mélancolie."},
  {"id":140,"n":"AMITIÉ ANIMALE","v":"Hypnos","t":"Forêt","d":-8,"c":8,"p":"E2","du":"HN magicien","jr":"Spéciale","ca":"Sortilège","e":"Les animaux présents dans la zone se montrent amicaux avec la cible."},
  {"id":141,"n":"DÉTECTION D'AURA","v":"Hypnos","t":"Sanctuaire","d":-3,"c":1,"p":"E2","du":"1 round","jr":"Aucun","ca":"Rituel de perception","e":"Lit les auras émotionnelles des créatures à portée."},
  {"id":142,"n":"PERCEPTION D'ÉROS","v":"Hypnos","t":"Pont","d":-7,"c":7,"p":"E1","du":"1 heure","jr":"Aucun","ca":"Rituel de perception","e":"Connaît l'émotion principale des personnes visibles et à qui ou quoi elle est adressée."},
  {"id":143,"n":"PRESTANCE","v":"Hypnos","t":"Cité","d":-8,"c":"3+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Pour chaque 3 r : Apparence +1 et +1 à tous les jets de communication."},
  {"id":144,"n":"NÉGATION D'ÉROS","v":"Hypnos","t":"Fleuve","d":-10,"c":8,"p":"E2","du":"HN magicien","jr":"Spéciale","ca":"Sortilège émotionnel","e":"Toutes les émotions vis-à-vis de la cible sont nulles pour la durée du sort, à l'exception de l'Amour véritable."},
  {"id":145,"n":"AMPLIFICATION D'ÉROS","v":"Hypnos","t":"Lac","d":-13,"c":13,"p":"E2","du":"HN magicien","jr":"Spéciale","ca":"Sortilège émotionnel","e":"Exactement comme la Négation d'Éros, mais tous les sentiments envers la cible sont portés au niveau extrême."},
  {"id":146,"n":"QUADRILLE D'HYPNOS","v":"Hypnos","t":"Cité","d":-6,"c":"4+","p":"E2","du":"Variable","jr":"Spéciale","ca":"Sort musical","e":"Support : une danse endiablée. Les personnes ratant leur JR spécial se laissent prendre par le rythme et ne peuvent s'empêcher de danser."},
  {"id":147,"n":"MIROIR D'HYPNOS","v":"Hypnos","t":"Nécropole","d":-5,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel de vision","e":"Voir à distance via un miroir ou surface réfléchissante (obligatoire)."},
  {"id":148,"n":"HARPE D'HYPNOS","v":"Hypnos","t":"Mont","d":-4,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel d'écoute","e":"Entendre à distance via un instrument sonore."},
  {"id":149,"n":"VOIX D'HYPNOS","v":"Hypnos","t":"Désert","d":-4,"c":4,"p":"Personnel","du":"1 round","jr":"Aucun","ca":"Rituel de perception","e":"Permet de détecter le mensonge."},
  {"id":150,"n":"INVOQUER SA VOIX","v":"Hypnos","t":"Cité","d":-6,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel de communication","e":"Négatif de Harpe d'Hypnos. Projette sa voix à distance."},
  {"id":151,"n":"INVOQUER SON IMAGE","v":"Hypnos","t":"Sanctuaire","d":-6,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel de communication","e":"Un hologramme fidèle de lui-même prend naissance près de la personne ou au centre du lieu choisi."},
  {"id":152,"n":"INVOQUER SA PRÉSENCE","v":"Hypnos","t":"Nécropole","d":-9,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel de communication","e":"Synthèse de Miroir + Harpe + Invoquer son Image. Le haut-rêvant voit et entend tandis que son hologramme se forme sur place."},
  {"id":153,"n":"ENCENS D'HYPNOS","v":"Hypnos","t":"Sanctuaire","d":-7,"c":6,"p":"E2","du":"1 round + 1/r","jr":"Aucun","ca":"Rituel","e":"Doit se trouver devant une déchirure du rêve et faire brûler de l'encens. Voit réellement dans l'autre rêve en surimpression dans la fumée."},
  {"id":154,"n":"ENCRE NOIRE D'HYPNOS","v":"Hypnos","t":"Lac","d":-10,"c":"6+","p":"E2","du":"HN + 1h/r sup.","jr":"Aucun","ca":"Rituel du passé","e":"Dans une vasque d'encre, voit se dérouler une scène du passé du lieu. Limite 100 ans, repoussée de 100 ans par 1r."},
  {"id":155,"n":"GONG D'HYPNOS","v":"Hypnos","t":"Marais","d":-9,"c":"5+","p":"E2","du":"HN + 1h/r sup.","jr":"Aucun","ca":"Rituel du passé","e":"Le gong est au son ce que l'Encre Noire est à l'image. Reproduit les sons du passé."},
  {"id":156,"n":"GRAND ENCENS D'HYPNOS","v":"Hypnos","t":"Fleuve","d":-13,"c":"4+","p":"E2","du":"1 round/r","jr":"Aucun","ca":"Rituel","e":"Voir et interagir dans un autre rêve via la déchirure. Synthèse avancée d'Encens d'Hypnos."},
  {"id":400,"n":"SOUFFLET","v":"Hypnos","t":"Gouffre","d":-6,"c":"1+","p":"E1","du":"Fin de l'heure en cours","jr":"Humanoïde selon HN, animal r-8","ca":"Sortilège offensif","e":"Identique à Poing de Thanatos. Le Haubert d'Oniros protège contre ce sort."},
  {"id":401,"n":"SATIÉTÉ","v":"Hypnos","t":"Sanctuaire","d":-4,"c":"3+","p":"E1","du":"HN magicien","jr":"Selon HN","ca":"Sortilège","e":"La suggestion d'un ventre plein permet de se passer pour un temps de nourriture et de boisson."},
  {"id":402,"n":"VUE ACÉRÉE","v":"Hypnos","t":"Fleuve","d":-8,"c":"4+","p":"E1","du":"1 heure","jr":"Selon HN","ca":"Sens acérés","e":"La cible gagne 1 point de Vue pour chaque tranche de 4r dépensés."},
  {"id":403,"n":"OUÏE ACÉRÉE","v":"Hypnos","t":"Lac","d":-8,"c":"4+","p":"E1","du":"1 heure","jr":"Selon HN","ca":"Sens acérés","e":"La cible gagne 1 point d'Ouïe pour chaque tranche de 4r dépensés."},
  {"id":404,"n":"ODORAT/GOÛT AFFINÉ","v":"Hypnos","t":"Marais","d":-3,"c":"2+","p":"E1","du":"1 heure","jr":"Selon HN","ca":"Sens acérés","e":"La cible gagne 1 point d'Odorat/Goût pour chaque tranche de 2r dépensés."},
  {"id":405,"n":"DEXTÉRITÉ AMÉLIORÉE","v":"Hypnos","t":"Fleuve","d":-6,"c":"3+","p":"E1","du":"1 heure","jr":"Selon HN","ca":"Sens acérés","e":"La cible gagne 1 point de Dextérité pour chaque tranche de 3r dépensés."},
  {"id":406,"n":"VIERGE D'OLIS","v":"Hypnos","t":"Sanctuaire","d":-7,"c":8,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Invoque une Vierge d'Olis : jeune fille à beauté éblouissante et voix merveilleuse, mais excessivement farouche."},
  {"id":407,"n":"COURSIERS DE PSARK","v":"Hypnos","t":"Plaines","d":-7,"c":8,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Invoque 2d7 grands chevaux blancs à la crinière et longue queue dorées. Refusent tout lien ou bride."},
  {"id":408,"n":"DESTRIER DE NOAPE","v":"Hypnos","t":"Cité","d":-7,"c":8,"p":"E1","du":"Spéciale","jr":"Aucun","ca":"Rituel d'invocation","e":"Invoque un destrier armuré (cheval de guerre lourd) qui disparaît dès que son cavalier met pied à terre."},
  {"id":409,"n":"FOU DU ROI","v":"Hypnos","t":"Cité","d":-6,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Bouffon petit et agile, n'obéissant qu'au lanceur. Adore faire rire par ses pitreries, imitations et sarcasmes."},
  {"id":410,"n":"ESSAIM DE GUÊPES FURIES","v":"Hypnos","t":"Forêt","d":-4,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Grosses guêpes rayées bleu et noir n'attaquant qu'une seule cible désignée."},
  {"id":411,"n":"SERPENT GLUSK","v":"Hypnos","t":"Forêt","d":-8,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Petit serpent vert-de-gris aux yeux jaune vifs (10-20 cm). Venin paralysant progressif."},
  {"id":412,"n":"ÂNE CORNU","v":"Hypnos","t":"Collines","d":-8,"c":"7+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Bel âne gris avec grandes cornes recourbées, déjà bâté et harnaché. N'obéit qu'au haut-rêvant. Encombrement de 18."},
  {"id":413,"n":"OURF MALHEUREUX","v":"Hypnos","t":"Forêt","d":-9,"c":9,"p":"E1","du":"Tâche","jr":"Aucun","ca":"Rituel d'invocation","e":"Un ourf est une sorte de gros grizzal aux dents de sabre. Toujours très malheureux. Se comporte comme un Guerrier Sorde."},
  {"id":414,"n":"PASSEUR DE YALM","v":"Hypnos","t":"Pont","d":-8,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Petit homme tout de gris, chapeau de feutre mou, longue perche. Service unique : barrer une embarcation en eau douce."},
  {"id":415,"n":"SOUVENIR D'ARCHÉTYPE","v":"Hypnos","t":"Sanctuaire","d":0,"c":0,"p":"EMP×1","du":"1 heure","jr":"Selon HN","ca":"Rituel","e":"Fait remonter à la mémoire le souvenir d'une compétence (sauf le Draconic). Elle vaut pendant une heure son niveau d'archétype."},
  # Narcos
  {"id":200,"v":"Narcos","t":"Pont","n":"BERCEUSE DE NARCOS","d":-5,"c":"4+","p":"E1","du":"Durée du morceau","jr":"Selon HN","ca":"Sort musical","e":"Support : morceau instrumental très lent et presque monocorde. Les auditeurs ratant leur JR spécial bénéficient d'un sommeil sans rêve favorisant la guérison."},
  {"id":201,"v":"Narcos","t":"Cité","n":"INVOCATION MESSAGER","d":-3,"c":"1+","p":"E1","du":"Variable","jr":"Aucun","ca":"Invocation TMR","e":"Invoque un esprit messager des Terres Médianes du Rêve pour transmettre une information précise à une personne distante."},
  {"id":202,"v":"Narcos","t":"Pont","n":"INVOCATION PASSEUR","d":-5,"c":"1+","p":"E1","du":"Variable","jr":"Aucun","ca":"Invocation TMR","e":"Invoque un passeur des Terres Médianes du Rêve pour faciliter le voyage entre les niveaux de rêve."},
  {"id":203,"v":"Narcos","t":"Gouffre","n":"INVOCATION CHANGEUR","d":-7,"c":7,"p":"E1","du":"Variable","jr":"Aucun","ca":"Invocation TMR","e":"Invoque un changeur des Terres Médianes du Rêve. Peut modifier certains aspects de la réalité onirique."},
  {"id":204,"v":"Narcos","t":"Plaines","n":"COURSIERS DE PSARK","d":-8,"c":7,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Invoque 2d7 grands chevaux blancs à la crinière et longue queue dorées."},
  {"id":205,"v":"Narcos","t":"Variable","n":"ESPRITS","d":-1,"c":"Variable","p":"E1","du":"Variable","jr":"Variable","ca":"Invocation","e":"Communique avec ou invoque des esprits divers des TMR. Les résultats sont très variables selon le type d'esprit et la case des TMR."},
  {"id":206,"v":"Narcos","t":"Plaines","n":"ÉCAILLE DE LÉGÈRETÉ","d":-4,"c":5,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Invoque une écaille de Narcos conférant la légèreté au porteur. Son encombrement est divisé par deux."},
  {"id":207,"v":"Narcos","t":"Collines","n":"ÂNE CORNU","d":-8,"c":"7+","p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Bel âne gris avec grandes cornes recourbées. N'obéit qu'au haut-rêvant. Encombrement de 18."},
  {"id":208,"v":"Narcos","t":"Cité","n":"FOU DU ROI","d":-6,"c":6,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Bouffon petit et agile, n'obéissant qu'au lanceur. Adore faire rire."},
  {"id":209,"v":"Narcos","t":"Forêt","n":"ESSAIM DE GUÊPES FURIES","d":-4,"c":5,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Grosses guêpes rayées bleu et noir n'attaquant qu'une seule cible désignée."},
  {"id":210,"v":"Narcos","t":"Forêt","n":"SERPENT GLUSK","d":-8,"c":6,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Petit serpent vert-de-gris aux yeux jaune vifs. Venin paralysant progressif."},
  {"id":211,"v":"Narcos","t":"Forêt","n":"OURF MALHEUREUX","d":-9,"c":9,"p":"E1","du":"Tâche","jr":"Aucun","ca":"Invocation","e":"Un ourf est une sorte de gros grizzal aux dents de sabre. Toujours très malheureux."},
  {"id":212,"v":"Narcos","t":"Pont","n":"PASSEUR DE YALM","d":-8,"c":7,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Petit homme tout de gris, chapeau de feutre mou, longue perche. Service unique : barrer une embarcation en eau douce."},
  {"id":213,"v":"Narcos","t":"Cité","n":"GUERRIER SORDE","d":-8,"c":7,"p":"E1","du":"Tâche","jr":"Aucun","ca":"Invocation","e":"Invoque un guerrier humanoïde armé et équipé. Ne peut accomplir qu'une tâche : combattre."},
  {"id":214,"v":"Narcos","t":"Mont","n":"DAGUE DE FORCE","d":-5,"c":3,"p":"Toucher","du":"HN","jr":"Aucun","ca":"Transformation d'arme","e":"Une dague ainsi modifiée a un +dom de +4. Résistance totale tant que dure le sort."},
  {"id":215,"v":"Narcos","t":"Désolation","n":"DRAGONNE LAME","d":-6,"c":4,"p":"Toucher","du":"HN","jr":"Aucun","ca":"Transformation d'arme","e":"Une épée dragonne ainsi modifiée a un +dom de +6."},
  {"id":216,"v":"Narcos","t":"Forêt","n":"FLÈCHE DE FEU","d":-4,"c":2,"p":"Toucher","du":"HN","jr":"Aucun","ca":"Transformation d'arme","e":"Augmente le tranchant et le pouvoir de pénétration d'une flèche. +dom de +5 et annule 5 points d'armure."},
  {"id":217,"v":"Narcos","t":"Forêt","n":"GOURDIN-DRAGON","d":-7,"c":7,"p":"Toucher","du":"HN","jr":"Aucun","ca":"Transformation d'arme","e":"Transformation radicale d'un morceau de bois en véritable épée dragonne (+dom de +3)."},
  {"id":218,"v":"Narcos","t":"Sanctuaire","n":"SOUVENIR D'ARCHÉTYPE","d":0,"c":0,"p":"EMP×1","du":"1 heure","jr":"Selon HN","ca":"Rituel","e":"Fait remonter à la mémoire le souvenir d'une compétence. Elle vaut pendant une heure son niveau d'archétype."},
  {"id":500,"v":"Narcos","t":"Mont","n":"BOUILLOIRE DE MÉLIMNOD","d":-9,"c":9,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"À poser sur une bouilloire. Dès que la bouilloire est pleine d'eau, elle chauffe spontanément à l'ébullition en 1 round."},
  {"id":501,"v":"Narcos","t":"Lac","n":"PUITS DE RÊVE","d":-8,"c":8,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Tirelire de points de rêve. Chaque Grande Écaille permet de stocker jusqu'à 7r."},
  {"id":502,"v":"Narcos","t":"Mont","n":"GRANDE ÉCAILLE DE MAÎTRISE","d":-7,"c":7,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Fait que le créateur ne maîtrise pas automatiquement l'objet, et qu'il ne peut le maîtriser qu'après avoir rempli certaines conditions précises."},
  {"id":503,"v":"Narcos","t":"Mont","n":"MIROIR DE SOLEIL","d":-14,"c":11,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Posée sur un miroir de métal ou de verre (~20 cm de diamètre), permet de capter et réfléchir la lumière du soleil même si un obstacle s'interpose."},
  {"id":504,"v":"Narcos","t":"Marais","n":"ACCORD DU RÊVE","d":-10,"c":13,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Posée sur une arme, permet de ne pas avoir à réussir de jet de Rêve lorsqu'on touche une entité de cauchemar."},
  {"id":505,"v":"Narcos","t":"Fleuve","n":"GDE ÉCAILLE PURIFICATRICE","d":-6,"c":8,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Posée sur un récipient, transforme en eau alchimiquement pure tout liquide que l'on verse dedans."},
  {"id":506,"v":"Narcos","t":"Gouffre","n":"GDE ÉCAILLE D'INVISIBILITÉ","d":-10,"c":9,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Trois degrés de puissance. Rend invisible à volonté le porteur et l'objet selon le degré activé."},
]

CATS = sorted(set(s["ca"] for s in SORTS))
TL = ["Cité","Collines","Désolation","Désert","Fleuve","Forêt","Gouffre","Lac","Marais","Mont","Nécropole","Plaines","Pont","Sanctuaire"]

# ─── Persistance ────────────────────────────────────────────────────────────
SAVE_FILE = Path.home() / ".rdd_morfehus.json"

def load_state():
    if SAVE_FILE.exists():
        try:
            return json.loads(SAVE_FILE.read_text("utf-8"))
        except Exception:
            pass
    return {}

def save_state(state):
    try:
        SAVE_FILE.write_text(json.dumps(state, ensure_ascii=False), "utf-8")
    except Exception:
        pass

# ─── Application ────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⬡ HAUT-RÊVE · Morfehus")
        self.configure(bg=BG)
        self.geometry("880x720")
        self.minsize(700, 560)

        state = load_state()
        self.pC  = tk.IntVar(value=int(state.get("pC", 22)))
        self.pM  = tk.IntVar(value=int(state.get("pM", 28)))
        self.sdr = tk.IntVar(value=int(state.get("sdr", 22)))
        self.fat = tk.IntVar(value=int(state.get("fat", 0)))
        self.connus   = set(state.get("con", []))
        self.log_data = state.get("log", [])
        self.t_hist   = state.get("tH", [])

        self._build_ui()
        self._refresh_reve()

    # ── Persistance ──
    def _save(self):
        save_state({
            "pC":  self.pC.get(),
            "pM":  self.pM.get(),
            "sdr": self.sdr.get(),
            "fat": self.fat.get(),
            "con": list(self.connus),
            "log": self.log_data[-12:],
            "tH":  self.t_hist[:15],
        })

    # ── UI principale ──
    def _build_ui(self):
        # En-tête
        hdr = tk.Frame(self, bg="#050A14", pady=8, padx=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⬡ HAUT-RÊVE", bg="#050A14", fg=GO,
                 font=("Georgia", 16, "bold")).pack(side="left")
        tk.Label(hdr, text="MORFEHUS · ONIROS · HYPNOS · NARCOS",
                 bg="#050A14", fg=SV, font=("Georgia", 8)).pack(side="left", padx=12)
        self.lbl_pdr = tk.Label(hdr, text="", bg="#050A14", fg=GO,
                                font=("Georgia", 14, "bold"))
        self.lbl_pdr.pack(side="right")
        self.lbl_fat = tk.Label(hdr, text="", bg="#050A14", fg="#22c55e",
                                font=("Georgia", 8))
        self.lbl_fat.pack(side="right", padx=8)

        # Notebook (onglets)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Dark.TNotebook", background=BG, borderwidth=0)
        style.configure("Dark.TNotebook.Tab",
                        background=CD, foreground=SV,
                        padding=[12, 6], font=("Georgia", 10))
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", "#0E1A2E")],
                  foreground=[("selected", GO)])

        nb = ttk.Notebook(self, style="Dark.TNotebook")
        nb.pack(fill="both", expand=True, padx=4, pady=4)

        self._tab_sorts  = self._build_sorts_tab(nb)
        self._tab_reve   = self._build_reve_tab(nb)
        self._tab_fat    = self._build_fat_tab(nb)
        self._tab_tmr    = self._build_tmr_tab(nb)

        nb.add(self._tab_sorts, text="◈  Sorts")
        nb.add(self._tab_reve,  text="◉  Rêve")
        nb.add(self._tab_fat,   text="◈  Fatigue")
        nb.add(self._tab_tmr,   text="◆  TMR")

    # ── Onglet Sorts ──
    def _build_sorts_tab(self, parent):
        frame = tk.Frame(parent, bg=BG)

        # Filtres
        flt = tk.Frame(frame, bg=BG, padx=8, pady=6)
        flt.pack(fill="x")

        tk.Label(flt, text="Recherche :", bg=BG, fg=SV, font=("Georgia", 9)).grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_sorts())
        e = tk.Entry(flt, textvariable=self.search_var, bg="#0D1525", fg=FG,
                     insertbackground=FG, relief="flat",
                     font=("Georgia", 11), width=30)
        e.grid(row=0, column=1, sticky="ew", padx=6)
        flt.columnconfigure(1, weight=1)

        row2 = tk.Frame(flt, bg=BG)
        row2.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4,0))

        tk.Label(row2, text="Voie :", bg=BG, fg=SV, font=("Georgia", 9)).pack(side="left")
        self.fV = tk.StringVar(value="Tous")
        for v in ["Tous", "Oniros", "Hypnos", "Narcos"]:
            c = VC.get(v, {}).get("color", SV)
            tk.Radiobutton(row2, text=v, variable=self.fV, value=v,
                           bg=BG, fg=c, selectcolor=BG, activebackground=BG,
                           activeforeground=c, font=("Georgia", 9),
                           command=self._filter_sorts).pack(side="left", padx=4)

        row3 = tk.Frame(flt, bg=BG)
        row3.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4,0))

        tk.Label(row3, text="TMR :", bg=BG, fg=SV, font=("Georgia", 9)).pack(side="left")
        self.fT = tk.StringVar(value="Tous")
        tmr_opts = ["Tous"] + TL
        om_tmr = ttk.Combobox(row3, textvariable=self.fT, values=tmr_opts,
                               state="readonly", width=14, font=("Georgia", 9))
        om_tmr.pack(side="left", padx=4)
        om_tmr.bind("<<ComboboxSelected>>", lambda _: self._filter_sorts())

        tk.Label(row3, text="Catégorie :", bg=BG, fg=SV, font=("Georgia", 9)).pack(side="left", padx=(8,0))
        self.fC = tk.StringVar(value="Tous")
        cats_opts = ["Tous"] + CATS
        om_cat = ttk.Combobox(row3, textvariable=self.fC, values=cats_opts,
                               state="readonly", width=20, font=("Georgia", 9))
        om_cat.pack(side="left", padx=4)
        om_cat.bind("<<ComboboxSelected>>", lambda _: self._filter_sorts())

        self.sCon = tk.BooleanVar(value=False)
        tk.Checkbutton(row3, text="★ Connus seulement", variable=self.sCon,
                       bg=BG, fg=GO, selectcolor=BG, activebackground=BG,
                       font=("Georgia", 9), command=self._filter_sorts).pack(side="left", padx=8)

        self.lbl_count = tk.Label(flt, text="", bg=BG, fg=SV, font=("Georgia", 8))
        self.lbl_count.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2,0))

        # Liste des sorts
        list_frame = tk.Frame(frame, bg=BG)
        list_frame.pack(fill="both", expand=True, padx=6, pady=4)

        scrollbar = tk.Scrollbar(list_frame, bg=BG, troughcolor=CD)
        scrollbar.pack(side="right", fill="y")

        self.sort_listbox = tk.Listbox(
            list_frame,
            bg=CD, fg=FG, selectbackground="#1A2A40",
            selectforeground=GO, relief="flat", bd=0,
            font=("Courier", 10),
            yscrollcommand=scrollbar.set,
            activestyle="none",
        )
        self.sort_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.sort_listbox.yview)
        self.sort_listbox.bind("<<ListboxSelect>>", self._on_sort_select)

        # Panneau détail
        self.detail_frame = tk.Frame(frame, bg=CD, padx=10, pady=8)
        self.detail_frame.pack(fill="x", padx=6, pady=(0,6))
        self.lbl_detail_title = tk.Label(self.detail_frame, text="",
                                          bg=CD, fg=GO, font=("Georgia", 13, "bold"),
                                          wraplength=740, justify="left")
        self.lbl_detail_title.pack(anchor="w")
        self.lbl_detail_meta = tk.Label(self.detail_frame, text="",
                                         bg=CD, fg=SV, font=("Georgia", 9),
                                         wraplength=740, justify="left")
        self.lbl_detail_meta.pack(anchor="w")
        self.lbl_detail_eff = tk.Label(self.detail_frame, text="",
                                        bg=CD, fg="#CBBCCC", font=("Georgia", 10),
                                        wraplength=740, justify="left")
        self.lbl_detail_eff.pack(anchor="w", pady=(4,0))

        btn_row = tk.Frame(self.detail_frame, bg=CD)
        btn_row.pack(anchor="w", pady=(6,0))
        self.btn_connu = tk.Button(btn_row, text="☆ Marquer connu",
                                    bg=CD, fg=SV, relief="flat",
                                    font=("Georgia", 10), cursor="hand2",
                                    command=self._toggle_connu)
        self.btn_connu.pack(side="left", padx=(0,8))
        self.btn_depenser = tk.Button(btn_row, text="",
                                       bg=CD, fg="#ef4444", relief="flat",
                                       font=("Georgia", 10), cursor="hand2",
                                       command=self._depenser_sort)
        self.btn_depenser.pack(side="left")

        self._sorted_visible = []
        self._selected_sort = None
        self._filter_sorts()
        return frame

    def _filter_sorts(self):
        q    = self.search_var.get().lower()
        fv   = self.fV.get()
        ft   = self.fT.get()
        fc   = self.fC.get()
        scon = self.sCon.get()

        res = []
        for s in SORTS:
            if fv != "Tous" and s["v"] != fv: continue
            if ft != "Tous" and s["t"] != ft: continue
            if fc != "Tous" and s["ca"] != fc: continue
            if scon and s["id"] not in self.connus: continue
            if q:
                if not (q in s["n"].lower() or q in s["ca"].lower() or q in s["e"].lower()):
                    continue
            res.append(s)

        self._sorted_visible = res
        self.sort_listbox.delete(0, "end")
        for s in res:
            vc  = VC.get(s["v"], {})
            g   = vc.get("g", "·")
            d   = str(s["d"])
            c   = str(s["c"]) + "r"
            star = "★" if s["id"] in self.connus else " "
            line = f"{star} {g} {s['n']:<30}  {d:>4}  {c:>5}  {s['t']}"
            self.sort_listbox.insert("end", line)
        self.lbl_count.config(
            text=f"{len(res)} sort{'s' if len(res)!=1 else ''} · {len(self.connus)} connu{'s' if len(self.connus)!=1 else ''}"
        )
        self._selected_sort = None
        self._clear_detail()

    def _on_sort_select(self, event):
        sel = self.sort_listbox.curselection()
        if not sel: return
        s = self._sorted_visible[sel[0]]
        self._selected_sort = s
        vc = VC.get(s["v"], {})
        color = vc.get("color", SV)
        self.lbl_detail_title.config(text=s["n"], fg=color)
        meta = (f"Voie : {s['v']}  ·  TMR : {s['t']}  ·  "
                f"Difficulté : {s['d']}  ·  Coût : {s['c']}r  ·  "
                f"Portée : {s['p']}  ·  Durée : {s['du']}  ·  "
                f"JR : {s['jr']}  ·  Catégorie : {s['ca']}")
        self.lbl_detail_meta.config(text=meta)
        self.lbl_detail_eff.config(text=s["e"])
        star = "★ Connu" if s["id"] in self.connus else "☆ Marquer connu"
        fc = GO if s["id"] in self.connus else SV
        self.btn_connu.config(text=star, fg=fc)
        if isinstance(s["c"], int):
            self.btn_depenser.config(text=f"−{s['c']} r (lancer)")
        else:
            self.btn_depenser.config(text="")

    def _clear_detail(self):
        for w in [self.lbl_detail_title, self.lbl_detail_meta,
                  self.lbl_detail_eff]:
            w.config(text="")
        self.btn_connu.config(text="")
        self.btn_depenser.config(text="")

    def _toggle_connu(self):
        s = self._selected_sort
        if not s: return
        if s["id"] in self.connus:
            self.connus.discard(s["id"])
        else:
            self.connus.add(s["id"])
        self._save()
        self._filter_sorts()
        # Retrouver et resélectionner
        for i, sv in enumerate(self._sorted_visible):
            if sv["id"] == s["id"]:
                self.sort_listbox.selection_set(i)
                self.sort_listbox.see(i)
                self._on_sort_select(None)
                break

    def _depenser_sort(self):
        s = self._selected_sort
        if not s or not isinstance(s["c"], int): return
        self._mod_pdr(-s["c"], s["n"])

    # ── Onglet Rêve ──
    def _build_reve_tab(self, parent):
        frame = tk.Frame(parent, bg=BG)

        # Jauge PdR
        top = tk.Frame(frame, bg=BG)
        top.pack(pady=14)
        self.canvas_pdr = tk.Canvas(top, width=150, height=150,
                                     bg=BG, highlightthickness=0)
        self.canvas_pdr.pack()
        self.lbl_pdr_big = tk.Label(frame, text="", bg=BG, fg=GO,
                                     font=("Georgia", 36, "bold"))
        self.lbl_pdr_big.pack()
        self.lbl_pdr_max = tk.Label(frame, text="", bg=BG, fg=SV,
                                     font=("Georgia", 11))
        self.lbl_pdr_max.pack()

        # Boutons +/-
        btns = tk.Frame(frame, bg=BG)
        btns.pack(pady=8)
        for d in [-10, -5, -3, -1]:
            tk.Button(btns, text=str(d), width=5, height=2,
                      bg="#1A0808", fg="#ef4444", relief="flat",
                      font=("Georgia", 12), cursor="hand2",
                      command=lambda v=d: self._mod_pdr(v, "Dépense")).pack(side="left", padx=3)
        for d in [1, 3, 5, 10]:
            tk.Button(btns, text=f"+{d}", width=5, height=2,
                      bg="#081A08", fg="#22c55e", relief="flat",
                      font=("Georgia", 12), cursor="hand2",
                      command=lambda v=d: self._mod_pdr(v, "Récupération")).pack(side="left", padx=3)

        # Max PdR + Seuil
        cfg_frame = tk.Frame(frame, bg=CD, padx=14, pady=10)
        cfg_frame.pack(fill="x", padx=20, pady=8)
        for label, var in [("Maximum PdR", self.pM), ("Seuil de Rêve", self.sdr)]:
            row = tk.Frame(cfg_frame, bg=CD)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, bg=CD, fg=SV, font=("Georgia", 10)).pack(side="left")
            tk.Button(row, text="−", bg=CD, fg="#ef4444", relief="flat",
                      font=("Georgia", 14), cursor="hand2",
                      command=lambda v=var: (v.set(max(0, v.get()-1)), self._refresh_reve(), self._save())).pack(side="right")
            lbl = tk.Label(row, textvariable=var, bg=CD, fg=GO,
                           font=("Georgia", 16, "bold"), width=3, anchor="center")
            lbl.pack(side="right")
            tk.Button(row, text="+", bg=CD, fg="#22c55e", relief="flat",
                      font=("Georgia", 14), cursor="hand2",
                      command=lambda v=var: (v.set(v.get()+1), self._refresh_reve(), self._save())).pack(side="right")

        # Historique
        tk.Label(frame, text="HISTORIQUE", bg=BG, fg=SV,
                 font=("Georgia", 8), letterSpacing=2 if False else 1).pack(anchor="w", padx=20)
        self.log_frame = tk.Frame(frame, bg=CD)
        self.log_frame.pack(fill="x", padx=20, pady=(4,8))
        self._refresh_log()
        return frame

    def _mod_pdr(self, d, label):
        old = self.pC.get()
        new = max(0, min(self.pM.get(), old + d))
        self.pC.set(new)
        entry = {
            "d": f"+{d}" if d > 0 else str(d),
            "r": label,
            "v": new,
            "t": __import__("datetime").datetime.now().strftime("%H:%M"),
        }
        self.log_data = [entry] + self.log_data[:11]
        self._refresh_reve()
        self._refresh_log()
        self._save()

    def _refresh_reve(self):
        pc = self.pC.get()
        pm = self.pM.get()
        # Couleur
        clr = "#ef4444" if pc <= 5 else "#f97316" if pc <= 10 else GO
        # Canvas arc
        c = self.canvas_pdr
        c.delete("all")
        cx, cy, r = 75, 75, 58
        c.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#1A2030", width=10)
        if pm > 0:
            angle = 360 * pc / pm
            import math
            # Dessiner l'arc en segments
            start_deg = 90
            extent = -angle
            c.create_arc(cx-r, cy-r, cx+r, cy+r,
                         start=start_deg, extent=extent,
                         outline=clr, width=10, style="arc")
        c.create_text(cx, cy-6, text=str(pc), fill=clr,
                      font=("Georgia", 28, "bold"))
        c.create_text(cx, cy+14, text=f"/ {pm} r", fill=SV,
                      font=("Georgia", 9))
        self.lbl_pdr_big.config(text=str(pc), fg=clr)
        self.lbl_pdr_max.config(text=f"/ {pm} r")
        # En-tête
        self.lbl_pdr.config(text=f"{pc} / {pm} r", fg=clr)
        fn = get_fn(self.fat.get())
        self.lbl_fat.config(text=fn["l"], fg=fn["c"])

    def _refresh_log(self):
        for w in self.log_frame.winfo_children():
            w.destroy()
        for e in self.log_data[:10]:
            row = tk.Frame(self.log_frame, bg=CD)
            row.pack(fill="x", pady=1)
            clr = "#ef4444" if e["d"].startswith("-") else "#22c55e"
            tk.Label(row, text=e["d"], bg=CD, fg=clr,
                     font=("Georgia", 10, "bold"), width=4).pack(side="left")
            tk.Label(row, text=e["r"], bg=CD, fg=SV,
                     font=("Georgia", 9)).pack(side="left", padx=4)
            tk.Label(row, text=f"{e['v']}r · {e['t']}", bg=CD, fg="#3A5070",
                     font=("Georgia", 8)).pack(side="right")

    # ── Onglet Fatigue ──
    def _build_fat_tab(self, parent):
        frame = tk.Frame(parent, bg=BG)

        self.lbl_fat_state = tk.Label(frame, text="", bg=BG,
                                       font=("Georgia", 14, "bold"))
        self.lbl_fat_state.pack(pady=(14,2))
        self.lbl_fat_malus = tk.Label(frame, text="", bg=BG, fg=SV,
                                       font=("Georgia", 10))
        self.lbl_fat_malus.pack()

        # Segments
        seg_frame = tk.Frame(frame, bg=BG)
        seg_frame.pack(pady=12, padx=20)
        self.seg_buttons = []
        for i, niv in enumerate(SI):
            btn = tk.Button(
                seg_frame, text="  ", width=3, height=1,
                relief="flat", bd=1, cursor="hand2",
                command=lambda idx=i: self._set_fat(idx)
            )
            btn.grid(row=0, column=i, padx=1)
            self.seg_buttons.append((btn, niv))

        # Légende
        leg = tk.Frame(frame, bg=BG)
        leg.pack(pady=4)
        for niv in FN:
            tk.Label(leg, text=f"  {niv['l']} ({niv['m']})  ",
                     bg=niv["c"], fg="white",
                     font=("Georgia", 8)).pack(side="left", padx=2)

        # Boutons +/-
        btns = tk.Frame(frame, bg=BG)
        btns.pack(pady=10)
        tk.Button(btns, text="+ 1 segment", width=14, height=2,
                  bg="#1A0808", fg="#ef4444", relief="flat",
                  font=("Georgia", 11), cursor="hand2",
                  command=lambda: self._mod_fat(1)).pack(side="left", padx=6)
        tk.Button(btns, text="− 1 segment", width=14, height=2,
                  bg="#081A08", fg="#22c55e", relief="flat",
                  font=("Georgia", 11), cursor="hand2",
                  command=lambda: self._mod_fat(-1)).pack(side="left", padx=6)

        tk.Button(frame, text="Repos complet · Réinitialiser", width=30,
                  bg=CD, fg=SV, relief="flat",
                  font=("Georgia", 10), cursor="hand2",
                  command=lambda: self._mod_fat(-self.fat.get())).pack(pady=4)

        self._refresh_fat()
        return frame

    def _set_fat(self, idx):
        cur = self.fat.get()
        new = idx if idx < cur else idx + 1
        self.fat.set(max(0, min(len(SI)-1, new)))
        self._refresh_fat()
        self._refresh_reve()
        self._save()

    def _mod_fat(self, d):
        self.fat.set(max(0, min(len(SI)-1, self.fat.get() + d)))
        self._refresh_fat()
        self._refresh_reve()
        self._save()

    def _refresh_fat(self):
        f   = self.fat.get()
        fn  = get_fn(f)
        self.lbl_fat_state.config(text=fn["l"], fg=fn["c"])
        if fn["m"] != 0:
            self.lbl_fat_malus.config(text=f"Malus Draconic {fn['m']}", fg=fn["c"])
        else:
            self.lbl_fat_malus.config(text="En forme · aucun malus", fg="#22c55e")
        for i, (btn, niv) in enumerate(self.seg_buttons):
            if i < f:
                btn.config(bg=niv["c"], activebackground=niv["c"])
            else:
                btn.config(bg="#1A2030", activebackground="#1A2030")

    # ── Onglet TMR ──
    def _build_tmr_tab(self, parent):
        frame = tk.Frame(parent, bg=BG, padx=12, pady=10)

        tk.Label(frame, text="MÉMORISER POSITION TMR", bg=BG, fg=SV,
                 font=("Georgia", 9)).pack(anchor="w", pady=(0,6))

        # Type TMR
        type_frame = tk.Frame(frame, bg=BG)
        type_frame.pack(fill="x", pady=4)
        self.tType = tk.StringVar(value="Cité")
        for t in TL:
            c = TC.get(t, SV)
            tk.Radiobutton(type_frame, text=t, variable=self.tType, value=t,
                           bg=BG, fg=c, selectcolor=BG, activebackground=BG,
                           font=("Georgia", 8),
                           command=lambda: None).pack(side="left", padx=2)

        # Coords
        tk.Label(frame, text="Coordonnées (ex: J4, A15…):", bg=BG, fg=SV,
                 font=("Georgia", 9)).pack(anchor="w", pady=(8,2))
        self.tCoords = tk.Entry(frame, bg="#0D1525", fg=FG, insertbackground=FG,
                                 relief="flat", font=("Georgia", 11))
        self.tCoords.pack(fill="x")

        # Note
        tk.Label(frame, text="Note (rencontre, sort, danger…):", bg=BG, fg=SV,
                 font=("Georgia", 9)).pack(anchor="w", pady=(8,2))
        self.tNote = tk.Text(frame, bg="#0D1525", fg=FG, insertbackground=FG,
                              relief="flat", font=("Georgia", 10),
                              height=3, wrap="word")
        self.tNote.pack(fill="x")

        tk.Button(frame, text="⬡ Mémoriser cette case",
                  bg="#0D1A0D", fg="#2ECC71", relief="flat",
                  font=("Georgia", 11), cursor="hand2",
                  command=self._sav_tmr).pack(fill="x", pady=8)

        # Historique TMR
        tk.Label(frame, text="DERNIÈRES POSITIONS", bg=BG, fg=SV,
                 font=("Georgia", 8)).pack(anchor="w")
        self.tmr_hist_frame = tk.Frame(frame, bg=CD)
        self.tmr_hist_frame.pack(fill="both", expand=True, pady=4)
        self._refresh_tmr()
        return frame

    def _sav_tmr(self):
        import datetime
        e = {
            "tp": self.tType.get(),
            "co": self.tCoords.get().strip(),
            "no": self.tNote.get("1.0", "end").strip(),
            "t":  datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        self.t_hist = [e] + self.t_hist[:14]
        self.tCoords.delete(0, "end")
        self.tNote.delete("1.0", "end")
        self._refresh_tmr()
        self._save()

    def _refresh_tmr(self):
        for w in self.tmr_hist_frame.winfo_children():
            w.destroy()
        if not self.t_hist:
            tk.Label(self.tmr_hist_frame, text="Aucune position mémorisée.",
                     bg=CD, fg=SV, font=("Georgia", 10)).pack(pady=16)
            return
        for i, e in enumerate(self.t_hist):
            c = TC.get(e["tp"], "#607D8B")
            row = tk.Frame(self.tmr_hist_frame, bg=CD)
            row.pack(fill="x", padx=6, pady=3)
            tk.Label(row, text=e["tp"], bg=CD, fg=c,
                     font=("Georgia", 9, "bold"), width=12, anchor="w").pack(side="left")
            info = e.get("co", "")
            if e.get("no"): info += f"  –  {e['no'][:60]}"
            tk.Label(row, text=info, bg=CD, fg=FG,
                     font=("Georgia", 9), anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=e.get("t",""), bg=CD, fg=SV,
                     font=("Georgia", 8)).pack(side="right")
            if i == 0:
                tk.Label(row, text="DERNIÈRE", bg=CD, fg=GO,
                         font=("Georgia", 7)).pack(side="right", padx=4)


# ─── Lancement ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
