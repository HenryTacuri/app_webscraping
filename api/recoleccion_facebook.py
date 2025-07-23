import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains


def extraer_publicaciones_facebook(num_publicaciones, enfermedad, num_comentarios, anio_publicacion=2025):
    # --- Configuración Chrome ---
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-notifications")
    
    option.add_argument('--profile-directory=Default') 

    prefs = {"profile.default_content_setting_values.notifications": 2}
    option.add_experimental_option("prefs", prefs)

    EMAIL = "henry.tacuri99@gmail.com"
    PASSWORD = "cCWyB6tZuLWx74V"
    CHROMEDRIVER_PATH = "C:/Users/HP VICTUS/Documents/Henry/vision_env/src/webscraping/chromedriver-win64/chromedriver.exe"

    service = Service(CHROMEDRIVER_PATH)
    browser = webdriver.Chrome(service=service, options=option)
    wait = WebDriverWait(browser, 30)

    # --- Login ---
    browser.get("https://es-la.facebook.com/")
    time.sleep(random.uniform(2, 4))
    email_field = wait.until(EC.visibility_of_element_located((By.NAME, 'email')))
    for c in EMAIL:
        email_field.send_keys(c)
        time.sleep(random.uniform(0.09, 0.25))
    time.sleep(random.uniform(0.4, 1.2))
    pass_field = wait.until(EC.visibility_of_element_located((By.NAME, 'pass')))
    for c in PASSWORD:
        pass_field.send_keys(c)
        time.sleep(random.uniform(0.09, 0.22))
    login_btn = browser.find_element(By.NAME, 'login')
    actions = ActionChains(browser)
    actions.move_to_element(login_btn).pause(random.uniform(0.5, 1.2)).click().perform()
    time.sleep(random.uniform(5, 8))

    time.sleep(6)

    # --- Buscar publicaciones ---
    print(f"\nBuscando publicaciones sobre: {enfermedad}")
    browser.get(f'https://www.facebook.com/search/posts?q={enfermedad}')
    time.sleep(6)

    wait = WebDriverWait(browser, 15)
    # Filtrar por año
    try:
        combobox = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label[contains(.,'Fecha de publicación')]]"))
        )
        combobox.click()
        time.sleep(2)
        anio_str = str(anio_publicacion)
        xpath_anio = f"//span[contains(text(), '{anio_str}')]"
        anio_element = wait.until(
            EC.visibility_of_element_located((By.XPATH, xpath_anio))
        )
        anio_element.click()
        time.sleep(2)
    except Exception as e:
        print(f"No se pudo seleccionar año: {e}")

    resultados = []
    processed_posts = set()
    publicaciones_extraidas = 0

    MAX_SCROLLS = 30
    SCROLL_AMOUNT = 800
    DELAY_BETWEEN_SCROLLS = 2

    for s in range(MAX_SCROLLS):
        if publicaciones_extraidas >= num_publicaciones:
            break

        print(f"[SCROLL {s+1}] Bajando página…")
        browser.execute_script(f"window.scrollBy(0, {SCROLL_AMOUNT});")
        time.sleep(DELAY_BETWEEN_SCROLLS)

        buttons = browser.find_elements(By.XPATH, "//div[@role='button' and @aria-label='Dejar un comentario']")
        print(f"  Encontrados {len(buttons)} botones para comentar.")

        for idx, btn in enumerate(buttons):
            if publicaciones_extraidas >= num_publicaciones:
                break
            # Obtener un ID de la publicación para evitar repetir
            try:
                parent = btn.find_element(By.XPATH, "./ancestor::div[contains(@role, 'article')]")
                post_id = parent.get_attribute("data-ft") or parent.get_attribute("id") or f"{enfermedad}_{idx}"
            except Exception:
                post_id = f"{enfermedad}_{idx}"

            if post_id in processed_posts:
                continue
            processed_posts.add(post_id)

            try:
                browser.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                time.sleep(1)
                try:
                    btn.click()
                except Exception:
                    browser.execute_script("arguments[0].click();", btn)
                time.sleep(2)

                # Esperar diálogo
                try:
                    dialog = WebDriverWait(browser, 8).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                    )
                except Exception:
                    print("No se pudo abrir el diálogo de comentarios")
                    continue

                # Extraer usuario del post
                user_post = "Desconocido"
                try:
                    user_link = dialog.find_element(By.XPATH,
                        ".//a[contains(@aria-label, ', ver historia') or contains(@aria-label, ', ver perfil')]"
                    )
                    user_post = user_link.text.strip()
                    if not user_post:
                        span = user_link.find_element(By.XPATH, ".//span")
                        user_post = span.text.strip()
                except Exception:
                    try:
                        user_post = dialog.find_element(By.XPATH, ".//strong/span").text.strip()
                    except Exception:
                        pass

                # Extraer texto principal y limpiar
                try:
                    preview = dialog.find_element(
                        By.XPATH,
                        ".//div[@data-ad-preview='message']"
                    )
                    paragraphs = preview.find_elements(By.XPATH, ".//div[@dir='auto']")
                    user_postText = "\n".join(
                        p.get_attribute("textContent").strip()
                        for p in paragraphs
                        if p.get_attribute("textContent").strip()
                    )
                except Exception:
                    user_postText = ""
                user_postText = user_postText

                # Scroll y expandir comentarios
                try:
                    scroll_areas = dialog.find_elements(By.XPATH, ".//div[contains(@class, 'x1i10hfl') and @role='dialog']//div[contains(@class,'scrollable') or contains(@class, 'x6s0dn4')]")
                    scroll_area = scroll_areas[0] if scroll_areas else dialog

                    num_scrolls = 10
                    for _ in range(num_scrolls):
                        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 600;", scroll_area)
                        time.sleep(0.3)
                        # Ver más comentarios
                        try:
                            ver_mas = dialog.find_elements(By.XPATH, ".//span[contains(text(),'Ver más comentarios')]")
                            for btn2 in ver_mas:
                                browser.execute_script("arguments[0].scrollIntoView({block:'center'});", btn2)
                                btn2.click()
                                time.sleep(0.2)
                        except Exception:
                            pass
                        # Ver las X respuestas
                        try:
                            ver_res = dialog.find_elements(By.XPATH, ".//span[contains(text(),'Ver las') and contains(text(),'respuestas')]")
                            for btn2 in ver_res:
                                browser.execute_script("arguments[0].scrollIntoView({block:'center'});", btn2)
                                btn2.click()
                                time.sleep(0.2)
                        except Exception:
                            pass
                    time.sleep(0.7)
                except Exception as e:
                    print("⚠️ Error al hacer scroll/expandir comentarios:", e)

                # Extraer comentarios (limpiando cada uno)
                comentarios = []
                try:
                    comentarios_divs = dialog.find_elements(
                        By.XPATH,
                        ".//div[contains(@class, 'x1y1aw1k')]"
                    )
                    for div in comentarios_divs[:num_comentarios]:
                        try:
                            user_comment = "Desconocido"
                            try:
                                nombre_elem = div.find_element(By.XPATH, ".//a[contains(@href,'facebook.com/')]/span")
                                user_comment = nombre_elem.text.strip()
                            except Exception:
                                pass
                            spans = div.find_elements(By.XPATH, ".//span[@dir='auto']")
                            user_commentText = " ".join([s.text.strip() for s in spans if s.text.strip()])
                            resultados.append({
                                "enfermedad": enfermedad,
                                "user_post": user_post,
                                "user_postText": user_postText,
                                "user_comment": user_comment,
                                "user_commentText": user_commentText
                            })
                        except Exception:
                            continue
                except Exception as e:
                    print("⚠️ Error extrayendo comentarios:", e)

                # Si no hay comentarios, agrega igual la publicación pero con campos vacíos
                if not comentarios_divs or len(comentarios_divs) == 0:
                    resultados.append({
                        "enfermedad": enfermedad,
                        "user_post": user_post,
                        "user_postText": user_postText,
                        "user_comment": "",
                        "user_commentText": ""
                    })

                publicaciones_extraidas += 1

                # Cerrar diálogo
                try:
                    close_btn = dialog.find_element(
                        By.XPATH,
                        ".//div[@aria-label='Cerrar' or @aria-label='Close']"
                    )
                    close_btn.click()
                except Exception:
                    try:
                        dialog.send_keys(Keys.ESCAPE)
                    except Exception:
                        pass
                time.sleep(1)

            except Exception as e:
                print(f"  No se pudo abrir/comentar post {idx}: {e}")
                try:
                    dialog = browser.find_element(By.XPATH, "//div[@role='dialog']")
                    dialog.send_keys(Keys.ESCAPE)
                except Exception:
                    pass
                time.sleep(1)
                continue

    browser.quit()

    return resultados

