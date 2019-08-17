from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.support.select import Select


class ScreenAnalysis:
    STAGING_URL = 'https://ace-web.qtstage.io/#secret-mode'
    driver = None
    def __init__(self):
        self.set_up()
        self.capture_screens()
        self.analyze()
        self.clean_up()
    def set_up(self):
        #self.driver = webdriver.Chrome("/Users/swati/Downloads/webdrivers/chromedriver")
        self.driver = webdriver.Firefox()

    def clean_up(self):
        self.driver.close()s

    def capture_screens(self):
        self.screenshot(self.STAGING_URL, 'header')

    def screenshot(self, url, file_name):
        driver = self.driver
        # with open('pom.json') as f:
        #    data = json.dumps(f)
        print("Capturing", url, "screenshot as", file_name, "...")
        driver.get(url)
        driver.fullscreen_window()
        # assert driver.find_elements_by_class_name(data["popup"]) is not None
        driver.find_element_by_xpath("//*[@id='secret-mode']/div/button[1]").click()
        select = Select(driver.find_element_by_xpath("//*[@id='header-theme']"))
        for i in range(9):
            if i < 4:
                select.select_by_value('header_{}'.format(i+1))
                driver.execute_script("window.scrollTo(0, 0);")
                driver.get_screenshot_as_png()
                element = driver.find_element_by_xpath("//div[@id='navbar']")
                location = element.location
                size = element.size
                file = 'screenshots/actual/' + file_name + '_' + str(i+1) + '.png'
                driver.save_screenshot(file)
                x = location['x']
                y = location['y']
                width = location['x'] + size['width']
                height = location['y'] + size['height']
                im = Image.open(file)
                im = im.crop((int(x), int(y), int(2840), int(225)))
                im.save(file)

            else:
                select.select_by_value('{}header_{}'.format('single-layer-', i-3))
                driver.execute_script("window.scrollTo(0, 0);")
                driver.get_screenshot_as_png()
                element = driver.find_element_by_xpath("//div[@id='navbar']")
                location = element.location
                size = element.size
                file = 'screenshots/actual/' + file_name + '_' + str(i + 1) + '.png'
                driver.save_screenshot(file)
                x = location['x']
                y = location['y']
                width = location['x'] + size['width']
                height = location['y'] + size['height']
                im = Image.open(file)
                im = im.crop((int(x), int(y), int(2840), int(113)))
                im.save(file)
        print("Done.")



    def analyze(self):
        # Constants and declarations
        actual_images = []
        base_images = []
        columns = 60
        rows = 80
        for i in range(9):
            actual_images.append(Image.open("screenshots/actual/header_{}.png".format(i+1)))
            base_images.append(Image.open("screenshots/baseline/header_{}.png".format(i+1)))
        for j in range(9):
            screen_width, screen_height = actual_images[j].size
            block_width = ((screen_width - 1) // columns) + 1 # this is just a division ceiling
            block_height = ((screen_height - 1) // rows) + 1
            for y in range(0, screen_height, block_height+1):
                for x in range(0, screen_width, block_width+1):
                    region_base = self.process_region(base_images[j], x, y, block_width, block_height)
                    region_actual = self.process_region(actual_images[j], x, y, block_width, block_height)
                    if region_base is not None and region_actual is not None and region_base != region_actual:
                        draw = ImageDraw.Draw(base_images[j])
                        draw.rectangle((x, y, x+block_width, y+block_height), outline="red")
                base_images[j].save("screenshots/diff/result_{}.png".format(str(j+1)))


    def process_region(self, image, x, y, width, height):
        region_total = 0
        # This can be used as the sensitivity factor, the larger it is the less sensitive the comparison
        factor = 5
        for coordinateY in range(y, y+height):
            for coordinateX in range(x, x+width):
                try:
                    pixel = image.getpixel((coordinateX, coordinateY))
                    region_total += sum(pixel)/4
                except:
                    return
        return region_total/factor
ScreenAnalysis()