import os
import time
import logging
import traceback
import concurrent.futures
from typing import Callable, Iterable

from playwright.sync_api import Page, Frame


def get_captcha_image(page: Page | Frame, directory: str = 'captcha'):
    """Detect and save CAPTCHA image, return filename if found"""
    captcha_images = page.locator('img')
    filenames = []
    
    # Check for CAPTCHA image (look for images that might be CAPTCHA)
    for i in range(captcha_images.count()):
        img = captcha_images.nth(i)
        src = img.get_attribute('src')
        if src and ('captcha' in src.lower() or 'cap' in src.lower() or src.startswith('data:image')):
            print("\n" + "="*50)
            print("CAPTCHA DETECTED!")
            
            # Save CAPTCHA image
            try:
                # Create captcha directory if it doesn't exist
                if not os.path.exists(directory):
                    os.makedirs(directory)
                
                # Generate filename with timestamp
                timestamp = int(time.time())
                filename = f"captcha/captcha_{timestamp}.png"
                
                # Take screenshot of the CAPTCHA image
                img.screenshot(path=filename)
                print(f"CAPTCHA image saved as: {filename}")
                return filename
                        
            except Exception as e:
                print(f"Could not save CAPTCHA image: {e}")
                return None
    
    # If no specific CAPTCHA found, check for any suspicious images
    all_images = page.locator('img')
    if all_images.count() > 1:  # If there are multiple images, one might be CAPTCHA
        print("Checking for possible CAPTCHA images...")
        # Save all images to be safe
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            timestamp = int(time.time())
            for i in range(all_images.count()):
                img = all_images.nth(i)
                try:
                    filename = f"captcha/possible_captcha_{timestamp}_{i}.png"
                    img.screenshot(path=filename)
                    print(f"Saved possible CAPTCHA image: {filename}")
                    filenames.append(filename)
                except Exception:
                    pass
            
            # Return the first saved image
            if filenames:
                print("Using first saved image as CAPTCHA")
                return filenames[0]
                            
        except Exception as e:
            print(f"Could not save images: {e}")
    
    return None


def get_trace(e: Exception, n: int = 5):
    return "".join(traceback.format_exception(e)[-n:])


def run_parallel_exec(exec_func: Callable, iterable: Iterable, *func_args, **kwargs):
    """
    Runs a function in parallel using ThreadPoolExecutor.

    Args:
        exec_func (Callable): A function to run concurrently.
        iterable (Iterable): An iterable to run the function on.
        *func_args: Any additional arguments to pass to the function.
        **kwargs: Any additional keyword arguments to pass to the function.

    Returns:
        List[Tuple[Any, Any]]: A list of tuples containing the input element and the result of the function.

    Notes:
        The `max_workers` argument can be passed as a keyword argument to set the maximum number of worker threads in the thread pool executor.
        The `quiet` argument can be passed as a keyword argument to suppress the traceback logging for exceptions.
    """
    func_name = (
        f"{exec_func.__name__} | parallel_exec | "
        if hasattr(exec_func, "__name__")
        else "unknown | parallel_exec | "
    )
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=kwargs.pop("max_workers", 100), thread_name_prefix=func_name
    ) as executor:
        future_element_map = {
            executor.submit(exec_func, element, *func_args): element
            for element in iterable
        }
        result: list[tuple] = []
        for future in concurrent.futures.as_completed(future_element_map):
            element = future_element_map[future]
            try:
                result.append((element, future.result()))
            except Exception as exc:
                log_trace = exc if kwargs.pop("quiet", False) else get_trace(exc, 3)
                logging.error(
                    f"Got error while running parallel_exec: {element}: \n{log_trace}"
                )
                result.append((element, exc))
        return result