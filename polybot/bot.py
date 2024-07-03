import telebot
from loguru import logger
import time
from telebot.types import InputFile
import os
import random
from sklearn.cluster import KMeans
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance

class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL with static Ngrok subdomain
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return: Complete file path of the downloaded photo
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_path = os.path.join(folder_name, file_info.file_path.split('/')[-1])

        with open(file_path, 'wb') as photo:
            photo.write(data)

        return file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        chat_id = msg['chat']['id']
        user_name = msg['chat'].get('first_name', '')

        # Check if the user is a new member
        if 'new_chat_members' in msg:
            greeting = f"Hello, {user_name}! Welcome to our bot."
            self.send_text(chat_id, greeting)
        elif user_name:
            self.send_text(chat_id, f"Welcome back to our bot, {user_name}!")
        else:
            self.send_text(chat_id, f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if self.is_current_msg_photo(msg):
            try:
                caption = msg.get("caption", "").lower()
                supported_filters = ['blur', 'contour', 'rotate', 'segment', 'salt and pepper', 'concat', 'brightness', 'contrast']  # Add more filters if needed
                filter_name, *parameters = caption.split()
                if filter_name not in supported_filters:
                    self.send_text(msg['chat']['id'], f"Unsupported filter. Supported filters are: {', '.join(supported_filters)}")
                    return

                img_path = self.download_user_photo(msg)
                if filter_name == 'rotate':
                    rotate_count = 1
                    if parameters and parameters[0].isdigit():
                        rotate_count = int(parameters[0])

                    processed_img = self.apply_rotate_filter(img_path, rotate_count)
                elif filter_name == 'contour':
                    processed_img = self.apply_contour_filter(img_path)
                elif filter_name == 'segment':
                    processed_img = self.apply_segment_filter(img_path)
                elif filter_name == 'salt and pepper':
                    processed_img = self.apply_salt_and_pepper_filter(img_path)
                elif filter_name == 'concat':
                    processed_img = self.apply_concat_filter(img_path)
                elif filter_name == 'brightness':
                    brightness_factor = 1.0
                    if parameters and parameters[0].replace('.', '').isdigit():
                        brightness_factor = float(parameters[0])

                    processed_img = self.apply_brightness_filter(img_path, brightness_factor)
                elif filter_name == 'contrast':
                    contrast_factor = 1.0
                    if parameters and parameters[0].replace('.', '').isdigit():
                        contrast_factor = float(parameters[0])

                    processed_img = self.apply_contrast_filter(img_path, contrast_factor)
                elif filter_name == 'blur':
                    blur_radius = 2
                    if parameters and parameters[0].isdigit():
                        blur_radius = int(parameters[0])

                    processed_img = self.apply_blur_filter(img_path, blur_radius)

                self.send_photo(msg['chat']['id'], processed_img)
                os.remove(img_path)  # Remove the downloaded image after processing
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                self.send_text(msg['chat']['id'], "Error processing image. Must write filter name.")
        else:
            # Extract the user's first name
            first_name = msg['from'].get('first_name', 'there')

            self.send_text(msg['chat']['id'], f"Hi {first_name} !,Please send a photo with a Caption indicating the filter to apply.")

    def apply_rotate_filter(self, img_path, rotate_count=1):
        """
        Apply rotation to the image located at img_path and return the path of the processed image.
        """
        original_img = Image.open(img_path)
        processed_img = original_img
        for _ in range(rotate_count):
            processed_img = processed_img.rotate(90)  # Rotate by 90 degrees
        processed_img_path = f"{img_path.split('.')[0]}_rotate.jpg"
        processed_img.save(processed_img_path)
        return processed_img_path


    def apply_blur_filter(self, img_path, blur_radius=2):
        """
        Apply blur filter to the image located at img_path and return the path of the processed image.
        """
        original_img = Image.open(img_path)
        processed_img = original_img.filter(ImageFilter.GaussianBlur(blur_radius))
        processed_img_path = f"{img_path.split('.')[0]}_blur.jpg"
        processed_img.save(processed_img_path)
        return processed_img_path

    def apply_contour_filter(self, img_path):
        """
        Apply contour filter to the image located at img_path and return the path of the processed image.
        """
        original_img = Image.open(img_path)

        # Convert the image to grayscale
        grayscale_img = original_img.convert('L')

        # Create a new blank image with the same size and mode as the original image
        contour_img = Image.new('RGB', grayscale_img.size)

        # Create a drawing context
        draw = ImageDraw.Draw(contour_img)

        # Apply contour filter by drawing contours
        width, height = grayscale_img.size
        for x in range(1, width - 1):  # Exclude edge pixels
            for y in range(1, height - 1):  # Exclude edge pixels
                # Get the pixel value at (x, y)
                pixel = grayscale_img.getpixel((x, y))
                # Check the surrounding pixels to create a contour effect
                surrounding_pixels = [
                    grayscale_img.getpixel((x - 1, y)),
                    grayscale_img.getpixel((x + 1, y)),
                    grayscale_img.getpixel((x, y - 1)),
                    grayscale_img.getpixel((x, y + 1))
                ]
                # Calculate the average difference between the current pixel and surrounding pixels
                difference = sum(surrounding_pixels) - 4 * pixel
                # Set the pixel color in the contour image based on the difference
                draw.point((x, y), fill=(max(0, pixel - difference),) * 3)

        # Save the processed image
        processed_img_path = f"{img_path.split('.')[0]}_contour.jpg"
        contour_img.save(processed_img_path)

        return processed_img_path

    def apply_segment_filter(self, img_path):
        """
        Apply segmentation filter to the image located at img_path and return the path of the processed image.
        """
        # Your implementation of segmentation filter
        original_img = Image.open(img_path)
        np_img = np.array(original_img)
        reshaped_img = np_img.reshape((-1, 3))

        # Apply k-means clustering
        kmeans = KMeans(n_clusters=2, random_state=0).fit(reshaped_img)
        labels = kmeans.labels_
        segmented_img = np.reshape(labels, (original_img.size[1], original_img.size[0]))

        # Convert the segmented image to PIL Image
        segmented_img = Image.fromarray((segmented_img * 255).astype(np.uint8))

        # Save the processed image
        processed_img_path = f"{img_path.split('.')[0]}_segment.jpg"
        segmented_img.save(processed_img_path)

        return processed_img_path
        pass

    def apply_salt_and_pepper_filter(self, img_path):
        """
        Apply salt and pepper noise to the image located at img_path and return the path of the processed image.
        """
        # Your implementation of salt and pepper noise filter
        original_img = Image.open(img_path)
        width, height = original_img.size
        for _ in range(int(width * height * 0.01)):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            original_img.putpixel((x, y), (255, 255, 255) if random.randint(0, 1) == 0 else (0, 0, 0))
        processed_img_path = f"{img_path.split('.')[0]}_salt_and_pepper.jpg"
        original_img.save(processed_img_path)
        return processed_img_path
        pass

    def apply_concat_filter(self, img_path):
        """
        Apply concatenation filter to the image located at img_path and return the path of the processed image.
        """
        # Your implementation of concatenation filter
        original_img = Image.open(img_path)
        width, height = original_img.size
        half_width = width // 2
        processed_img = Image.new('RGB', (width * 2, height))
        processed_img.paste(original_img, (0, 0))
        processed_img.paste(original_img.transpose(Image.FLIP_LEFT_RIGHT), (half_width, 0))
        processed_img_path = f"{img_path.split('.')[0]}_concat.jpg"
        processed_img.save(processed_img_path)
        return processed_img_path
        pass

    def apply_brightness_filter(self, img_path, brightness_factor=1.0):
        """
        Apply brightness adjustment to the image located at img_path and return the path of the processed image.
        """
        original_img = Image.open(img_path)
        enhancer = ImageEnhance.Brightness(original_img)
        processed_img = enhancer.enhance(brightness_factor)
        processed_img_path = f"{img_path.split('.')[0]}_brightness.jpg"
        processed_img.save(processed_img_path)
        return processed_img_path

    def apply_contrast_filter(self, img_path, contrast_factor=1.0):
        """
        Apply contrast adjustment to the image located at img_path and return the path of the processed image.
        """
        original_img = Image.open(img_path)
        enhancer = ImageEnhance.Contrast(original_img)
        processed_img = enhancer.enhance(contrast_factor)
        processed_img_path = f"{img_path.split('.')[0]}_contrast.jpg"
        processed_img.save(processed_img_path)
        return processed_img_path

