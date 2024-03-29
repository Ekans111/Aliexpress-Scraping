from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from re import findall, search
from time import sleep

def click_function(driver, click_element):
    sleep(0.2)
    # Get the height of the browser window
    window_height = driver.execute_script("return window.innerHeight;")

    # Get the vertical position of the element
    element_y = click_element.location['y']

    # Calculate the scroll position to center the element in the middle of the screen
    scroll_y = element_y - (window_height / 2)

    # Scroll the element into the middle of the screen using JavaScript
    driver.execute_script("window.scrollTo(0, arguments[0]);", scroll_y)

    click_element.click()
    sleep(0.2)

def main(id, ng_words, driver):
    url = f'https://ja.aliexpress.com/item/{id}.html'
    try:
      driver.get(url)

      sleep(1)
      try:
        drag_element = driver.find_element(By.ID, 'nc_1_n1z')
        action_chains = ActionChains(driver)
        action_chains.drag_and_drop_by_offset(drag_element, 200, 0).perform()
      except Exception as e:
        print("Drag Error: ", e)
        pass
      try:
        fee_text = driver.find_element(By.CSS_SELECTOR, '[class="dynamic-shipping-line dynamic-shipping-titleLayout"]').text
        fee_price_without_comma = fee_text.replace(',', '')
        fee_price = search(r'(\d+)円', fee_price_without_comma).group(1)
        print("fee: ", fee_price)
        if fee_price is not None and int(fee_price) > 1000:
          return "error"
      except Exception as e:
        print("Fee Error: ", e)
        pass

      response = {}
      response['id'] = id
      response['title'] = driver.find_element(By.CSS_SELECTOR, 'h1').text

      if len(ng_words) > 0 and any(element in response['title'] for element in ng_words) :
        print("Fail ng_words: ", response['title'])
        return "error"
      print("Pass ng_words: ", response['title'])
      
      price_elements = driver.find_elements(By.CSS_SELECTOR, '[data-sku-col]')
      max_price = 0
      size_list = []
      color_list = []
      try:
        parent_div = driver.find_element(By.CSS_SELECTOR, "div[class*='sku-item--wrap--']")
        img_elements = parent_div.find_elements(By.TAG_NAME, "img")

        for img in img_elements:
          alt_text = img.get_attribute("alt")
          if alt_text is not None:
            color_list.append(alt_text)
        
        print("Color_list: ", color_list)
      except Exception as e:
        print("Color Error: ", e)
        pass
      # init max_price
      try:
        pre_price = driver.find_element(By.CSS_SELECTOR, '[data-pl="product-price"]').text
        pre_price_without_comma = pre_price.replace(',', '')
        pre_price_int = findall(r'(\d+)円', pre_price_without_comma)
        if int(pre_price_int[0]) > max_price:
          max_price = int(pre_price_int[0])
      except Exception as e:
        print("Initial Price Error: ", e)
        pass

      for element in price_elements:
        try:
          if element.text != "":
            size_list.append(element.text)
          click_function(driver, element)
          pre_price = driver.find_element(By.CSS_SELECTOR, '[data-pl="product-price"]').text
          pre_price_without_comma = pre_price.replace(',', '')
          pre_price_int = findall(r'(\d+)円', pre_price_without_comma)
          if len(pre_price_int) == 0:
            continue
          else:
            if int(pre_price_int[0]) > max_price:
              max_price = int(pre_price_int[0])
        except Exception as e:
          print("Price Error: ", e)
          pass
      response['price'] = max_price
      print("Price: ", max_price)
      img_element = driver.find_element(By.CLASS_NAME, 'pdp-info-left')
      img_list = img_element.find_elements(By.TAG_NAME, 'img')
      img_src_list = []
      for img in img_list:
        img_src_list.append(img.get_attribute('src').replace('_80x80.jpg', ''))
      img_src_list.pop(0)
      response['img'] = img_src_list

      description_element = driver.find_element(By.ID, 'nav-specification')
      try:
        more_detail_button = description_element.find_element(By.TAG_NAME, 'button')
        click_function(driver, more_detail_button)
        sleep(2)
      except Exception as e:
        print("Error: ", e)
        pass
      description_keys = description_element.find_elements(By.XPATH, "//div[@id='nav-specification']//li//span")

      description_keys_text = []
      for key in description_keys: 
        description_keys_text.append(key.text)
      
      if len(size_list) > 0:
        description_keys_text.append("サイズ")
        my_string = '/'.join(size_list)
        print("サイズ: ", my_string)
        description_keys_text.append(my_string)
      if len(color_list) > 0:
        description_keys_text.append("カラー")
        my_string = '/'.join(color_list)
        print("カラー: ", my_string)
        description_keys_text.append(my_string)

      paired_description = [[description_keys_text[i], description_keys_text[i+1]] for i in range(0, len(description_keys_text), 2)]
      print("Description Keys: ", paired_description)
      response['description'] = paired_description
    except Exception as e:
        print("Error: ", e)
        return "error"
    return response

# if __name__ == '__main__':
#     print(main("1005006060893788"))