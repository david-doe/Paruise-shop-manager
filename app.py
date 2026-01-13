import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import urllib.parse
import random

# --- 1. CONFIGURATION (OBLIGATOIRE EN PREMIER) ---
st.set_page_config(page_title="Paruise Shop Manager", page_icon="👑", layout="wide")

# GESTION PLOTLY (ANTI-CRASH)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except:
    PLOTLY_OK = False

# INFO BOUTIQUE
SHOP_NAME = "Paruise Shop"
SHOP_PHONE = "22893991499"

# --- 2. STYLE "DARK LUXE" (VISIBILITÉ PARFAITE & OR) ---
st.markdown("""
<style>
    /* 1. FOND GLOBAL */
    .stApp {
        background-color: #0E1117 !important;
        color: #E0E0E0 !important;
    }

    /* 2. SIDEBAR (GAUCHE) - COULEUR AJUSTÉE (ROUGE LOVE NOTE) */
    [data-testid="stSidebar"] {
        background-color: #6D071A !important; /* Même couleur que le message mignon */
        border-right: 1px solid #D4AF37;
    }
    
    /* CORRECTION VISIBILITÉ TEXTE MENU */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stRadio div {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }

    /* 3. TEXTES ET LABELS */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label, .stTextArea label, .stRadio label {
        color: #FFFFFF !important;
        font-size: 15px !important;
        font-weight: bold !important;
    }
    
    /* TITRES */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
    }
    h1 span, h2 span, h3 span { color: #D4AF37 !important; }

    /* 4. CHAMPS DE SAISIE (BLANC POUR ÉCRIRE) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input, .stTextArea textarea {
        background-color: #F0F2F6 !important;
        color: #000000 !important; /* Texte Noir */
        border: 1px solid #D4AF37 !important;
        border-radius: 8px !important;
    }
    /* Menu déroulant texte noir */
    div[data-baseweb="select"] span { color: #000000 !important; }
    div[data-baseweb="popover"] li { color: #000000 !important; }

    /* 5. BOUTONS (PREMIUM) */
    .stButton>button {
        background: linear-gradient(135deg, #800020 0%, #5a0016 100%) !important;
        color: white !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 10px !important;
        height: 55px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .stButton>button:hover {
        transform: scale(1.02);
        border-color: #FFFFFF !important;
    }

    /* 6. NOTE D'AMOUR (SIDEBAR) */
    .love-note {
        background-color: #580514; /* Un peu plus foncé pour se détacher légèrement */
        border: 2px dashed #D4AF37;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 30px;
        color: #FFD700;
        font-style: italic;
        font-size: 16px;
    }

    /* 7. CADRES */
    .step-box {
        background-color: #1E1E1E;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #D4AF37;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }
    .step-title {
        color: #D4AF37 !important;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 15px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }
    
    /* MESSAGE CARD */
    .msg-preview {
        background-color: #DCF8C6; /* Couleur WhatsApp */
        color: black;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ccc;
        font-family: monospace;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CONNEXION ---
@st.cache_resource
def get_database():
    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in st.secrets:
            key_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
            client = gspread.authorize(creds)
            return client.open("Data manager Paruise Shop")
    except: pass
    try:
        import os
        if os.path.exists('credentials.json'):
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
            client = gspread.authorize(creds)
            return client.open("Data manager Paruise Shop")
    except: pass
    st.error("❌ ERREUR CONNEXION.")
    return None

sh = get_database()
if not sh: st.stop()

def load_data(sheet):
    try:
        ws = sh.worksheet(sheet)
        d = ws.get_all_values()
        if len(d) < 2: return pd.DataFrame()
        return pd.DataFrame(d[1:], columns=d[0]).loc[:, [h for h in d[0] if h.strip() != ""]]
    except: return pd.DataFrame()

# --- 4. FONCTIONS ---
def clean_num(val):
    try: return float(str(val).replace("FCFA","").replace(" ","").replace(",", ".").strip())
    except: return 0.0

def whatsapp_link(phone, msg):
    encoded = urllib.parse.quote(msg)
    if pd.isna(phone) or str(phone).strip() == "": return f"https://wa.me/?text={encoded}"
    clean = str(phone).replace(" ", "").replace("+", "").replace(".", "").split(".")[0]
    return f"https://wa.me/{clean}?text={encoded}"

# --- 5. NAVIGATION ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3163/3163212.png", width=120)
st.sidebar.markdown("## PARUISE SHOP")
st.sidebar.markdown("---")

menu = st.sidebar.radio("MENU", [
    "🛒 Nouvelle Vente (Caisse)",
    "📦 Stock & Pépites",
    "💌 Clients & Amour",
    "📢 Marketing Impactant",
    "💸 Dépenses (Sorties)",
    "📈 Évolution du Budget"
])

# MESSAGE MIGNON
st.sidebar.markdown("""
<div class="love-note">
    💖 <b>Maman Maëlys !</b><br><br>
    J'ai créé cet outil spécialement pour toi.<br>
    Utilise-le au mieux !<br>
    <i>- Ton frère qui t'aime</i>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# 1. CAISSE
# =============================================================================
if menu == "🛒 Nouvelle Vente (Caisse)":
    st.title("🛍️ Encaisser avec le Sourire")
    
    df_prod = load_data("PRODUITS")
    df_cli = load_data("CLIENTS")
    
    # ÉTAPE 1
    st.markdown("""<div class="step-box"><div class="step-title">1️⃣ Qui est notre Reine du jour ?</div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        cli_list = ["-- Nouvelle Cliente --"] + df_cli["Nom_Client"].tolist() if not df_cli.empty else ["-- Nouvelle Cliente --"]
        
        # LOGIQUE INTELLIGENTE POUR SÉLECTIONNER AUTOMATIQUEMENT LA NOUVELLE CLIENTE
        index_defaut = 0
        if "nouvelle_cliente_creee" in st.session_state:
            nom_a_chercher = st.session_state["nouvelle_cliente_creee"]
            if nom_a_chercher in cli_list:
                index_defaut = cli_list.index(nom_a_chercher)
        
        client_nom = st.selectbox("Rechercher la cliente", cli_list, index=index_defaut, label_visibility="collapsed")
    
    final_client, final_tel = "", ""
    if client_nom == "-- Nouvelle Cliente --":
        with st.expander("✨ Inscrire une nouvelle Reine", expanded=True):
            n_nom = st.text_input("Son Nom")
            n_tel = st.text_input("Son WhatsApp")
            ca, cb = st.columns(2)
            n_qrt = ca.text_input("Quartier")
            n_src = cb.selectbox("Source", ["Passage", "TikTok", "Facebook", "Amie"])
            if st.button("💾 Enregistrer la Reine"):
                sh.worksheet("CLIENTS").append_row([n_nom, n_tel, n_qrt, n_src, ""])
                st.success(f"Bienvenue à {n_nom} !")
                # On sauvegarde le nom en mémoire pour le recharger tout de suite
                st.session_state["nouvelle_cliente_creee"] = n_nom
                st.rerun()
    else:
        # Nettoyage de la mémoire si on a changé de client
        if "nouvelle_cliente_creee" in st.session_state and st.session_state["nouvelle_cliente_creee"] != client_nom:
            del st.session_state["nouvelle_cliente_creee"]
            
        final_client = client_nom
        if not df_cli.empty:
            infos = df_cli[df_cli["Nom_Client"]==final_client]
            if not infos.empty: final_tel = str(infos.iloc[0]["Telephone"])
    st.markdown("</div>", unsafe_allow_html=True)

    # ÉTAPE 2
    st.markdown("""<div class="step-box"><div class="step-title">2️⃣ Son Coup de Cœur</div>""", unsafe_allow_html=True)
    if df_prod.empty:
        st.warning("⚠️ Stock vide.")
        st.stop()
        
    c3, c4 = st.columns(2)
    with c3:
        if "Nom_Article" in df_prod.columns:
            df_prod["Display"] = df_prod["Nom_Article"]
            choix = st.selectbox("Choisir l'article", df_prod["Display"])
            row = df_prod[df_prod["Display"]==choix].iloc[0]
            p_vente = clean_num(row.get("Prix_Vente", 0))
            p_achat = clean_num(row.get("Prix_Achat", 0))
            st.markdown(f"🏷️ Prix Étiquette : **<span style='color:#D4AF37; font-size:20px'>{p_vente:,.0f} FCFA</span>**", unsafe_allow_html=True)
        else: st.error("Erreur Stock"); st.stop()
        
    with c4:
        qte = st.number_input("Quantité", 1, 20, 1)
        prix_final = st.number_input("PRIX FINAL ACCORDÉ", value=int(p_vente), step=500)
    st.markdown("</div>", unsafe_allow_html=True)

    # ÉTAPE 3
    st.markdown("""<div class="step-box"><div class="step-title">3️⃣ L'Encaissement</div>""", unsafe_allow_html=True)
    pay = st.selectbox("Moyen de paiement", ["Espèces 💵", "Flooz 📱", "TMoney 🟡", "Virement 🏦"])
    
    total = prix_final * qte
    benefice = (prix_final - p_achat) * qte
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37'>TOTAL À PAYER : {total:,.0f} FCFA</h2>", unsafe_allow_html=True)
    
    if st.button("✨ VALIDER CETTE VENTE ✨"):
        if final_client:
            date = datetime.now().strftime("%d/%m/%Y")
            sh.worksheet("VENTES").append_row([date, final_client, row["Nom_Article"], prix_final, qte, total, pay])
            st.balloons()
            st.markdown(f"<div style='background-color:#1B5E20; color:white; padding:15px; border-radius:10px; text-align:center;'>👏 Bravo ! Vente réussie.<br>Gain net : {benefice:,.0f} FCFA</div>", unsafe_allow_html=True)
            
            # Reçu Mignon
            prenom = str(final_client).split(' ')[0]
            msg = f"""Coucou {prenom} ! C'est Paruise Shop 👑
Merci infiniment pour ta confiance.

🛍️ *Ton shopping :* {row['Nom_Article']}
💎 *Total :* {total:,.0f} FCFA

Tu vas être rayonnante avec ça ! Envoie-nous une photo quand tu le portes. ✨"""
            
            lnk = whatsapp_link(final_tel, msg)
            st.markdown(f"<br><a href='{lnk}' target='_blank'><button style='width:100%; background-color:#25D366; border:none;'>📲 ENVOYER LE REÇU WHATSAPP</button></a>", unsafe_allow_html=True)
            
            # On nettoie la session après une vente réussie
            if "nouvelle_cliente_creee" in st.session_state:
                del st.session_state["nouvelle_cliente_creee"]
                
        else:
            st.warning("⚠️ Sélectionne une cliente (ou enregistre la nouvelle ci-dessus).")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 2. STOCK
# =============================================================================
elif menu == "📦 Stock & Pépites":
    st.title("📦 Tes Trésors (Stock)")
    
    with st.expander("➕ AJOUTER UN NOUVEL ARTICLE", expanded=False):
        with st.form("add_stk"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nom de la pépite")
            
            # LISTE CATÉGORIES MISE À JOUR SELON TES INSTRUCTIONS
            liste_cat = [
                "BODY SWEET", 
                "PANTALON TISSU", 
                "PANTALON JEAN", 
                "CROP TOP", 
                "CULOTTE", 
                "JUPE", 
                "VESTE ET BLASER", 
                "T-shirt",
                "Robe",
                "Sac", 
                "Chaussure", 
                "Accessoire"
            ]
            
            n_cat = c2.selectbox("Catégorie", liste_cat)
            c3, c4, c5 = st.columns(3)
            pa = c3.number_input("Prix Achat", step=500)
            pv = c4.number_input("Prix Vente", step=500)
            qty = c5.number_input("Quantité", min_value=1)
            
            if st.form_submit_button("Enregistrer"):
                sh.worksheet("PRODUITS").append_row([n_nom, n_cat, pa, pv, "", qty])
                st.success("C'est en rayon !")
                st.rerun()

    df_p = load_data("PRODUITS")
    if not df_p.empty:
        df_p["Stock_Actuel"] = pd.to_numeric(df_p["Stock_Actuel"], errors='coerce').fillna(0)
        st.dataframe(df_p, use_container_width=True)
        
        low = df_p[df_p["Stock_Actuel"] < 3]
        if not low.empty:
            st.markdown(f"<div style='color:#FF5252; font-weight:bold; padding:10px;'>⚠️ {len(low)} articles bientôt en rupture !</div>", unsafe_allow_html=True)
            st.dataframe(low[["Nom_Article", "Stock_Actuel"]])

# =============================================================================
# 3. CLIENTS & AMOUR (COMPLET ET ILLIMITÉ)
# =============================================================================
elif menu == "💌 Clients & Amour":
    st.title("💌 Chouchouter tes Clientes")
    st.markdown("C'est ici que tu fidélises. Un petit message change tout.")
    
    df_c = load_data("CLIENTS")
    df_v = load_data("VENTES")
    
    if df_c.empty:
        st.warning("Ajoute d'abord des clientes dans le menu Caisse.")
        st.stop()

    # SÉLECTION CLIENTE
    st.markdown("""<div class="step-box"><div class="step-title">👤 À qui veux-tu écrire ?</div>""", unsafe_allow_html=True)
    destinataire = st.selectbox("Choisir la cliente", df_c["Nom_Client"].tolist())
    
    # Récupération infos
    infos = df_c[df_c["Nom_Client"] == destinataire].iloc[0]
    tel = str(infos["Telephone"])
    prenom = destinataire.split(' ')[0]
    
    # Historique achat
    total_depense = 0
    derniere_visite = "Jamais"
    if not df_v.empty:
        client_sales = df_v[df_v[df_v.columns[1]] == destinataire]
        if not client_sales.empty:
            # On suppose Total colonne 5
            total_depense = client_sales[client_sales.columns[5]].apply(clean_num).sum()
            derniere_visite = client_sales.iloc[-1][0] # Date
            
    c1, c2 = st.columns(2)
    c1.info(f"💰 Total Dépensé : {total_depense:,.0f} FCFA")
    c2.info(f"📅 Dernière visite : {derniere_visite}")
    st.markdown("</div>", unsafe_allow_html=True)

    # GÉNÉRATEUR DE MESSAGES ILLIMITÉ
    st.markdown("""<div class="step-box"><div class="step-title">✍️ Générateur de Messages Magiques</div>""", unsafe_allow_html=True)
    
    categorie = st.selectbox("Quel est le but du message ?", [
        "👋 Bienvenue (1er achat)",
        "💖 Remerciement VIP (Fidélité)",
        "💤 Relance (Ça fait longtemps)",
        "🎂 Joyeux Anniversaire",
        "👗 Nouvelle Collection (Teasing)",
        "✅ Suivi (Satisfaction)"
    ])
    
    ton = st.radio("Quel ton utiliser ?", ["🥰 Doux & Affectueux", "👑 Pro & Valorisant", "🎉 Fun & Dynamique"], horizontal=True)
    
    # --- BIBLIOTHÈQUE DE MESSAGES ---
    messages_db = {
        "👋 Bienvenue (1er achat)": {
            "🥰 Doux & Affectueux": [
                f"Coucou {prenom} ! 🥰 Merci encore pour ta visite aujourd'hui. Je suis trop contente de te compter parmi mes nouvelles clientes. À très vite !",
                f"Bienvenue dans la famille Paruise, {prenom} ! ❤️ J'espère que ton article te plaira. N'hésite pas si tu as besoin de conseils."
            ],
            "👑 Pro & Valorisant": [
                f"Bonjour {prenom}, merci pour votre premier achat chez Paruise Shop. ✨ Ravie de vous avoir rencontrée. Au plaisir de vous revoir !",
                f"Merci pour la confiance {prenom}. ✅ C'est un excellent choix. Nous restons à votre disposition."
            ],
            "🎉 Fun & Dynamique": [
                f"Hello {prenom} ! 👋 Ça y est, tu fais partie de la Team Paruise ! Merci pour ton achat, tu vas tout déchirer avec ! 🔥",
                f"Yes {prenom} ! Merci d'être passée. On espère te revoir très vite pour d'autres pépites ! 💃"
            ]
        },
        "💖 Remerciement VIP (Fidélité)": {
            "🥰 Doux & Affectueux": [
                f"Mon étoile {prenom} ! 🌟 Je regardais mes comptes et je voulais juste te dire MERCI. Merci d'être si fidèle. Je t'embrasse fort !",
                f"Coucou {prenom} ❤️. Tu es vraiment une cliente en or. Merci de soutenir mon rêve. Passe quand tu veux, tu es chez toi ici."
            ],
            "👑 Pro & Valorisant": [
                f"Chère {prenom}, vous faites partie de nos meilleures clientes. 🏆 Merci pour votre fidélité exemplaire. À très bientôt chez Paruise Shop.",
                f"Un grand merci {prenom} pour votre confiance renouvelée. C'est un honneur de vous habiller. ✨"
            ],
            "🎉 Fun & Dynamique": [
                f"Alerte VIP ! 🚨 {prenom}, tu es officiellement une de mes clientes préférées ! Merci pour tout, t'es la meilleure ! 🙌",
                f"Wow {prenom} ! On ne t'arrête plus ! 😍 Merci de toujours choisir Paruise Shop. On t'adore !"
            ]
        },
        "💤 Relance (Ça fait longtemps)": {
            "🥰 Doux & Affectueux": [
                f"Coucou {prenom}... 👋 Je pensais à toi ce matin. Ça fait longtemps qu'on ne t'a pas vue ! J'espère que tu vas bien ? Passe nous faire un petit coucou. ❤️",
                f"Toc toc {prenom} ! 👀 La boutique est un peu vide sans ton sourire. Tout va bien ? On t'attend avec impatience !"
            ],
            "👑 Pro & Valorisant": [
                f"Bonjour {prenom}. Cela fait un moment que nous ne vous avons pas vue. Nous avons reçu des nouveautés qui correspondent à votre style. ✨",
                f"Votre élégance nous manque, {prenom}. 🌹 Venez découvrir nos derniers arrivages à la boutique."
            ],
            "🎉 Fun & Dynamique": [
                f"Eh oh {prenom} ! Tu nous boudes ? 😜 Reviens vite, on a reçu des trucs de dingue ! Tu vas adorer !",
                f"Avis de recherche : On a perdu {prenom} ! 😂 Reviens nous voir, promis on a des pépites pour toi !"
            ]
        },
        "🎂 Joyeux Anniversaire": {
            "🥰 Doux & Affectueux": [
                f"Joyeux Anniversaire ma belle {prenom} ! 🎂🥳 Je te souhaite tout le bonheur du monde. Passe prendre ton petit cadeau à la boutique ! 🎁",
                f"C'est ta journée {prenom} ! 🎉 Profite, brille, danse ! Gros bisous de toute l'équipe Paruise."
            ],
            "👑 Pro & Valorisant": [
                f"Joyeux Anniversaire {prenom}. 🥂 Que cette nouvelle année vous apporte succès et élégance. Profitez de -15% aujourd'hui pour fêter ça.",
                f"Un très bel anniversaire à notre cliente préférée {prenom}. ✨ Meilleurs vœux de la part de Paruise Shop."
            ],
            "🎉 Fun & Dynamique": [
                f"Happy Birthday Queen {prenom} ! 👑 Aujourd'hui c'est toi la star ! Viens fêter ça avec nous ! 🍾",
                f"Bon anniv {prenom} ! 🎂 Pas de régime aujourd'hui, et pas de limite de shopping ! 😂 Profite bien !"
            ]
        },
        "👗 Nouvelle Collection (Teasing)": {
            "🥰 Doux & Affectueux": [
                f"Coucou {prenom} ! ✨ J'ai reçu des merveilles ce matin et j'ai tout de suite pensé à toi... Tu dois venir voir ça ! 😍",
                f"Psst {prenom}... J'ai gardé une pièce de côté qui t'irait trop bien. Passe l'essayer avant que je la mette en rayon ! ❤️"
            ],
            "👑 Pro & Valorisant": [
                f"Madame {prenom}, notre nouvelle collection est arrivée. Des pièces uniques et distinguées, comme vous. 💎",
                f"Avant-première pour vous {prenom}. ✨ Venez découvrir l'arrivage de la semaine en exclusivité."
            ],
            "🎉 Fun & Dynamique": [
                f"Alerte PÉPITE {prenom} ! 🚨 Ce que je viens de recevoir est juste INCROYABLE ! Fonce avant qu'il n'y en ait plus ! 🏃‍♀️",
                f"Tu n'es pas prête {prenom}... 😍 Le nouvel arrivage est une tuerie ! Viens vite voir ça !"
            ]
        },
        "✅ Suivi (Satisfaction)": {
            "🥰 Doux & Affectueux": [
                f"Alors {prenom}, ton nouvel article ? 😍 J'espère que tu te sens belle dedans ! Envoie-moi une photo si tu le portes ! Bisous.",
                f"Petit message pour savoir si tout va bien avec ton achat, {prenom} ? ❤️ J'espère que ça te plaît toujours autant !"
            ],
            "👑 Pro & Valorisant": [
                f"Bonjour {prenom}, nous espérons que vous êtes satisfaite de votre achat. ✨ N'hésitez pas à nous faire un retour.",
                f"La qualité vous convient-elle {prenom} ? Votre satisfaction est notre priorité chez Paruise Shop. ✅"
            ],
            "🎉 Fun & Dynamique": [
                f"Alors {prenom}, on valide ou on valide ? 😎 J'espère que tu fais des jalouses avec ta nouvelle tenue ! 🔥",
                f"Dis-moi tout {prenom} ! Tu l'as porté ? Ça donne quoi ? 😍 On veut voir les photos !"
            ]
        }
    }
    
    # Sélection aléatoire
    msg_list = messages_db[categorie][ton]
    final_msg = random.choice(msg_list)
    
    st.markdown("### 📱 Aperçu du message :")
    st.markdown(f"<div class='msg-preview'>{final_msg}</div>", unsafe_allow_html=True)
    
    # BOUTON ENVOI
    lnk = whatsapp_link(tel, final_msg)
    st.markdown(f"""
    <a href='{lnk}' target='_blank'>
        <button style='width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; font-size:18px; cursor:pointer;'>
            🚀 ENVOYER MAINTENANT SUR WHATSAPP
        </button>
    </a>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Générer un autre message (Variante)"):
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 4. MARKETING
# =============================================================================
elif menu == "📢 Marketing Impactant":
    st.title("📢 Fais du Bruit !")
    
    tab1, tab2 = st.tabs(["📘 Facebook", "🎵 TikTok"])
    prod = st.text_input("Produit vedette", "Cette Robe en Soie")
    
    with tab1:
        st.markdown("### L'Art de l'Émotion")
        fb_txt = f"""🤫 JE NE DEVRAIS PAS VOUS MONTRER ÇA...

Quand j'ai ouvert le carton et vu {prod}... je n'ai pas pu résister.
La coupe ? Parfaite. La matière ? Une caresse sur la peau.

👑 Mes Reines de Wonyomé, attention, je n'en ai que quelques pièces.
📍 Paruise Shop (Face Station Sanol)
👇 Cliquez vite ici : https://wa.me/{SHOP_PHONE}"""
        st.text_area("Copier :", fb_txt, height=250)

    with tab2:
        st.markdown("### Titres TikTok")
        st.code("Arrête de scroller si tu veux être la plus classe.")
        st.code("On parie que tu vas craquer pour cette tenue ? 😏")
        st.code("#Lome #TogoFashion #ParuiseShop #Chic228 #OOTD")

# =============================================================================
# 5. DÉPENSES
# =============================================================================
elif menu == "💸 Dépenses (Sorties)":
    st.title("💸 Où va l'argent ?")
    
    with st.form("dep"):
        d_date = st.date_input("Date", datetime.now())
        d_cat = st.selectbox("C'est pour quoi ?", ["Marchandise (Stock)", "Loyer Boutique", "Factures", "Transport", "Repas/Perso", "Épargne"])
        d_montant = st.number_input("Montant", step=500)
        d_desc = st.text_input("Petit détail")
        if st.form_submit_button("Noter la dépense"):
            try: sh.worksheet("DEPENSES").append_row([d_date.strftime("%d/%m/%Y"), d_cat, d_montant, d_desc])
            except: st.error("Crée l'onglet DEPENSES !")
            st.success("C'est noté. On surveille le budget !")

# =============================================================================
# 6. BUDGET
# =============================================================================
elif menu == "📈 Évolution du Budget":
    st.title("📈 La Vie de ton Argent")
    
    if not PLOTLY_OK:
        st.warning("⚠️ Chargement des graphiques...")
    else:
        df_v = load_data("VENTES")
        df_d = load_data("DEPENSES")
        
        data_points = []
        if not df_v.empty:
            col_t = "Total" if "Total" in df_v.columns else df_v.columns[5]
            for _, row in df_v.iterrows():
                try:
                    d = datetime.strptime(row.iloc[0], "%d/%m/%Y")
                    data_points.append({"Date": d, "Montant": clean_num(row[col_t])})
                except: pass
        if not df_d.empty:
            col_m = "Montant" if "Montant" in df_d.columns else df_d.columns[2]
            for _, row in df_d.iterrows():
                try:
                    d = datetime.strptime(row.iloc[0], "%d/%m/%Y")
                    data_points.append({"Date": d, "Montant": -clean_num(row[col_m])})
                except: pass
                
        if data_points:
            df_chart = pd.DataFrame(data_points).sort_values("Date")
            df_chart["Caisse"] = df_chart["Montant"].cumsum()
            
            fig = px.area(df_chart, x="Date", y="Caisse", title="Trésorerie (Cash Réel)", color_discrete_sequence=['#D4AF37'])
            fig.update_layout(plot_bgcolor="#1E1E1E", paper_bgcolor="#0E1117", font_color="white", xaxis_showgrid=False, yaxis_gridcolor='#333')
            st.plotly_chart(fig, use_container_width=True)
            
            solde = df_chart.iloc[-1]['Caisse']
            st.markdown(f"<h3 style='text-align:center'>Solde actuel : <span style='color:#D4AF37'>{solde:,.0f} FCFA</span></h3>", unsafe_allow_html=True)
        else:
            st.info("Pas encore assez de données pour tracer la courbe.")
