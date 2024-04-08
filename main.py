from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from time import sleep
from datetime import timedelta

driver = webdriver.Chrome()

driver.get("https://cmspweb.ip.tv")

wait = WebDriverWait(driver, timeout=2)
implicit_wait = driver.implicitly_wait(1000 * 5)

user_ra = ""
user_password = ""

records_class = "3C" # Terá a opção para o 3C e C3


def login():
    wait.until(lambda driver : driver.find_element(By.ID, "access-student")).click()

    wait.until(lambda driver : driver.find_element(By.ID, "ra-student")).send_keys(user_ra[slice(0, -1)])
    wait.until(lambda driver : driver.find_element(By.ID, "digit-student")).send_keys(user_ra[slice(-1, -2, -1)])

    wait.until(lambda driver : driver.find_element(By.ID, "password-student")).send_keys(user_password)

    wait.until(lambda driver : driver.find_element(By.ID, "btn-login-student")).click()

    enter_records()


def enter_records():
    if records_class == "3C":
        wait.until(lambda driver : driver.find_element(By.ID, "lproom_r3b3556ff22951b448-l")).click()
    elif records_class == "C3":
        wait.until(lambda driver : driver.find_element(By.ID, "lproom_r43d55cb67a22a9f47-l")).click()

    wait.until(lambda driver : driver.find_element(By.ID, "roomDetailCsm")).click()

    driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))

    watch_videos()


def count_videos():
    videos = wait.until(lambda driver : driver.find_elements(By.CLASS_NAME, "MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation1.MuiCard-root.css-1154o8t"))
    return videos, int(len(videos))


def video_countdown(time, offset=0):
    video_duration = int(time[0])*3600 + int(time[1])*60 + int(time[2]) + offset

    while video_duration > 0:
        timer = timedelta(seconds=video_duration)
        print(timer, end="\r")

        sleep(1)
        video_duration -= 1


def play_video():
    action = ActionChains(driver)
    action.send_keys(Keys.TAB).perform()
    action.send_keys(Keys.SPACE).perform()


def mute_video():
    action = ActionChains(driver)
    for i in range(0, 20):
        action.send_keys(Keys.ARROW_DOWN).perform()


def watch_videos():
    videos = count_videos()
    videos_list = videos[0]
    videos_amount = videos[1]

    action = ActionChains(driver)

    for video in videos_list:
        print(f"Videos Left: {videos_amount}", end="\r")

        time = wait.until(lambda video : video.find_elements(By.CLASS_NAME, "MuiTypography-root.MuiTypography-caption.MuiTypography-noWrap.css-guitlj"))[5].text
        time = time.split(" ", 1)[1].split(":")

        wait.until(lambda video : video.find_element(By.CLASS_NAME, "react-player__preview")).click()

        play_video()
        mute_video()
        video_countdown(time)

        action.send_keys(Keys.ESCAPE).perform() # Exit video

        videos_amount -= 1


login()
driver.close()
