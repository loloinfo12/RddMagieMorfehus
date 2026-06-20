# -*- coding: utf-8 -*-
"""
RDD — Haut-Rêve · Morfehus
Application Streamlit — aide de jeu pour Rêve de Dragon
"""

import streamlit as st
import json
import math
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# ─── Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⬡ Haut-Rêve · Morfehus",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English&display=swap');
html, body, [data-testid="stAppViewContainer"] {
    background-color: #080D1A !important;
    color: #E8DCC8 !important;
}
[data-testid="stSidebar"] { background-color: #050A14 !important; }
h1,h2,h3,h4 { color: #C0913A !important; font-family: Georgia, serif !important; }
.sort-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    cursor: pointer;
}
.sort-card:hover { border-color: rgba(192,145,58,0.3); }
.sort-card.connu { border-color: rgba(192,145,58,0.25); }
.sort-card.expanded { background: rgba(192,145,58,0.05); border-color: rgba(192,145,58,0.2); }
.badge {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 11px;
    font-weight: bold;
    margin-right: 4px;
}
.diff-easy  { color: #22c55e; }
.diff-med   { color: #eab308; }
.diff-hard  { color: #f97316; }
.diff-xhard { color: #ef4444; }
.metric-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    margin-bottom: 8px;
}
.fat-seg {
    display: inline-block;
    width: 28px; height: 22px;
    border-radius: 4px;
    margin: 2px;
    cursor: pointer;
}
stButton > button {
    font-family: Georgia, serif !important;
}
div[data-testid="stTabs"] button {
    color: #8899AA !important;
    font-family: Georgia, serif !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #C0913A !important;
    border-bottom-color: #C0913A !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Données ──────────────────────────────────────────────────────────────
VC = {
    "Oniros": {"color": "#C0913A", "g": "◈"},
    "Hypnos": {"color": "#9B59B6", "g": "◉"},
    "Narcos": {"color": "#2ECC71", "g": "◆"},
}
TC = {
    "Cité":"#C9A227","Désert":"#C87941","Forêt":"#2A7D2A","Mont":"#7B8D9A",
    "Sanctuaire":"#8B2FC9","Nécropole":"#5C2D91","Pont":"#C84315","Fleuve":"#1565C0",
    "Lac":"#0288D1","Plaines":"#4CAF50","Collines":"#8C9B21","Gouffre":"#283593",
    "Désolation":"#6D4C41","Marais":"#2E7D32","Variable":"#607D8B",
}
TL = ["Cité","Collines","Désolation","Désert","Fleuve","Forêt","Gouffre",
      "Lac","Marais","Mont","Nécropole","Plaines","Pont","Sanctuaire"]

FN = [
    {"l":"En forme",   "s":3, "m":0,  "c":"#22c55e"},
    {"l":"Fatigué −1", "s":3, "m":-1, "c":"#84cc16"},
    {"l":"Fatigué −2", "s":1, "m":-2, "c":"#eab308"},
    {"l":"Fatigué −3", "s":1, "m":-3, "c":"#f97316"},
    {"l":"Fatigué −4", "s":1, "m":-4, "c":"#ef4444"},
    {"l":"Fatigué −5", "s":1, "m":-5, "c":"#dc2626"},
    {"l":"Fatigué −6", "s":1, "m":-6, "c":"#991b1b"},
    {"l":"Épuisé  −7", "s":1, "m":-7, "c":"#450a0a"},
]
SI = []
for n in FN:
    for _ in range(n["s"]):
        SI.append(n)

def get_fn(f):
    r = f
    for n in FN:
        if r <= 0: return n
        if r < n["s"]: return n
        r -= n["s"]
    return FN[-1]

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
  {"id":31,"n":"ARABESQUES","v":"Oniros","t":"Cité","d":-6,"c":5,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Zone contrôlée","e":"Dans cette zone contrôlée, les forces pures dessinent des formes en 3D selon le désir du magicien. Ces assemblages ne sont pas tangibles mais visibles."},
  {"id":32,"n":"ARBRES À ARMES","v":"Oniros","t":"Désolation","d":-10,"c":8,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone offensive","e":"Zone de BOIS EN MÉTAL : les végétaux se transforment partiellement en acier aiguisé. Feuilles → pointes de flèches barbelées, baies → billes pour frondes, tiges → lames de poignards."},
  {"id":33,"n":"BOUCLIER GARDIEN","v":"Oniros","t":"Sanctuaire","d":-8,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Défense","e":"Petite zone mobile et contrôlée de force pure, assez vive et solide pour parer les coups. Résistance de 20."},
  {"id":34,"n":"BOULET","v":"Oniros","t":"Mont","d":-8,"c":6,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Zone d'AIR EN TERRE instantanée produisant toujours de la pierre. Résultat : un boulet de taille variable. En pierre. Dur, rond, et lourd."},
  {"id":35,"n":"BOUQUET D'ARMES","v":"Oniros","t":"Sanctuaire","d":-11,"c":9,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone de MÉTAL EN BOIS transformant le métal en fleurs. Paix et amour..."},
  {"id":36,"n":"BUISSON","v":"Oniros","t":"Collines","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone","e":"Crée un buisson dont la nature (ordinaire) et la forme sont au choix du lanceur."},
  {"id":37,"n":"CARAPACE","v":"Oniros","t":"Sanctuaire","d":-11,"c":9,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Défense","e":"Variation d'AIR EN MÉTAL. Produit une sphère creuse en acier aux murs épais, gravée d'écailles, avec une trappe et huit meurtrières étroites. Un abri parfait."},
  {"id":38,"n":"CLAQUE","v":"Oniros","t":"Cité","d":-5,"c":3,"p":"E2","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Venue de nulle part, une force invisible soufflette la cible. Au mieux, la cible est en demi-surprise pendant un round."},
  {"id":39,"n":"ÉTOILE","v":"Oniros","t":"Plaines","d":-4,"c":2,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Lumière","e":"Variante d'AIR EN FEU : microzone engendrant un feu blanc, froid et presque stable. Pas d'utilité pratique mais très joli."},
  {"id":40,"n":"FAUTEUIL","v":"Oniros","t":"Cité","d":-5,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Confort","e":"Zone créant un siège de forces intangibles. Confort absolu. Permet aussi de flotter assis dans rien."},
  {"id":41,"n":"FILET DE RACINES","v":"Oniros","t":"Forêt","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Zone d'AIR EN BOIS instantanée créant une cage d'épaisses racines entremêlées. Les créatures dans la zone se retrouvent emprisonnées."},
  {"id":42,"n":"FLAMBOIEMENT","v":"Oniros","t":"Désert","d":-8,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone de feu","e":"Zone mobile de MÉTAL EN FEU n'affectant que d'infimes sphères de métal à la fois. Légères étincelles et flammèches."},
  {"id":43,"n":"FLÈCHE DE FEU","v":"Oniros","t":"Mont","d":-7,"c":5,"p":"E3","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Variante d'AIR EN FEU mobile, rapide et instantanée. Créatures touchées : brûlures (+dom+4) et risque de s'enflammer."},
  {"id":44,"n":"GRÊLE MÉTALLIQUE","v":"Oniros","t":"Gouffre","d":-11,"c":9,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone offensive","e":"Éphémère zone d'AIR EN MÉTAL créant une multitude de billes de fer. Redoutables si elles tombent d'assez haut."},
  {"id":45,"n":"LIT DES EAUX","v":"Oniros","t":"Cité","d":-6,"c":4,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Confort","e":"Variante d'EAU EN BOIS. Crée un lit garni de couvertures en lin, d'oreillers rembourrés de feuilles."},
  {"id":46,"n":"MAIN GIGANTE","v":"Oniros","t":"Mont","d":-8,"c":"6+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone contrôlée","e":"Zone contrôlée et mobile sculptée en forme de main invisible (résistance 20). Peut manipuler et soulever toute chose de Taille 8 ou moins."},
  {"id":47,"n":"MARE","v":"Oniros","t":"Plaines","d":-10,"c":8,"p":"E1","du":"Instantanée","jr":"Aucun","ca":"Zone","e":"La Terre prise dans la zone devient aussitôt une jolie mare avec roseaux, nénuphars et lentilles d'eau pour faire vrai."},
  {"id":48,"n":"MORSURE DE LA TERRE","v":"Oniros","t":"Gouffre","d":-11,"c":9,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone offensive","e":"Variante d'AIR EN TERRE créant des stalactites ou stalagmites, tous acérés. Armes cruelles (équivalent gros javelots, +dom+2)."},
  {"id":49,"n":"PLATEAU","v":"Oniros","t":"Cité","d":-4,"c":3,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Variante ludique de la zone de PONT. Mobile, forme exacte au choix. Diamètre limité à 1,5 mètres."},
  {"id":50,"n":"PLUIE","v":"Oniros","t":"Plaines","d":-7,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone d'AIR EN EAU. Débit réglable de la bruine infime à la bonne averse. Le haut-rêve inventa la douche..."},
  {"id":51,"n":"PLUIE DE FLEURS","v":"Oniros","t":"Plaines","d":-9,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone d'AIR EN BOIS créant un nuage de fleurettes bleues charmantes. Leur doux parfum invite au repos : jet de Volonté à -4 ou sommeil irrésistible."},
  {"id":52,"n":"PONT IMMATÉRIEL","v":"Oniros","t":"Pont","d":-6,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Déplacement","e":"Crée un pont de force pure translucide et traversable. Mobile selon le désir du magicien."},
  {"id":53,"n":"RÉCIPIENT","v":"Oniros","t":"Cité","d":-6,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone de forces mobile créant des sphères creuses ouvertes au-dessus. Forme au choix, de la chopine à la baignoire."},
  {"id":54,"n":"TORCHE","v":"Oniros","t":"Cité","d":-7,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Lumière","e":"Micro-zone d'AIR EN FEU (max 10 cm de diamètre), variable et mobile. Réduite à un lumignon : briquet. Inextinguible."},
  {"id":55,"n":"BROUILLARD","v":"Oniros","t":"Forêt","d":-3,"c":"1+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Crée un brouillard dense dans la zone cible. Débit et densité modulables."},
  {"id":56,"n":"SILENCE","v":"Oniros","t":"Désert","d":-2,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Absorbe tous les sons dans la zone. Silence absolu — aucun son ne peut ni entrer ni sortir."},
  {"id":57,"n":"TÉNÈBRES","v":"Oniros","t":"Gouffre","d":-4,"c":3,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Crée une zone d'obscurité totale. Aucune lumière ne peut pénétrer dans la zone ni en sortir."},
  {"id":58,"n":"ANTI-MAGIE","v":"Oniros","t":"Plaines","d":-2,"c":"1+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone spéciale","e":"Zone annulant les effets magiques actifs présents dans son périmètre. Les sorts permanents ne sont pas affectés."},
  {"id":59,"n":"APESANTEUR","v":"Oniros","t":"Plaines","d":-5,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone d'apesanteur. Objets et créatures flottent librement."},
  {"id":60,"n":"AIMANTATION","v":"Oniros","t":"Mont","d":-8,"c":"3+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Aimante puissamment les objets métalliques de la zone vers un point central. Peut désarmer des adversaires."},
  {"id":61,"n":"ALARME","v":"Oniros","t":"Pont","d":-9,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone spéciale","e":"Déclenche une alarme dès qu'une créature entre dans la zone. Peut être maintenue pendant le sommeil."},
  {"id":62,"n":"ANNULATION","v":"Oniros","t":"Lac","d":-13,"c":12,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone spéciale","e":"Annule toute magie dans la zone, y compris les enchantements permanents."},
  {"id":63,"n":"QUIÉTUDE","v":"Oniros","t":"Nécropole","d":-3,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone","e":"Zone de quiétude absolue. Calme mental et physique total pour les créatures présentes."},
  {"id":64,"n":"TÉLÉPORTATION","v":"Oniros","t":"Collines","d":-11,"c":9,"p":"Spéciale","du":"Instantanée","jr":"Aucun","ca":"Rituel","e":"Téléporte la cible à un lieu bien connu du lanceur."},
  {"id":65,"n":"RÉTROTÉLÉPORTATION","v":"Oniros","t":"Plaines","d":-11,"c":9,"p":"Spéciale","du":"Instantanée","jr":"Aucun","ca":"Rituel","e":"Retour instantané au dernier point de départ d'une téléportation."},
  {"id":66,"n":"PORTAIL","v":"Oniros","t":"Pont","d":-13,"c":13,"p":"E1","du":"Permanent","jr":"Aucun","ca":"Rituel","e":"Crée un portail permanent reliant deux lieux connus du lanceur."},
  {"id":67,"n":"BOIS CHAUFFÉ","v":"Oniros","t":"Forêt","d":-3,"c":"1+","p":"E2","du":"HN magicien","jr":"Aucun","ca":"Chaleur élémentale","e":"Chauffe sélectivement le bois de la zone. +5°C par point de rêve."},
  {"id":68,"n":"EAU CHAUFFÉE","v":"Oniros","t":"Désert","d":-3,"c":"1+","p":"E2","du":"HN magicien","jr":"Aucun","ca":"Chaleur élémentale","e":"Chauffe sélectivement l'eau de la zone. +5°C par point de rêve. Peut être poussé jusqu'à l'ébullition."},
  {"id":69,"n":"MÉTAL CHAUFFÉ","v":"Oniros","t":"Mont","d":-3,"c":"1+","p":"E2","du":"HN magicien","jr":"Aucun","ca":"Chaleur élémentale","e":"Chauffe sélectivement le métal de la zone. +5°C par point de rêve."},
  {"id":70,"n":"TERRE CHAUFFÉE","v":"Oniros","t":"Désolation","d":-3,"c":"1+","p":"E2","du":"HN magicien","jr":"Aucun","ca":"Chaleur élémentale","e":"Chauffe sélectivement la terre de la zone. +5°C par point de rêve."},
  {"id":71,"n":"BOIS LIQUIDE","v":"Oniros","t":"Lac","d":-7,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Liquéfaction élémentale","e":"Rend liquide comme l'Eau le bois de la zone."},
  {"id":72,"n":"FEU LIQUIDE","v":"Oniros","t":"Mont","d":-11,"c":7,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Liquéfaction élémentale","e":"Rend liquide comme l'Eau le feu de la zone."},
  {"id":720,"n":"TERRE LIQUIDE","v":"Oniros","t":"Marais","d":-5,"c":4,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Liquéfaction élémentale","e":"Rend liquide comme l'Eau la terre de la zone."},
  {"id":721,"n":"MÉTAL LIQUIDE","v":"Oniros","t":"Fleuve","d":-4,"c":4,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Liquéfaction élémentale","e":"Rend liquide comme l'Eau le métal de la zone."},
  {"id":73,"n":"BOUCLIER ÉL./AIR","v":"Oniros","t":"Gouffre","d":-8,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Empêche l'élément Air de pénétrer dans la zone."},
  {"id":74,"n":"BOUCLIER ÉL./BOIS","v":"Oniros","t":"Désert","d":-8,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Empêche le Bois de pénétrer dans la zone. Flèches, lances, objets de bois s'arrêtent à sa frontière."},
  {"id":75,"n":"BOUCLIER ÉL./EAU","v":"Oniros","t":"Pont","d":-6,"c":4,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"L'eau libre (pluie, rivière) n'entre pas dans la zone mais ruisselle autour."},
  {"id":76,"n":"BOUCLIER ÉL./FEU","v":"Oniros","t":"Sanctuaire","d":-6,"c":4,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Les flammes d'un incendie contournent la zone."},
  {"id":77,"n":"BOUCLIER ÉL./MÉTAL","v":"Oniros","t":"Marais","d":-8,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Empêche le métal de pénétrer dans la zone."},
  {"id":78,"n":"BOUCLIER ÉL./TERRE","v":"Oniros","t":"Désolation","d":-8,"c":6,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Bouclier élémental","e":"Empêche la Terre de pénétrer dans la zone."},
  {"id":79,"n":"PYROMANCIE","v":"Oniros","t":"Collines","d":-11,"c":9,"p":"E2","du":"HN magicien","jr":"Aucun","ca":"Rituel","e":"Zone d'AIR EN FEU mobile, rapide, sculptable et contrôlée par le magicien. Dommages pouvant aller jusqu'à +dom+11."},
  {"id":300,"n":"EMBÛCHE","v":"Oniros","t":"Forêt","d":-5,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Zone de piège","e":"Zone dans laquelle il devient délicat de marcher sans trébucher. Jet d'Agilité à -4 ou la créature s'étale."},
  {"id":301,"n":"CAGE","v":"Oniros","t":"Gouffre","d":-8,"c":"5+","p":"E2","du":"1 min/5r puis +1min/r","jr":"Aucun","ca":"Zone de capture","e":"Zone emprisonnant toute créature qui entre entièrement dedans. Zone invisible. En sortir : jet de Force à -5."},
  {"id":302,"n":"BRUIT","v":"Oniros","t":"Cité","d":-4,"c":4,"p":"E3","du":"HN magicien","jr":"Aucun","ca":"Zone sonore","e":"Illusion sonore de n'importe quelle nature semblant venir de l'intérieur de la zone."},
  {"id":303,"n":"PETITE CICATRISATION","v":"Oniros","t":"Cité","d":-4,"c":"1+","p":"E1","du":"HN magicien","jr":"r-8","ca":"Zone de soin","e":"Favorise la cicatrisation naturelle des blessures. Bonus au jet de guérison égal au nombre de r dépensés."},
  {"id":304,"n":"GRANDE CICATRISATION","v":"Oniros","t":"Sanctuaire","d":-8,"c":"1+","p":"E1","du":"HN magicien","jr":"r-8","ca":"Zone de soin","e":"Toute personne qui y dort au moins une heure peut effectuer un jet de guérison pour faire rétrograder ses blessures."},
  {"id":305,"n":"COAGULATION","v":"Oniros","t":"Nécropole","d":-6,"c":"1+","p":"E1","du":"HN magicien","jr":"r-8","ca":"Zone de soin","e":"N'affecte que les créatures en hémorragie. Tant que la créature reste dans la zone, les pertes d'endurance s'arrêtent."},
  {"id":306,"n":"BULLE VOLANTE","v":"Oniros","t":"Marais","d":-10,"c":"6+","p":"Toucher","du":"Fin HN + 1h/r","jr":"Aucun","ca":"Zone mobile","e":"Zone mobile de Taille standard, souple, adaptable. Vitesse par défaut : 10 km/h draconique."},
  {"id":307,"n":"BARQUE DE RÊVE","v":"Oniros","t":"Lac","d":-8,"c":"5+","p":"E1","du":"Fin HN + 1h/r","jr":"Aucun","ca":"Zone mobile","e":"Zone mobile pour 5 passagers pour 5r. Vitesse par défaut : 4 km/h draconique."},
  {"id":308,"n":"MANTEAU","v":"Oniros","t":"Sanctuaire","d":-3,"c":"1+","p":"E1","du":"Fin HN + r","jr":"r-8 et 1r cible","ca":"Zone mobile perso.","e":"ZMP : se moule sur le corps et se déplace avec la cible. Entoure la cible d'une température de 25°C."},
  {"id":309,"n":"LUISANCE","v":"Oniros","t":"Désolation","d":-3,"c":"2+","p":"E1","du":"Fin HN + r","jr":"r-8 et 1r cible","ca":"Zone mobile perso.","e":"ZMP : la peau de la victime se met à luire et éclaire comme une bougie."},
  {"id":310,"n":"BOUÉE","v":"Oniros","t":"Pont","d":-3,"c":"3+","p":"E1","du":"Fin HN + r","jr":"r-8 et 1r cible","ca":"Zone mobile perso.","e":"ZMP jouant le rôle d'une bouée. Garde automatiquement la tête et les épaules de la cible hors de l'eau."},
  {"id":311,"n":"HAUBERT D'ONIROS","v":"Oniros","t":"Fleuve","d":-8,"c":"7+","p":"Toucher","du":"Fin HN + r","jr":"r-8 et 1r cible","ca":"Zone mobile perso.","e":"ZMP conférant une protection de 5 points. Protège aussi contre : Soufflet (Hypnos), Poing et Fléau de Thanatos."},
  {"id":312,"n":"DÉPLACEMENT DE ZONES","v":"Oniros","t":"Variable","d":-5,"c":4,"p":"E2","du":"Instantanée","jr":"Aucun","ca":"Rituel","e":"Déplace le centre d'une zone que le haut-rêvant a créé. Déplacement instantané."},
  # Hypnos
  {"id":100,"n":"BIGLE","v":"Hypnos","t":"Désert","d":-8,"c":5,"p":"E3","du":"HN créature","jr":"-6 ou -9","ca":"Sortilège offensif","e":"Au-delà de 3 mètres, la cible voit systématiquement les choses trop à gauche d'environ deux mètres. Très gênant pour le tir et le ciblage de sort."},
  {"id":101,"n":"CHATOUILLES","v":"Hypnos","t":"Cité","d":-4,"c":"1+","p":"EMP×1","du":"1 round/r","jr":"Selon HN","ca":"Sortilège","e":"La cible a l'horrible impression d'être chatouillée partout. Jet de Volonté à -3 pour tenter une action."},
  {"id":102,"n":"CONCENTRATION","v":"Hypnos","t":"Mont","d":-6,"c":2,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Permet de conserver la concentration en TMR tout en n'étant qu'à demi libre de ses mouvements."},
  {"id":103,"n":"ÉGAREMENT","v":"Hypnos","t":"Désolation","d":-4,"c":4,"p":"E1","du":"1 heure+","jr":"Selon HN","ca":"Sortilège","e":"Apport massif de pseudo-souvenirs empêchant toute concentration intellectuelle, manuelle ou verbale."},
  {"id":104,"n":"ÉTHYLISME","v":"Hypnos","t":"Cité","d":-5,"c":"1+","p":"EMP×1","du":"Selon HN","jr":"Selon HN","ca":"Sortilège","e":"La cible subit des effets similaires à une ingestion de boisson alcoolisée."},
  {"id":105,"n":"FATIGUE","v":"Hypnos","t":"Nécropole","d":-7,"c":5,"p":"E1","du":"Instantanée","jr":"Selon HN","ca":"Sortilège","e":"Provoque l'illusion d'une grande fatigue. La victime marque instantanément 6 cases de fatigue."},
  {"id":106,"n":"FAUCHAGE","v":"Hypnos","t":"Plaines","d":-6,"c":5,"p":"E1","du":"Instantanée","jr":"Selon HN","ca":"Sortilège offensif","e":"Provoque chez la cible l'illusion qu'on vient de lui faucher les jambes, si saisissante que le personnage chute sans pouvoir se rattraper."},
  {"id":107,"n":"FAUX-RÊVE","v":"Hypnos","t":"Désert","d":-6,"c":5,"p":"E1","du":"Instantanée","jr":"Selon HN","ca":"Sortilège","e":"Donne le pseudo-souvenir d'une courte séquence de rêve, néanmoins interprétée comme véritable."},
  {"id":108,"n":"FOU-RIRE","v":"Hypnos","t":"Cité","d":-5,"c":5,"p":"E1","du":"Variable","jr":"Selon HN","ca":"Sortilège","e":"La suggestion d'une idée drôlatique cause un irrépressible fou-rire, automatique le premier round."},
  {"id":109,"n":"GIGUE","v":"Hypnos","t":"Forêt","d":-5,"c":"1+","p":"EMP×1","du":"30 sec/r","jr":"Selon HN","ca":"Sortilège","e":"La cible entend une musique entraînante qui la pousse à danser sans pouvoir s'arrêter, jusqu'à épuisement total."},
  {"id":110,"n":"GRAND SOMMEIL","v":"Hypnos","t":"Marais","d":-11,"c":8,"p":"E1","du":"Spéciale","jr":"Selon HN","ca":"Sortilège","e":"Plonge la victime dans un sommeil magique que rien ne peut parvenir à réveiller. Le paramétrage doit inclure un mot de réveil."},
  {"id":111,"n":"INAUDIBILITÉ","v":"Hypnos","t":"Désolation","d":-9,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Illusion strictement auditive. La cible devient inaudible. En combat : complète surprise à la première attaque."},
  {"id":112,"n":"INSENSIBILITÉ","v":"Hypnos","t":"Mont","d":-8,"c":"1+","p":"EMP×1","du":"Jusqu'à fin prochain HN","jr":"Selon HN","ca":"Sortilège","e":"La cible devient en partie insensible à la douleur. Ne protège pas des coups, juste de la douleur."},
  {"id":113,"n":"INVISIBILITÉ","v":"Hypnos","t":"Fleuve","d":-10,"c":8,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Illusion strictement visuelle rendant la cible invisible. En combat : complète surprise à la première attaque."},
  {"id":114,"n":"LANGUE D'HYPNOS","v":"Hypnos","t":"Cité","d":-3,"c":2,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel","e":"Illusion purement gustative s'appliquant aux objets, aliments et boissons."},
  {"id":115,"n":"LUMINESCENCE","v":"Hypnos","t":"Nécropole","d":-5,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Lumière","e":"Illusion visuelle rendant un objet luminescent. L'objet émet une faible luminosité légèrement bleutée et changeante."},
  {"id":116,"n":"MÉTAMORPHOSE","v":"Hypnos","t":"Gouffre","d":-8,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Illusion purement visuelle changeant l'apparence de la cible pour lui donner celle d'une autre catégorie."},
  {"id":117,"n":"NARINE D'HYPNOS","v":"Hypnos","t":"Plaines","d":-4,"c":3,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Illusion purement olfactive. L'intensité de l'odeur est celle de la cible."},
  {"id":118,"n":"NUDITÉ D'HYPNOS","v":"Hypnos","t":"Lac","d":-8,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Vêtements et équipement de la cible deviennent invisibles."},
  {"id":119,"n":"ROBE D'HYPNOS","v":"Hypnos","t":"Mont","d":-6,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Variante de Transfiguration s'appliquant à l'ensemble des vêtements et pièces d'équipement de la cible."},
  {"id":120,"n":"ROBE FANTASMAGORIQUE","v":"Hypnos","t":"Gouffre","d":-7,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Ne peut être lancée que sur un humanoïde nu ou sous l'effet de Nudité d'Hypnos. Permet d'inventer tous les vêtements imaginables."},
  {"id":121,"n":"TYMPAN D'HYPNOS","v":"Hypnos","t":"Collines","d":-5,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion sensorielle","e":"Illusion purement auditive. Sosie vocal parfait : jet d'OUÏE à -8."},
  {"id":122,"n":"TRANSFIGURATION","v":"Hypnos","t":"Mont","d":-6,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Illusion purement visuelle. Comme Métamorphose, mais l'illusion doit rester dans la même catégorie. Sosie parfait : jet de VUE à -8."},
  {"id":123,"n":"SOMMEIL","v":"Hypnos","t":"Marais","d":-9,"c":"1+","p":"E2","du":"Variable","jr":"Selon HN","ca":"Sortilège","e":"Plonge la cible dans le sommeil. Durée proportionnelle aux points de rêve dépensés."},
  {"id":124,"n":"ILLUSION ANIMALE","v":"Hypnos","t":"Forêt","d":-4,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion complexe","e":"Illusion visuelle et sonore complète d'un animal. Seuls les animaux réellement connus du haut-rêvant peuvent être imités."},
  {"id":125,"n":"ILLUSION GÉOGRAPHIQUE","v":"Hypnos","t":"Gouffre","d":-4,"c":4,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion complexe","e":"Illusion d'un décor géographique complet (forêt, falaise, rivière...). Très utile pour dissimuler un passage."},
  {"id":126,"n":"ILLUSION HUMANOÏDE","v":"Hypnos","t":"Cité","d":-6,"c":"2+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Illusion complexe","e":"Illusion complète d'un humanoïde. Peut être statique ou dotée de mouvements simples (+1r)."},
  {"id":127,"n":"ALLONGEMENT D'ILLUSION","v":"Hypnos","t":"Variable","d":-6,"c":"1+","p":"—","du":"Variable","jr":"Aucun","ca":"Modif. illusion","e":"Prolonge la durée d'une illusion existante. Chaque r supplémentaire : +1 heure de naissance complète."},
  {"id":128,"n":"ÉLOIGNEMENT D'ILLUSION","v":"Hypnos","t":"Variable","d":-5,"c":"1+","p":"—","du":"Variable","jr":"Aucun","ca":"Modif. illusion","e":"Déplace le point d'ancrage d'une illusion existante à une distance choisie."},
  {"id":129,"n":"ANNUL. SES ILLUSIONS","v":"Hypnos","t":"Variable","d":-4,"c":2,"p":"—","du":"Instantanée","jr":"Aucun","ca":"Modif. illusion","e":"Annule toutes ses propres illusions actives instantanément."},
  {"id":130,"n":"PERMANENCE D'ILLUSION","v":"Hypnos","t":"Variable","d":-13,"c":13,"p":"—","du":"Permanente","jr":"Aucun","ca":"Modif. illusion","e":"Rend une illusion permanente, sans maintien actif. L'illusion persistera même après la mort du haut-rêvant."},
  {"id":131,"n":"AURA D'ANGOISSE","v":"Hypnos","t":"Désolation","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"Toute créature entrant dans la zone doit faire un JR r-8 ou ressentir l'angoisse et la peur instinctives."},
  {"id":132,"n":"AURA D'ANTIPATHIE","v":"Hypnos","t":"Nécropole","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Génère l'antipathie instinctive envers la cible."},
  {"id":133,"n":"AURA DE BRAVOURE","v":"Hypnos","t":"Plaines","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Inspire le courage et la bravoure."},
  {"id":134,"n":"AURA DE CONFIANCE","v":"Hypnos","t":"Sanctuaire","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Inspire confiance et sentiment de sécurité."},
  {"id":135,"n":"AURA D'INDOLENCE","v":"Hypnos","t":"Sanctuaire","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Provoque paresse et indolence."},
  {"id":136,"n":"AURA DE JOIE","v":"Hypnos","t":"Cité","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Communique la joie et l'allégresse."},
  {"id":137,"n":"AURA DE MÉFIANCE","v":"Hypnos","t":"Marais","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Génère méfiance et suspicion."},
  {"id":138,"n":"AURA DE SYMPATHIE","v":"Hypnos","t":"Collines","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Provoque sympathie et bienveillance spontanées."},
  {"id":139,"n":"AURA DE TRISTESSE","v":"Hypnos","t":"Gouffre","d":-6,"c":10,"p":"Personnel","du":"HN magicien","jr":"Aucun","ca":"Aura émotionnelle","e":"JR r-8. Communique tristesse et mélancolie."},
  {"id":140,"n":"AMITIÉ ANIMALE","v":"Hypnos","t":"Forêt","d":-8,"c":8,"p":"E2","du":"HN magicien","jr":"Spéciale","ca":"Sortilège","e":"Les animaux présents dans la zone se montrent amicaux avec la cible."},
  {"id":141,"n":"DÉTECTION D'AURA","v":"Hypnos","t":"Sanctuaire","d":-3,"c":1,"p":"E2","du":"1 round","jr":"Aucun","ca":"Rituel de perception","e":"Lit les auras émotionnelles des créatures à portée."},
  {"id":142,"n":"PERCEPTION D'ÉROS","v":"Hypnos","t":"Pont","d":-7,"c":7,"p":"E1","du":"1 heure","jr":"Aucun","ca":"Rituel de perception","e":"Connaît l'émotion principale des personnes visibles et à qui ou quoi elle est adressée."},
  {"id":143,"n":"PRESTANCE","v":"Hypnos","t":"Cité","d":-8,"c":"3+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Sortilège","e":"Pour chaque 3 r : Apparence +1 et +1 à tous les jets de communication."},
  {"id":144,"n":"NÉGATION D'ÉROS","v":"Hypnos","t":"Fleuve","d":-10,"c":8,"p":"E2","du":"HN magicien","jr":"Spéciale","ca":"Sortilège émotionnel","e":"Toutes les émotions vis-à-vis de la cible sont nulles pour la durée du sort, à l'exception de l'Amour véritable."},
  {"id":145,"n":"AMPLIFICATION D'ÉROS","v":"Hypnos","t":"Lac","d":-13,"c":13,"p":"E2","du":"HN magicien","jr":"Spéciale","ca":"Sortilège émotionnel","e":"Comme la Négation d'Éros, mais tous les sentiments envers la cible sont portés au niveau extrême."},
  {"id":146,"n":"QUADRILLE D'HYPNOS","v":"Hypnos","t":"Cité","d":-6,"c":"4+","p":"E2","du":"Variable","jr":"Spéciale","ca":"Sort musical","e":"Support : une danse endiablée. Les personnes ratant leur JR et un jet de VOLONTÉ se laissent prendre par le rythme."},
  {"id":147,"n":"MIROIR D'HYPNOS","v":"Hypnos","t":"Nécropole","d":-5,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel de vision","e":"Voir à distance via un miroir ou surface réfléchissante (obligatoire)."},
  {"id":148,"n":"HARPE D'HYPNOS","v":"Hypnos","t":"Mont","d":-4,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel d'écoute","e":"Entendre à distance via un instrument sonore. 1 round par r dépensé."},
  {"id":149,"n":"VOIX D'HYPNOS","v":"Hypnos","t":"Désert","d":-4,"c":4,"p":"Personnel","du":"1 round","jr":"Aucun","ca":"Rituel de perception","e":"Permet de détecter le mensonge en réécoutant mentalement une conversation."},
  {"id":150,"n":"INVOQUER SA VOIX","v":"Hypnos","t":"Cité","d":-6,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel de communication","e":"Projette sa voix à distance. Communication à sens unique."},
  {"id":151,"n":"INVOQUER SON IMAGE","v":"Hypnos","t":"Sanctuaire","d":-6,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel de communication","e":"Un hologramme fidèle de lui-même prend naissance près de la personne ou au centre du lieu choisi."},
  {"id":152,"n":"INVOQUER SA PRÉSENCE","v":"Hypnos","t":"Nécropole","d":-9,"c":"1+","p":"E1","du":"1 round/r","jr":"Aucun","ca":"Rituel de communication","e":"Synthèse de Miroir + Harpe + Invoquer son Image. Peut parler, entendre, dialoguer, mais sans substance."},
  {"id":153,"n":"ENCENS D'HYPNOS","v":"Hypnos","t":"Sanctuaire","d":-7,"c":6,"p":"E2","du":"1 round + 1/r","jr":"Aucun","ca":"Rituel","e":"Doit se trouver devant une déchirure du rêve et faire brûler de l'encens. Voit dans l'autre rêve en surimpression."},
  {"id":154,"n":"ENCRE NOIRE D'HYPNOS","v":"Hypnos","t":"Lac","d":-10,"c":"6+","p":"E2","du":"HN + 1h/r sup.","jr":"Aucun","ca":"Rituel du passé","e":"Dans une vasque d'encre, voit se dérouler une scène du passé du lieu. Limite 100 ans."},
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
  {"id":408,"n":"DESTRIER DE NOAPE","v":"Hypnos","t":"Cité","d":-7,"c":8,"p":"E1","du":"Spéciale","jr":"Aucun","ca":"Rituel d'invocation","e":"Invoque un destrier armuré qui disparaît dès que son cavalier met pied à terre."},
  {"id":409,"n":"FOU DU ROI","v":"Hypnos","t":"Cité","d":-6,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Bouffon petit et agile, n'obéissant qu'au lanceur. Adore faire rire par ses pitreries, imitations et sarcasmes."},
  {"id":410,"n":"ESSAIM DE GUÊPES FURIES","v":"Hypnos","t":"Forêt","d":-4,"c":5,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Grosses guêpes rayées bleu et noir n'attaquant qu'une seule cible désignée."},
  {"id":411,"n":"SERPENT GLUSK","v":"Hypnos","t":"Forêt","d":-8,"c":6,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Petit serpent vert-de-gris aux yeux jaune vifs. Venin paralysant progressif."},
  {"id":412,"n":"ÂNE CORNU","v":"Hypnos","t":"Collines","d":-8,"c":"7+","p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Bel âne gris avec grandes cornes recourbées. N'obéit qu'au haut-rêvant. Encombrement de 18."},
  {"id":413,"n":"OURF MALHEUREUX","v":"Hypnos","t":"Forêt","d":-9,"c":9,"p":"E1","du":"Tâche","jr":"Aucun","ca":"Rituel d'invocation","e":"Un ourf est une sorte de gros grizzal aux dents de sabre. Toujours très malheureux."},
  {"id":414,"n":"PASSEUR DE YALM","v":"Hypnos","t":"Pont","d":-8,"c":7,"p":"E1","du":"HN magicien","jr":"Aucun","ca":"Rituel d'invocation","e":"Petit homme tout de gris, chapeau de feutre mou, longue perche. Service : barrer une embarcation en eau douce."},
  {"id":415,"n":"SOUVENIR D'ARCHÉTYPE","v":"Hypnos","t":"Sanctuaire","d":0,"c":0,"p":"EMP×1","du":"1 heure","jr":"Selon HN","ca":"Rituel","e":"Fait remonter à la mémoire le souvenir d'une compétence. Elle vaut pendant une heure son niveau d'archétype."},
  # Narcos
  {"id":200,"v":"Narcos","t":"Pont","n":"BERCEUSE DE NARCOS","d":-5,"c":"4+","p":"E1","du":"Durée du morceau","jr":"Selon HN","ca":"Sort musical","e":"Support : morceau instrumental très lent. Les auditeurs ratant leur JR bénéficient d'un sommeil favorisant la guérison."},
  {"id":201,"v":"Narcos","t":"Cité","n":"INVOCATION MESSAGER","d":-3,"c":"1+","p":"E1","du":"Variable","jr":"Aucun","ca":"Invocation TMR","e":"Invoque un esprit messager des Terres Médianes du Rêve pour transmettre une information précise à une personne distante."},
  {"id":202,"v":"Narcos","t":"Pont","n":"INVOCATION PASSEUR","d":-5,"c":"1+","p":"E1","du":"Variable","jr":"Aucun","ca":"Invocation TMR","e":"Invoque un passeur des Terres Médianes du Rêve pour faciliter le voyage entre les niveaux de rêve."},
  {"id":203,"v":"Narcos","t":"Gouffre","n":"INVOCATION CHANGEUR","d":-7,"c":7,"p":"E1","du":"Variable","jr":"Aucun","ca":"Invocation TMR","e":"Invoque un changeur des Terres Médianes du Rêve. Peut modifier certains aspects de la réalité onirique."},
  {"id":204,"v":"Narcos","t":"Plaines","n":"COURSIERS DE PSARK","d":-8,"c":7,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Invoque 2d7 grands chevaux blancs à la crinière et longue queue dorées."},
  {"id":205,"v":"Narcos","t":"Variable","n":"ESPRITS","d":-1,"c":"Variable","p":"E1","du":"Variable","jr":"Variable","ca":"Invocation","e":"Communique avec ou invoque des esprits divers des TMR. Les résultats sont très variables."},
  {"id":206,"v":"Narcos","t":"Plaines","n":"ÉCAILLE DE LÉGÈRETÉ","d":-4,"c":5,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Invoque une écaille de Narcos conférant la légèreté au porteur. Son encombrement est divisé par deux."},
  {"id":207,"v":"Narcos","t":"Collines","n":"ÂNE CORNU","d":-8,"c":"7+","p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Bel âne gris avec grandes cornes recourbées. N'obéit qu'au haut-rêvant. Encombrement de 18."},
  {"id":208,"v":"Narcos","t":"Cité","n":"FOU DU ROI","d":-6,"c":6,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Bouffon petit et agile, n'obéissant qu'au lanceur."},
  {"id":209,"v":"Narcos","t":"Forêt","n":"ESSAIM DE GUÊPES FURIES","d":-4,"c":5,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Grosses guêpes rayées bleu et noir n'attaquant qu'une seule cible désignée."},
  {"id":210,"v":"Narcos","t":"Forêt","n":"SERPENT GLUSK","d":-8,"c":6,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Petit serpent vert-de-gris aux yeux jaune vifs. Venin paralysant progressif."},
  {"id":211,"v":"Narcos","t":"Forêt","n":"OURF MALHEUREUX","d":-9,"c":9,"p":"E1","du":"Tâche","jr":"Aucun","ca":"Invocation","e":"Un ourf est une sorte de gros grizzal aux dents de sabre. Toujours très malheureux."},
  {"id":212,"v":"Narcos","t":"Pont","n":"PASSEUR DE YALM","d":-8,"c":7,"p":"E1","du":"HN","jr":"Aucun","ca":"Invocation","e":"Petit homme tout de gris, chapeau de feutre mou, longue perche. Service : barrer une embarcation en eau douce."},
  {"id":213,"v":"Narcos","t":"Cité","n":"GUERRIER SORDE","d":-8,"c":7,"p":"E1","du":"Tâche","jr":"Aucun","ca":"Invocation","e":"Invoque un guerrier humanoïde armé et équipé. Ne peut accomplir qu'une tâche : combattre."},
  {"id":214,"v":"Narcos","t":"Mont","n":"DAGUE DE FORCE","d":-5,"c":3,"p":"Toucher","du":"HN","jr":"Aucun","ca":"Transformation d'arme","e":"Une dague ainsi modifiée a un +dom de +4."},
  {"id":215,"v":"Narcos","t":"Désolation","n":"DRAGONNE LAME","d":-6,"c":4,"p":"Toucher","du":"HN","jr":"Aucun","ca":"Transformation d'arme","e":"Une épée dragonne ainsi modifiée a un +dom de +6."},
  {"id":216,"v":"Narcos","t":"Forêt","n":"FLÈCHE DE FEU","d":-4,"c":2,"p":"Toucher","du":"HN","jr":"Aucun","ca":"Transformation d'arme","e":"Augmente le tranchant d'une flèche. +dom de +5 et annule 5 points d'armure."},
  {"id":217,"v":"Narcos","t":"Forêt","n":"GOURDIN-DRAGON","d":-7,"c":7,"p":"Toucher","du":"HN","jr":"Aucun","ca":"Transformation d'arme","e":"Transformation radicale d'un morceau de bois en véritable épée dragonne (+dom de +3)."},
  {"id":218,"v":"Narcos","t":"Sanctuaire","n":"SOUVENIR D'ARCHÉTYPE","d":0,"c":0,"p":"EMP×1","du":"1 heure","jr":"Selon HN","ca":"Rituel","e":"Fait remonter à la mémoire le souvenir d'une compétence. Elle vaut pendant une heure son niveau d'archétype."},
  {"id":500,"v":"Narcos","t":"Mont","n":"BOUILLOIRE DE MÉLIMNOD","d":-9,"c":9,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Posée sur une bouilloire. Dès que la bouilloire est pleine d'eau, elle chauffe spontanément à l'ébullition en 1 round."},
  {"id":501,"v":"Narcos","t":"Lac","n":"PUITS DE RÊVE","d":-8,"c":8,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Tirelire de points de rêve. Chaque Grande Écaille permet de stocker jusqu'à 7r."},
  {"id":502,"v":"Narcos","t":"Mont","n":"GRANDE ÉCAILLE DE MAÎTRISE","d":-7,"c":7,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Fait que le créateur ne maîtrise pas automatiquement l'objet, et qu'il ne peut le maîtriser qu'après certaines conditions précises."},
  {"id":503,"v":"Narcos","t":"Mont","n":"MIROIR DE SOLEIL","d":-14,"c":11,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Posée sur un miroir, permet de capter et réfléchir la lumière du soleil même si un obstacle s'interpose."},
  {"id":504,"v":"Narcos","t":"Marais","n":"ACCORD DU RÊVE","d":-10,"c":13,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Posée sur une arme, permet de ne pas avoir à réussir de jet de Rêve lorsqu'on touche une entité de cauchemar."},
  {"id":505,"v":"Narcos","t":"Fleuve","n":"GDE ÉCAILLE PURIFICATRICE","d":-6,"c":8,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Posée sur un récipient, transforme en eau alchimiquement pure tout liquide que l'on verse dedans."},
  {"id":506,"v":"Narcos","t":"Gouffre","n":"GDE ÉCAILLE D'INVISIBILITÉ","d":-10,"c":9,"p":"Toucher","du":"Permanente (pose)","jr":"Aucun","ca":"Grande Écaille","e":"Trois degrés de puissance. Rend invisible à volonté le porteur et l'objet selon le degré activé."},
]

CATS = sorted(set(s["ca"] for s in SORTS))

TMR_X = ['A','B','C','D','E','F','G','H','I','J','K','L','M']
TMR_Y = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15']
# La grille a 189 cases : 14 lignes complètes (A-M) + 1 ligne partielle (A15-G15)
TMR_TOTAL = 189

def tmr_valid(xi, yi):
    """Retourne True si la case (xi, yi) existe dans la grille (0-indexed)."""
    return yi * 13 + xi < TMR_TOTAL

_TC_RAW = [
    'Cité','Désert','Désolation','Forêt','Plaines','Nécropole','Plaines','Gouffre','Collines','Sanctuaire','Désolation','Plaines','Fleuve','Collines','Cité',
    'Plaines','Collines','Plaines','Mont','Collines','Forêt','Marais','Fleuve','Lac','Mont','Cité','Fleuve','Gouffre','Nécropole',
    'Nécropole','Marais','Fleuve','Pont','Marais','Cité','Fleuve','Forêt','Mont','Marais','Pont','Lac','Désert','Forêt','Plaines',
    'Fleuve','Cité','Gouffre','Lac','Fleuve','Fleuve','Plaines','Cité','Pont','Fleuve','Désolation','Collines','Cité','Sanctuaire',
    'Mont','Plaines','Forêt','Plaines','Mont','Sanctuaire','Forêt','Plaines','Fleuve','Gouffre','Lac','Mont','Plaines','Mont','Forêt',
    'Cité','Lac','Fleuve','Fleuve','Cité','Fleuve','Fleuve','Lac','Plaines','Marais','Cité','Nécropole','Forêt','Plaines',
    'Désolation','Marais','Gouffre','Sanctuaire','Pont','Marais','Cité','Plaines','Désert','Cité','Fleuve','Plaines','Plaines','Désert','Plaines',
    'Lac','Collines','Forêt','Plaines','Désert','Mont','Gouffre','Forêt','Collines','Plaines','Fleuve','Collines','Désolation','Plaines',
    'Plaines','Forêt','Mont','Plaines','Désolation','Nécropole','Plaines','Fleuve','Fleuve','Lac','Pont','Gouffre','Mont','Cité','Mont',
    'Mont','Désert','Cité','Collines','Marais','Lac','Fleuve','Mont','Marais','Fleuve','Plaines','Cité','Gouffre','Désert',
    'Cité','Forêt','Plaines','Pont','Fleuve','Désolation','Cité','Désert','Sanctuaire','Plaines','Cité','Désolation','Forêt','Nécropole','Collines',
    'Fleuve','Fleuve','Lac','Sanctuaire','Collines','Forêt','Gouffre','Mont','Collines','Désert','Collines','Plaines','Mont','Plaines',
    'Cité','Nécropole','Mont','Gouffre','Cité','Désolation','Désert','Plaines','Nécropole','Forêt','Cité','Collines','Plaines','Désolation','Cité',
]

_NOM_RAW = [
    'VIDE','de MIEUX','de DEMAIN','de FALCONAX','de TRILKH','de ZNIAK','de l\'ARC','de SHOK','de KORREX','d\'OLIS','d\'HIER','SAGES','','de STOLIS','de MIELH',
    'd\'ASSORH','de DAWELL','de RUBEGA','CRÂNEURS','de TANEGV','de BUST','BLUANTS','','de LUCRE','SALÉS','de BRILZ','','des LITIGES','de GORLO',
    'de KROAK','GLIGNANTS','','de GIOLI','FLOUANTS','PAVOIS','','TURMIDE','TUMÉFIÉS','de DOM','de ROI','de FRICASA','de NEIGE','de BISSAM','de TOUÉ',
    '','de FROST','d\'OKI','de FOAM','','','d\'AFFA','d\'OLAK','d\'ORX','','de PARTOUT','d\'HUAÏ','SORDIDE','PLAT',
    'de KANAÏ','de FIASK','d\'ESTOUBH','d\'ORTI','BRÛLANTS','de PLAINE','de GLUSKS','d\'IOLISE','','de JUNK','de GLINSTER','AJOURÉS','de XNEZ','de QUATH','des FURIES',
    'GLAUQUE','de MISÈRE','','','de PANOPLE','','','des CHATS','de FOE','ZULTANTS','de NOAPE','de THROAT','des CRIS','BRISÉES',
    'de JAMAIS','NUISANTS','de SUN','BLANC','d\'IK','GLUTANTS','de TERWA','SANS JOIE','de SEL','de SERGAL','','de LUFMIL','CALCAIRES','de SEK','des SOUPIRS',
    'd\'ANTICALME','de PARTA','de GANNA','de PSARK','de KRANE','GURDES','de KAFPA','d\'OURF','de NOIRSEUL','NOIRES','','de TOOTH','de RIEN','BLANCHES',
    'GRISES','FADE','GRINÇANTS','de XIAX','de TOUJOURS','de XOTAR','de TROO','','','WANITO','de YALM','ABIMEUX','BIGLEUX','DESTITUÉE','des DRAGÉES',
    'FAINÉANTS','de POLY','VENIN','d\'ENCRE','de JAB','d\'IAUPE','','BARASK','GRONCHANTS','','de MILTIAR','FOLLE','de GROMPH','de SANIK',
    'd\'ONKAUSE','TAMÉE','de DOIS','de FAH','','de POOR','de KOLIX','de FUMÉE','NOIR','JAUNES','TONNERRE','d\'AMOUR','de KLUTH','d\'ANTINÉAR','POURPRES',
    '','','LAINEUX','MAUVE','SUAVES','GUEUSE','d\'ÉPISOPHE','TAVELÉS','CORNUES','de NICROP','de KOL','VENTEUSES','DORMANTS','de JISLITH',
    'JALOUSE','de LOGOS','de VDAH','GRISANT','RIMARDE','de PRESQUE','de LAVE','LAVÉES','de ZONAR','de JAJOU','CRAPAUD','RÉVULSANTES','d\'ANJOU','d\'APRÈS','de KLANA',
]

# Normalisation clés : "Mont" dans la carte → "Mont" dans TC
_TC_NORM = {"Mont": "Mont"}  # identique, déjà normalisé

def tmr_idx(x_letter, y_num):
    """Retourne l'index dans les tableaux (0-based), x=colonne A-M, y=ligne 1-15."""
    xi = TMR_X.index(x_letter)
    yi = int(y_num) - 1
    return yi * 13 + xi

def tmr_cell(x_letter, y_num):
    xi = TMR_X.index(x_letter)
    yi = int(y_num) - 1
    if not tmr_valid(xi, yi):
        return {"type": "—", "nom": "", "full": "Case inexistante", "x": x_letter, "y": y_num, "idx": -1}
    idx  = yi * 13 + xi
    typ  = _TC_RAW[idx]
    nom  = _NOM_RAW[idx]
    full = f"{typ}s {nom}".strip() if nom else typ
    return {"type": typ, "nom": nom, "full": full, "x": x_letter, "y": y_num, "idx": idx}


# ─── Neon / PostgreSQL ────────────────────────────────────────────────────
# La connexion string est lue depuis st.secrets["DATABASE_URL"]
# Dans .streamlit/secrets.toml (local) ou Secrets sur Streamlit Cloud :
#   DATABASE_URL = "postgresql://user:pwd@ep-xxx.neon.tech/neondb?sslmode=require"

def get_conn():
    """Nouvelle connexion à chaque appel — Neon coupe les connexions inactives."""
    return psycopg2.connect(st.secrets["DATABASE_URL"], sslmode="require",
                            connect_timeout=10)

def db_init():
    """Crée la table si elle n'existe pas encore."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS personnage (
                    id         TEXT PRIMARY KEY DEFAULT 'default',
                    pC         INTEGER NOT NULL DEFAULT 22,
                    pM         INTEGER NOT NULL DEFAULT 28,
                    sdr        INTEGER NOT NULL DEFAULT 22,
                    fat        INTEGER NOT NULL DEFAULT 0,
                    connus     JSONB   NOT NULL DEFAULT '[]',
                    log        JSONB   NOT NULL DEFAULT '[]',
                    t_hist     JSONB   NOT NULL DEFAULT '[]',
                    tmr_cases  JSONB   NOT NULL DEFAULT '{}'
                );
                INSERT INTO personnage (id) VALUES ('default')
                ON CONFLICT (id) DO NOTHING;
                ALTER TABLE personnage ADD COLUMN IF NOT EXISTS
                    tmr_cases JSONB NOT NULL DEFAULT '{}';
            """)
        conn.commit()
    finally:
        conn.close()

def db_load():
    """Charge l'état depuis Neon."""
    db_init()
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM personnage WHERE id = 'default';")
            row = cur.fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()

def db_save():
    """Persiste l'état courant dans Neon."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE personnage SET
                    pC        = %s,
                    pM        = %s,
                    sdr       = %s,
                    fat       = %s,
                    connus    = %s,
                    log       = %s,
                    t_hist    = %s,
                    tmr_cases = %s
                WHERE id = 'default';
            """, (
                st.session_state.pC,
                st.session_state.pM,
                st.session_state.sdr,
                st.session_state.fat,
                json.dumps(list(st.session_state.connus)),
                json.dumps(st.session_state.log[:12]),
                json.dumps(st.session_state.t_hist[:15]),
                json.dumps(st.session_state.tmr_cases),
            ))
        conn.commit()
    finally:
        conn.close()

# ─── Session state (initialisé depuis Neon au premier chargement) ─────────
def init_state():
    if "db_loaded" not in st.session_state:
        try:
            row = db_load()
            st.session_state.pC        = int(row.get("pc",  22))
            st.session_state.pM        = int(row.get("pm",  28))
            st.session_state.sdr       = int(row.get("sdr", 22))
            st.session_state.fat       = int(row.get("fat",  0))
            st.session_state.connus    = set(row.get("connus") or [])
            st.session_state.log       = list(row.get("log")   or [])
            st.session_state.t_hist    = list(row.get("t_hist") or [])
            # tmr_cases : dict { str(sort_id) -> { "A1": 45, "B3": 60, … } }
            raw_tc = row.get("tmr_cases") or {}
            st.session_state.tmr_cases = {str(k): dict(v) for k, v in raw_tc.items()}
        except Exception as e:
            st.warning(f"⚠️ Base de données inaccessible, mode hors-ligne : {e}")
            st.session_state.pC        = 22
            st.session_state.pM        = 28
            st.session_state.sdr       = 22
            st.session_state.fat       = 0
            st.session_state.connus    = set()
            st.session_state.log       = []
            st.session_state.t_hist    = []
            st.session_state.tmr_cases = {}
        st.session_state.exp_sort  = None
        st.session_state.db_loaded = True

init_state()

# ─── Helpers ──────────────────────────────────────────────────────────────
def diff_color(d):
    if isinstance(d, int):
        if d >= -4:  return "diff-easy"
        if d >= -7:  return "diff-med"
        if d >= -10: return "diff-hard"
        return "diff-xhard"
    return ""

def pdr_color(pc, pm):
    if pc <= 5:  return "#ef4444"
    if pc <= 10: return "#f97316"
    return "#C0913A"

def mod_pdr(delta, label):
    old = st.session_state.pC
    new = max(0, min(st.session_state.pM, old + delta))
    st.session_state.pC = new
    entry = {
        "d": f"+{delta}" if delta > 0 else str(delta),
        "r": label,
        "v": new,
        "t": datetime.now().strftime("%H:%M"),
    }
    st.session_state.log = [entry] + st.session_state.log[:11]
    db_save()

# ─── En-tête ──────────────────────────────────────────────────────────────
fn  = get_fn(st.session_state.fat)
pc  = st.session_state.pC
pm  = st.session_state.pM
clr = pdr_color(pc, pm)

st.markdown(f"""
<div style="background:linear-gradient(135deg,#050A14,#0E1A2E);
            padding:12px 20px;border-bottom:1px solid rgba(255,255,255,0.08);
            display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
  <div>
    <span style="color:#C0913A;font-size:22px;font-weight:bold;font-family:Georgia,serif">⬡ HAUT-RÊVE</span>
    <span style="color:#3A5070;font-size:10px;margin-left:12px;letter-spacing:2px">MORFEHUS · ONIROS · HYPNOS · NARCOS</span>
  </div>
  <div style="text-align:right">
    <span style="color:{clr};font-size:24px;font-weight:bold">{pc}</span>
    <span style="color:#3A5070;font-size:12px"> / {pm} r</span>
    <div style="color:{fn['c']};font-size:10px;margin-top:2px">{fn['l']}{' (Drac. ' + str(fn['m']) + ')' if fn['m']!=0 else ' · Forme'}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Onglets ──────────────────────────────────────────────────────────────
tab_sorts, tab_reve, tab_fat, tab_tmr = st.tabs(["◈  Sorts", "◉  Rêve", "◈  Fatigue", "◆  TMR"])

# ══════════════════════════════════════════════════════════════════════════
# SORTS
# ══════════════════════════════════════════════════════════════════════════
with tab_sorts:
    c1, c2 = st.columns([1, 2])
    with c1:
        q    = st.text_input("🔍 Recherche", placeholder="Nom, effet, catégorie…", label_visibility="collapsed")
        voie = st.radio("Voie", ["Tous", "Oniros", "Hypnos", "Narcos"], horizontal=True)
        tmr_f = st.selectbox("Case TMR", ["Tous"] + TL)
        cat_f = st.selectbox("Catégorie", ["Tous"] + CATS)
        scon  = st.checkbox("★ Connus seulement")

    # Filtrage
    res = []
    for s in SORTS:
        if voie != "Tous" and s["v"] != voie: continue
        if tmr_f != "Tous" and s["t"] != tmr_f: continue
        if cat_f != "Tous" and s["ca"] != cat_f: continue
        if scon and s["id"] not in st.session_state.connus: continue
        if q:
            qq = q.lower()
            if not (qq in s["n"].lower() or qq in s["ca"].lower() or qq in s["e"].lower()):
                continue
        res.append(s)

    with c2:
        st.caption(f"{len(res)} sort{'s' if len(res)!=1 else ''} · {len(st.session_state.connus)} connu{'s' if len(st.session_state.connus)!=1 else ''}")

        for s in res:
            vc   = VC.get(s["v"], {"color":"#888","g":"·"})
            tc   = TC.get(s["t"], "#607D8B")
            star = "★" if s["id"] in st.session_state.connus else "☆"
            d    = s["d"]
            dc   = diff_color(d)
            is_exp = st.session_state.exp_sort == s["id"]

            border = f"1px solid {vc['color']}44" if is_exp else ("1px solid rgba(192,145,58,.2)" if s["id"] in st.session_state.connus else "1px solid rgba(255,255,255,0.08)")
            bg     = f"{vc['color']}0D" if is_exp else "rgba(255,255,255,0.04)"

            st.markdown(f"""
<div style="background:{bg};border:{border};border-radius:10px;
            padding:10px 14px;margin-bottom:6px;cursor:pointer">
  <div style="display:flex;align-items:center;gap:8px">
    <span style="color:{vc['color']};font-size:11px;
          background:{vc['color']}18;border:1px solid {vc['color']}33;
          border-radius:4px;padding:2px 5px">{vc['g']}</span>
    <span style="flex:1;font-weight:bold;color:{'#E8DCC8' if s['id'] in st.session_state.connus else '#7A8A9A'}">{star} {s['n']}</span>
    <span class="{dc}" style="font-size:11px;font-weight:bold">{d}</span>
    <span style="color:{tc};font-size:10px;background:{tc}22;
          border:1px solid {tc}33;border-radius:4px;padding:2px 5px">{s['t']}</span>
  </div>
  <div style="color:#9B8FAA;font-size:10px;margin-top:4px">
    {s['c']}r · <span style="color:#566070">{s['ca']} · {s['p']}</span>
  </div>
</div>""", unsafe_allow_html=True)

            btn_cols = st.columns([3, 1, 1])
            with btn_cols[0]:
                lbl = f"{'▼' if is_exp else '▶'} {s['n']}"
                if st.button(lbl, key=f"exp_{s['id']}", use_container_width=True):
                    st.session_state.exp_sort = None if is_exp else s["id"]
                    st.rerun()
            with btn_cols[1]:
                star_lbl = "★ Connu" if s["id"] in st.session_state.connus else "☆ Marquer"
                if st.button(star_lbl, key=f"con_{s['id']}", use_container_width=True):
                    if s["id"] in st.session_state.connus:
                        st.session_state.connus.discard(s["id"])
                    else:
                        st.session_state.connus.add(s["id"])
                    db_save()
                    st.rerun()
            with btn_cols[2]:
                if isinstance(s["c"], int) and s["c"] > 0:
                    if st.button(f"−{s['c']} r", key=f"dep_{s['id']}", use_container_width=True):
                        mod_pdr(-s["c"], s["n"])
                        st.rerun()

            if is_exp:
                cols6 = st.columns(3)
                metas = [("Difficulté", str(s["d"])), ("Coût", f"{s['c']} r"), ("Portée", s["p"]),
                         ("Durée", s["du"]), ("JR", s["jr"]), ("Catégorie", s["ca"])]
                for i, (k, v) in enumerate(metas):
                    with cols6[i % 3]:
                        st.markdown(f"""<div style="background:rgba(255,255,255,0.04);
                            border-radius:5px;padding:5px 8px;margin-bottom:4px">
                            <div style="color:#3A5070;font-size:9px">{k}</div>
                            <div style="color:#CCC;font-size:11px">{v}</div></div>""",
                            unsafe_allow_html=True)
                st.markdown(f"""<div style="background:{vc['color']}06;border-top:1px solid {vc['color']}1A;
                    padding:10px 4px;color:#CBBCCC;font-size:12px;line-height:1.7">{s['e']}</div>""",
                    unsafe_allow_html=True)

                # ── Cases TMR maîtrisées (uniquement pour les sorts connus) ──
                if s["id"] in st.session_state.connus:
                    sid = str(s["id"])
                    # Toutes les cases du bon type pour ce sort
                    sort_type = s["t"]
                    # Cas "Variable" : on propose toutes les cases
                    if sort_type == "Variable":
                        cases_dispo = [
                            f"{x}{y}" for yi, y in enumerate(TMR_Y)
                            for xi, x in enumerate(TMR_X)
                            if tmr_valid(xi, yi)
                        ]
                    else:
                        cases_dispo = [
                            f"{x}{y}" for yi, y in enumerate(TMR_Y)
                            for xi, x in enumerate(TMR_X)
                            if tmr_valid(xi, yi) and _TC_RAW[yi * 13 + xi] == sort_type
                        ]

                    cases_sort = st.session_state.tmr_cases.get(sid, {})
                    tc_color   = TC2.get(sort_type, "#607D8B")

                    st.markdown(f"""
<div style="border-top:1px solid rgba(255,255,255,0.08);margin-top:10px;padding-top:10px">
  <span style="color:{tc_color};font-size:10px;font-weight:bold;letter-spacing:1px">
    ⬡ CASES TMR MAÎTRISÉES · {sort_type.upper()}
    ({len(cases_sort)}/{len(cases_dispo)} cases)
  </span>
</div>""", unsafe_allow_html=True)

                    # Cases déjà ajoutées
                    if cases_sort:
                        pills_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0">'
                        for coord, pct in sorted(cases_sort.items()):
                            # Couleur selon % : rouge→orange→vert
                            if pct < 30:   pc_col = "#ef4444"
                            elif pct < 60: pc_col = "#f97316"
                            elif pct < 85: pc_col = "#eab308"
                            else:          pc_col = "#22c55e"
                            pills_html += (
                                f'<span style="background:{tc_color}22;border:1px solid {tc_color}55;'
                                f'border-radius:6px;padding:4px 8px;font-size:11px;color:{tc_color}">'
                                f'{coord} <span style="color:{pc_col};font-weight:bold">{pct}%</span></span>'
                            )
                        pills_html += '</div>'
                        st.markdown(pills_html, unsafe_allow_html=True)

                        # Contrôles par case existante
                        for coord in sorted(cases_sort.keys()):
                            pct = cases_sort[coord]
                            ccols = st.columns([2, 1, 1, 1, 1])
                            with ccols[0]:
                                # Nom de la case
                                cx = coord[0]
                                cy = coord[1:]
                                if cx in TMR_X and cy in TMR_Y:
                                    idx_c = TMR_Y.index(cy) * 13 + TMR_X.index(cx)
                                    nom_c = _NOM_RAW[idx_c]
                                    st.markdown(
                                        f'<span style="color:{tc_color};font-size:11px">'
                                        f'<b>{coord}</b>'
                                        f'{"  " + nom_c if nom_c else ""}</span>',
                                        unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<span style="color:{tc_color};font-size:11px"><b>{coord}</b></span>',
                                                unsafe_allow_html=True)
                            with ccols[1]:
                                if st.button("−1", key=f"tmrc_dec_{sid}_{coord}", use_container_width=True):
                                    new_pct = max(0, pct - 1)
                                    st.session_state.tmr_cases.setdefault(sid, {})[coord] = new_pct
                                    db_save(); st.rerun()
                            with ccols[2]:
                                if pct >= 100: pct_col = "#22c55e"
                                elif pct >= 60: pct_col = "#eab308"
                                else: pct_col = "#f97316"
                                st.markdown(
                                    f'<div style="text-align:center;color:{pct_col};font-weight:bold;'
                                    f'font-size:14px;padding:4px">{pct}%</div>',
                                    unsafe_allow_html=True)
                            with ccols[3]:
                                if st.button("+1", key=f"tmrc_inc_{sid}_{coord}", use_container_width=True):
                                    new_pct = min(100, pct + 1)
                                    st.session_state.tmr_cases.setdefault(sid, {})[coord] = new_pct
                                    db_save(); st.rerun()
                            with ccols[4]:
                                if st.button("✕", key=f"tmrc_del_{sid}_{coord}", use_container_width=True):
                                    st.session_state.tmr_cases.get(sid, {}).pop(coord, None)
                                    if not st.session_state.tmr_cases.get(sid):
                                        st.session_state.tmr_cases.pop(sid, None)
                                    db_save(); st.rerun()

                    # Sélecteur pour ajouter une nouvelle case
                    cases_non_ajoutees = [c for c in cases_dispo if c not in cases_sort]
                    if cases_non_ajoutees:
                        add_cols = st.columns([3, 1])
                        with add_cols[0]:
                            new_case = st.selectbox(
                                "Ajouter une case",
                                ["—"] + cases_non_ajoutees,
                                key=f"tmrc_add_sel_{sid}",
                                label_visibility="collapsed",
                            )
                        with add_cols[1]:
                            if st.button("＋ Ajouter", key=f"tmrc_add_btn_{sid}",
                                         use_container_width=True, disabled=(new_case == "—")):
                                if new_case != "—":
                                    st.session_state.tmr_cases.setdefault(sid, {})[new_case] = 0
                                    db_save(); st.rerun()
                    else:
                        st.markdown('<span style="color:#22c55e;font-size:10px">✓ Toutes les cases maîtrisées !</span>',
                                    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# RÊVE
# ══════════════════════════════════════════════════════════════════════════
with tab_reve:
    pc  = st.session_state.pC
    pm  = st.session_state.pM
    clr = pdr_color(pc, pm)

    # Arc SVG
    r_svg = 60
    circ  = 2 * math.pi * r_svg
    filled = circ * pc / max(pm, 1)
    st.markdown(f"""
<div style="text-align:center;padding:14px 0">
  <svg width="150" height="150" viewBox="0 0 150 150">
    <circle cx="75" cy="75" r="{r_svg}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="11"/>
    <circle cx="75" cy="75" r="{r_svg}" fill="none" stroke="{clr}" stroke-width="11"
      stroke-dasharray="{filled:.1f} {circ:.1f}"
      stroke-linecap="round"
      stroke-dashoffset="{circ*0.25:.1f}"
      style="transition:stroke-dasharray .4s ease"/>
    <text x="75" y="70" text-anchor="middle" fill="{clr}"
      font-family="Georgia,serif" font-size="30" font-weight="bold">{pc}</text>
    <text x="75" y="90" text-anchor="middle" fill="#3A5070"
      font-family="Georgia,serif" font-size="11">/ {pm} r</text>
  </svg>
</div>""", unsafe_allow_html=True)

    # Boutons PdR
    cols_neg = st.columns(4)
    for i, d in enumerate([-10, -5, -3, -1]):
        with cols_neg[i]:
            if st.button(str(d), key=f"pdr{d}", use_container_width=True):
                mod_pdr(d, "Dépense"); st.rerun()
    cols_pos = st.columns(4)
    for i, d in enumerate([1, 3, 5, 10]):
        with cols_pos[i]:
            if st.button(f"+{d}", key=f"pdrp{d}", use_container_width=True):
                mod_pdr(d, "Récupération"); st.rerun()

    st.divider()

    # Max PdR + Seuil
    col_a, col_b = st.columns(2)
    with col_a:
        new_pm = st.number_input("Maximum PdR", min_value=1, max_value=100,
                                  value=st.session_state.pM, step=1)
        if new_pm != st.session_state.pM:
            st.session_state.pM = new_pm; db_save(); st.rerun()
    with col_b:
        new_sdr = st.number_input("Seuil de Rêve", min_value=0, max_value=100,
                                   value=st.session_state.sdr, step=1)
        if new_sdr != st.session_state.sdr:
            st.session_state.sdr = new_sdr; db_save(); st.rerun()

    # Historique
    if st.session_state.log:
        st.markdown("**HISTORIQUE**")
        for e in st.session_state.log[:10]:
            clr_e = "#ef4444" if e["d"].startswith("-") else "#22c55e"
            st.markdown(
                f'<span style="color:{clr_e};font-weight:bold;min-width:32px;display:inline-block">{e["d"]}</span>'
                f'<span style="color:#8899AA;margin-left:8px">{e["r"]}</span>'
                f'<span style="color:#3A5070;float:right;font-size:10px">{e["v"]}r · {e["t"]}</span>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# FATIGUE
# ══════════════════════════════════════════════════════════════════════════
with tab_fat:
    fat = st.session_state.fat
    fn  = get_fn(fat)

    st.markdown(f"""
<div style="text-align:center;padding:10px 0 6px">
  <div style="font-size:20px;font-weight:bold;color:{fn['c']};font-family:Georgia,serif">{fn['l']}</div>
  <div style="font-size:12px;color:{fn['c']};opacity:.8;margin-top:2px">
    {"Malus Draconic " + str(fn['m']) if fn['m'] != 0 else "En forme · aucun malus"}
  </div>
</div>""", unsafe_allow_html=True)

    # Segments
    segs_html = '<div style="display:flex;flex-wrap:wrap;gap:4px;margin:12px 0">'
    for i, niv in enumerate(SI):
        bg = niv["c"] if i < fat else "rgba(255,255,255,0.07)"
        segs_html += f'<div style="width:32px;height:24px;border-radius:4px;background:{bg};border:1px solid {niv["c"] if i < fat else "rgba(255,255,255,0.1)"}"></div>'
    segs_html += '</div>'
    st.markdown(segs_html, unsafe_allow_html=True)

    # Contrôles
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("＋ 1 segment", use_container_width=True):
            st.session_state.fat = min(len(SI)-1, fat+1); db_save(); st.rerun()
    with col2:
        if st.button("－ 1 segment", use_container_width=True, disabled=fat==0):
            st.session_state.fat = max(0, fat-1); db_save(); st.rerun()
    with col3:
        if st.button("Repos complet", use_container_width=True, disabled=fat==0):
            st.session_state.fat = 0; db_save(); st.rerun()

    # Légende
    st.markdown("---")
    leg_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">'
    for niv in FN:
        leg_html += f'<span style="background:{niv["c"]};color:white;border-radius:4px;padding:3px 8px;font-size:10px">{niv["l"]} ({niv["m"]})</span>'
    leg_html += '</div>'
    st.markdown(leg_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# DONNÉES CARTE TMR
# ══════════════════════════════════════════════════════════════════════════
# Couleurs par type (version normalisée "Mont" comme dans _TC_RAW)
TC2 = {
    "Cité":       "#C9A227",
    "Désert":     "#C87941",
    "Désolation": "#6D4C41",
    "Forêt":      "#2A7D2A",
    "Mont":       "#7B8D9A",
    "Sanctuaire": "#8B2FC9",
    "Nécropole":  "#5C2D91",
    "Pont":       "#C84315",
    "Fleuve":     "#1565C0",
    "Lac":        "#0288D1",
    "Plaines":    "#4CAF50",
    "Collines":   "#8C9B21",
    "Gouffre":    "#283593",
    "Marais":     "#2E7D32",
}

def build_tmr_svg(sel_x=None, sel_y=None, hist_coords=None):
    """Génère le SVG de la carte TMR 13×15."""
    CW, CH = 46, 32   # largeur/hauteur d'une cellule
    OX, OY = 28, 22   # offset pour les labels
    W = OX + 13 * CW + 4
    H = OY + 15 * CH + 4

    hist_set = set()
    if hist_coords:
        for hc in hist_coords:
            if len(hc) >= 2 and hc[0] in TMR_X:
                yn = hc[1:]
                if yn in TMR_Y:
                    hist_set.add((hc[0], yn))

    lines = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="font-family:monospace">']
    # Fond
    lines.append(f'<rect width="{W}" height="{H}" fill="#050A14"/>')

    # Colonnes labels (A-M)
    for xi, lx in enumerate(TMR_X):
        cx = OX + xi * CW + CW // 2
        lines.append(f'<text x="{cx}" y="14" text-anchor="middle" fill="#3A5070" font-size="10">{lx}</text>')

    # Lignes labels (1-15)
    for yi, ly in enumerate(TMR_Y):
        cy = OY + yi * CH + CH // 2 + 4
        lines.append(f'<text x="13" y="{cy}" text-anchor="middle" fill="#3A5070" font-size="10">{ly}</text>')

    # Cellules
    for yi, yv in enumerate(TMR_Y):
        for xi, xv in enumerate(TMR_X):
            if not tmr_valid(xi, yi):
                continue
            idx  = yi * 13 + xi
            typ  = _TC_RAW[idx]
            nom  = _NOM_RAW[idx]
            col  = TC2.get(typ, "#333")
            rx   = OX + xi * CW
            ry   = OY + yi * CH

            is_sel  = (xv == sel_x and yv == sel_y)
            is_hist = (xv, yv) in hist_set

            fill   = col + "55" if not is_sel else col + "CC"
            stroke = "#C0913A" if is_sel else (col + "AA" if is_hist else col + "44")
            sw     = 2 if (is_sel or is_hist) else 1

            lines.append(
                f'<rect x="{rx+1}" y="{ry+1}" width="{CW-2}" height="{CH-2}" '
                f'rx="3" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
            )
            # Label type (3 premières lettres)
            abr = typ[:3].upper()
            lines.append(
                f'<text x="{rx+CW//2}" y="{ry+CH//2+1}" text-anchor="middle" '
                f'dominant-baseline="middle" fill="{col}" font-size="8" font-weight="bold">{abr}</text>'
            )
            # Étoile si hist
            if is_hist and not is_sel:
                lines.append(
                    f'<text x="{rx+CW-5}" y="{ry+9}" text-anchor="middle" fill="#C0913A" font-size="8">★</text>'
                )
            # Pion position actuelle
            if is_sel:
                lines.append(
                    f'<circle cx="{rx+CW//2}" cy="{ry+CH//2}" r="7" fill="#C0913A" opacity="0.9"/>'
                )
                lines.append(
                    f'<text x="{rx+CW//2}" y="{ry+CH//2+4}" text-anchor="middle" fill="#050A14" font-size="9" font-weight="bold">⬡</text>'
                )

    lines.append('</svg>')
    return '\n'.join(lines)


# ══════════════════════════════════════════════════════════════════════════
# TMR (onglet)
# ══════════════════════════════════════════════════════════════════════════
with tab_tmr:

    col_map, col_panel = st.columns([3, 2])

    with col_panel:
        st.markdown("#### ⬡ Position TMR")

        sel_x = st.selectbox("Colonne", TMR_X, key="tmr_sel_x")
        xi_cur = TMR_X.index(st.session_state.get("tmr_sel_x", "A"))
        lignes_valides = [y for yi, y in enumerate(TMR_Y) if tmr_valid(xi_cur, yi)]
        sel_y = st.selectbox("Ligne", lignes_valides, key="tmr_sel_y")

        # Info case sélectionnée
        cell = tmr_cell(sel_x, sel_y)
        tc   = TC2.get(cell["type"], "#888")
        st.markdown(f"""
<div style="background:{tc}18;border:1px solid {tc}44;border-radius:8px;padding:10px 14px;margin:8px 0">
  <div style="color:{tc};font-weight:bold;font-size:13px">{cell['type']}</div>
  <div style="color:#E8DCC8;font-size:11px;margin-top:2px">{cell['nom'] or '—'}</div>
  <div style="color:#3A5070;font-size:9px;margin-top:4px">{sel_x}{sel_y} · case {cell['idx']+1}</div>
</div>""", unsafe_allow_html=True)

        t_note = st.text_area("Note (rencontre, sort, danger…)", key="tmr_note", height=72)

        if st.button("⬡ Mémoriser cette case", use_container_width=True):
            entry = {
                "tp": cell["type"],
                "co": f"{sel_x}{sel_y}",
                "no": t_note.strip(),
                "t":  datetime.now().strftime("%d/%m %H:%M"),
            }
            st.session_state.t_hist = [entry] + st.session_state.t_hist[:14]
            db_save()
            st.rerun()

        st.divider()
        st.markdown("**Historique**")
        if not st.session_state.t_hist:
            st.markdown('<div style="color:#3A5070;font-size:11px">Aucune position mémorisée.</div>',
                        unsafe_allow_html=True)
        else:
            for i, e in enumerate(st.session_state.t_hist):
                c    = TC2.get(e["tp"], "#607D8B")
                info = e.get("no", "")[:50]
                badge = "★ " if i == 0 else ""
                st.markdown(
                    f'<div style="border-left:3px solid {c};padding:3px 8px;margin-bottom:4px;font-size:11px">'
                    f'<span style="color:{c};font-weight:bold">{badge}{e.get("co","?")} · {e["tp"]}</span>'
                    f'{"<br><span style=\\'color:#8899AA\\'>" + info + "</span>" if info else ""}'
                    f'<span style="color:#3A5070;float:right;font-size:9px">{e.get("t","")}</span>'
                    f'</div>',
                    unsafe_allow_html=True)

    with col_map:
        st.markdown("#### Carte des Terres Médianes du Rêve")
        # Coordonnées historiques pour marquage
        hist_coords = [e.get("co","") for e in st.session_state.t_hist]
        svg = build_tmr_svg(
            sel_x=st.session_state.get("tmr_sel_x", "A"),
            sel_y=st.session_state.get("tmr_sel_y", "1"),
            hist_coords=hist_coords,
        )
        st.markdown(svg, unsafe_allow_html=True)

        # Légende compacte
        leg = '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px">'
        for typ, col in TC2.items():
            leg += f'<span style="background:{col}33;border:1px solid {col}66;color:{col};border-radius:4px;padding:2px 6px;font-size:9px">{typ[:3].upper()} {typ}</span>'
        leg += '</div>'
        st.markdown(leg, unsafe_allow_html=True)
