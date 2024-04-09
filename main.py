from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchFrameException

from time import sleep
from datetime import timedelta
from argparse import ArgumentParser, Namespace


def debug(mtype, message):
	if args.verbose:
		if mtype == 'error':
			print(f"\032[ERROR]\033 {message}")
		if mtype == 'info':
			print(f"\032[INFO]\033 {message}")
		elif mtype == 'warning':
			print(f"\032[WARNING]\033 {message}")
		elif mtype == 'success':
			print(f"\032[SUCCESS]\033 {message}")
		else:
			print(f"\032[DEBUG]\033 {message}")


parser = ArgumentParser()

parser_login = parser.add_argument_group('Login')

parser_login.add_argument('-u', '--ra', type=str, help='RA of the student, with digit')
parser_login.add_argument('-d', '--uf', type=str, help='UF of the sudent', default='sp')
parser_login.add_argument('-p', '--password', type=str, help='Password of the student')
parser_login.add_argument('-c', '--channel', type=str, help='Channel of choice', choices=['3c', 'c3'])
parser_login.add_argument('-a', '--amount', type=int, help='Amount of videos to watch', default=0)

parser_debug = parser.add_argument_group('Debug')

parser_debug.add_argument('-v', '--verbose', help='Verbose mode', action='store_false', default=True)

args: Namespace = parser.parse_args()

if args.ra and args.password and args.channel:
	arg_ra = args.ra
	arg_uf = args.uf
	arg_password = args.password
	arg_channel = args.channel
	arg_amount = args.amount
else:
	debug('warning', 'Not all arguments were informed')
	exit()


driver = webdriver.Chrome()
driver.get('https://cmspweb.ip.tv/login')

implicit_wait = driver.implicitly_wait(5)
wait = WebDriverWait(driver, 900)


def login(ra, uf, password):
	debug('info', f'Logging in with RA:{ra} and UF:{uf}')

	wait.until(lambda driver: driver.find_element(By.ID, 'access-student')).click()

	wait.until(lambda driver: driver.find_element(By.ID, 'ra-student')).send_keys(ra[slice(0, -1)])
	wait.until(lambda driver: driver.find_element(By.ID, 'digit-student')).send_keys(ra[slice(-1, -2, -1)])

	uf_student = wait.until(lambda driver: driver.find_element(By.ID, 'uf-student'))
	Select(uf_student).select_by_value(uf)

	wait.until(lambda driver: driver.find_element(By.ID, 'password-student')).send_keys(password)

	wait.until(lambda driver: driver.find_element(By.ID, 'btn-login-student')).click()

	debug('success', f'Logged in with RA:{ra} and UF:{uf}')


def navigate(channel):
	debug('info', 'Entering Recordings Room')

	implicit_wait
	if channel.lower() == '3c':
		wait.until(lambda driver: driver.find_element(By.ID, 'lproom_r3b3556ff22951b448-l')).click()
	elif channel.lower() == 'c3':
		wait.until(lambda driver: driver.find_element(By.ID, 'lproom_r43d55cb67a22a9f47-l')).click()

	implicit_wait
	wait.until(lambda driver: driver.find_element(By.ID, 'roomDetailCsm')).click()
	
	debug('success', 'Entered Recordings Room')


def count_videos():
	debug('info', 'Counting videos')

	driver.switch_to.default_content()

	try:
		implicit_wait
		iframe = wait.until(lambda driver: driver.find_element(By.XPATH, '//*[@id="recordings-area-body"]/iframe'))
		driver.switch_to.frame(iframe)
	except NoSuchFrameException:
		debug('error', 'Failed to switch to iframe')
		exit()

	videos_list = wait.until(lambda driver: driver.find_elements(By.CLASS_NAME, 'MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation1.MuiCard-root.css-1154o8t'))

	driver.switch_to.default_content()

	video_amount = int(len(videos_list))

	debug('success', f'Found {video_amount} videos')

	return videos_list, video_amount


def video_countdown(time):
	video_duration = time
	while video_duration > 0:
		timer = timedelta(seconds = video_duration)
		sleep(1)
		video_duration -= 1
		print(f'Remaining Time: {timer}', end='\r')


def mute_video():
	action = ActionChains(driver)
	for i in range(0, 20):
		action.send_keys(Keys.DOWN).perform()


def watch_videos(amount):
	videos = count_videos()
	videos_list = videos[0]
	videos_amount = videos[1]
	video_num = 0
	watched = 0

	video_duration = 0
	offset_time = 15

	action = ActionChains(driver)

	if amount == 0 or amount > videos_amount:
		watch_amount = videos_amount
		display_amount = videos_amount
	else:
		watch_amount = amount
		display_amount = amount

	debug('info', f'Watching {watch_amount} videos')

	try:
		implicit_wait
		iframe = wait.until(lambda driver: driver.find_element(By.TAG_NAME, 'iframe'))
		driver.switch_to.frame(iframe)
	except NoSuchFrameException:
		debug('error', 'Failed to switch to iframe')
		exit()

	while watch_amount > 0:
		debug('info', f'Watching video {video_num+1}/{display_amount}')

		implicit_wait
		time = wait.until(lambda driver: videos_list[video_num].find_elements(By.CLASS_NAME, 'MuiTypography-root.MuiTypography-caption.MuiTypography-noWrap.css-guitlj'))[5].text
		time = time.split(' ')[1].split(':')
		video_duration = int(time[0])*3600 + int(time[1])*60 + int(time[2]) # Hours, Minutes, Seconds

		video = videos_list[video_num]
		wait.until(lambda driver: video.find_element(By.CLASS_NAME, 'react-player__preview')).click()
		
		action.send_keys(Keys.TAB).perform()
		mute_video()
		action.send_keys(Keys.SPACE).perform()

		implicit_wait
		video_countdown(video_duration)

		action.send_keys(Keys.ESCAPE).perform()

		video_num += 1
		watched += 1
		watch_amount -= 1

	driver.switch_to.default_content()

	debug('success', f'Finished {video_num}/{display_amount} videos')


login(arg_ra, arg_uf, arg_password)
navigate(arg_channel)
watch_videos(arg_amount)

driver.quit()
