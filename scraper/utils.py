import time

def retry(f, max_retries=3, interval=1):
    """
    Retry function with exponential backoff.
    """
    for i in range(max_retries):
        try:
            return f()
        except Exception as e:
            if i == max_retries - 1:
                raise e
            else:
                time.sleep(interval)

def find_element(driver, by, value):
    """
    Find element by xpath, id, or class.
    """
    def _find_element():
        return driver.find_element(by, value)

    return retry(_find_element, max_retries=5, interval=1)

def find_elements(driver, by, value):
    """
    Find elements by xpath, id, or class.
    """
    def _find_elements():
        elements = driver.find_elements(by, value)

        if len(elements) == 0:
            raise Exception(f'No elements found by {by} and {value}')
        
        return elements

    return retry(_find_elements, max_retries=5, interval=1)