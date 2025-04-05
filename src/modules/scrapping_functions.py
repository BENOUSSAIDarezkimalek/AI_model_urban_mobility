from datetime import datetime,time
import locale
from bs4 import BeautifulSoup
import json
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# Configuration du WebDriver en mode headless
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def fetch_json_event(url, driver):
    try:
        driver.get(url)
        time.sleep(3)  # Ajout d’un délai pour éviter d’être bloqué

        # Scroll pour charger le contenu
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extraction du JSON
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        script_tag = soup.find("script", {"type": "application/ld+json"})
        
        return json.loads(script_tag.string) if script_tag else None

    except Exception as e:
        print(f" Erreur pour {url}: {e}")
        return None


# def get_Harena_datetime(calendar_tag) :
#     date_text = calendar_tag.get_text(separator=' ').strip()
#     clean_text = re.sub(r'\s+', ' ', date_text).strip()
#     # Dictionnaire des mois français
#     mois_fr = {
#         'janv.': '01', 'févr.': '02', 'mars': '03', 'avr.': '04',
#         'mai': '05', 'juin': '06', 'juil.': '07', 'août': '08',
#         'sept.': '09', 'oct.': '10', 'nov.': '11', 'déc.': '12'
#     }

#     # Split des parties
#     parts = clean_text.split()
#     jour = parts[0]
#     mois = mois_fr[parts[1]]
#     annee = parts[2]
#     heure = parts[3]

#     # Reformatage en string de type "31-08-2024 20:00"
#     date_str = f"{jour}-{mois}-{annee} {heure}"

#     # Conversion en datetime
#     dt = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
#     return dt  


# def extraire_datetimes(date_string, annee_reference=2025):
#     """
#     Extrait une liste de datetime.datetime depuis un string comme :
#     'Samedi 15 février, 17h30, 20h30'
#     """
#     mois_mapping = {
#         'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04', 'mai': '05', 'juin': '06',
#         'juillet': '07', 'août': '08', 'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
#     }

#     if not date_string.strip():
#         return []

#     try:
#         date_part, *hours = date_string.split(',')
#         # Exemple : 'Samedi 15 février' => récupère '15' et 'février'
#         tokens = date_part.strip().split(' ')
#         day_num = tokens[1].zfill(2)
#         mois = tokens[2].lower()
#         mois_num = mois_mapping.get(mois)

#         # Construit la date sans l'heure
#         full_date = f"{annee_reference}-{mois_num}-{day_num}"

#         datetimes = []
#         for hour in hours:
#             hour_clean = hour.strip().replace('h', ':')  # 17h30 => 17:30
#             dt_str = f"{full_date} {hour_clean}"
#             dt = pd.to_datetime(dt_str, format="%Y-%m-%d %H:%M", errors='coerce')
#             if pd.notnull(dt):
#                 datetimes.append(dt.to_pydatetime())  # Objet datetime natif
#         return datetimes

#     except Exception as e:
#         print(f"Erreur de parsing sur la date : {date_string} => {e}")
#         return []

# def fetch_datetime_fcmatch(url_feuille_match):
#     url_feuille_match = f'https://www.fcnantes.com/articles/20242025/{url_feuille_match}'
#     response_feuille_match = requests.get(url_feuille_match)

#     if response_feuille_match.status_code == 200:
#         soup_feuille_martch = BeautifulSoup(response_feuille_match.content, 'html.parser')
#         time_text = soup_feuille_martch.find('div', class_="principal_fdm").find('center').text.strip()

#         # Extraction de l'heure avec regex
#         heure_match = re.search(r'\b(\d{1,2}):(\d{2})\b', time_text)
#         if heure_match:
#             heures = int(heure_match.group(1))
#             minutes = int(heure_match.group(2))
#             print(f"Heure : {heures}, Minutes : {minutes}")

#             # Utilise la classe datetime.time proprement
#             time_obj = time(heures, minutes)
#             print(f"Time object : {time_obj} / Type : {type(time_obj)}")
#             return time_obj
#     return None