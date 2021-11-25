#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys

import click
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from pytesseract.pytesseract import image_to_string
import app_logger
import post_processing


def get_image(input, verbose):
    if verbose:
        logger = app_logger.get_logger(__name__)
    pdf = False

    # определение формата входных данных
    try:
        if '.jpg' in input:
            image = cv2.imread(input)
            if image is None:
                logger.error('Error no jpg image')
                raise IOError
            image = cv2.resize(image, None, fx=0.3, fy=0.3)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif '.png' in input:
            image = cv2.imread(input)
            if image is None:
                logging.error('Error no png image')
                raise IOError
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image =  cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 71, 11) # 91, 11
            cv2.destroyAllWindows()
        elif '.pdf' in input:
            pdf = True
            img_pdf = convert_from_path(input)
            image = []
            for img in img_pdf:
                img = np.array(img)
                image.append(img)
        # ошибка в инпуте
        else:
            click.echo('Wrong format! Please, try again!')
    except IOError:
        click.echo('I/O Error: Could not open file'+input+': No such file or directory')
        logger.error('Exit due to an error')
        sys.exit()
    except Exception as e:
        click.echo(e)
        logger.error('Exit due to an error')
        sys.exit()
    return image, pdf


@click.command()
@click.option('--input')
@click.option('--output')
@click.option('--verbose', is_flag=True, help='Print verbose message')
def read_doc(input, output, verbose):
    if verbose:
        logger = app_logger.get_logger(__name__)
    # получить изображение для работы
    image, pdf = get_image(input, verbose)
    logger.info('The image was received correctly')
    # распознание текста
    if pdf:
        all_text = []
        for img in image:
            text = pytesseract.image_to_string(img)
            all_text.append(text)
        # сохранение текста в файл
        with open(output, 'w') as f:
            for text in all_text:
                f.write(text)
        logger.info('Text from pdf was written')
    else:
        text = pytesseract.image_to_string(image)
        # сохранение текста в файл
        with open(output, 'w') as f:
            f.write(text)
        logger.info('Text from image was written')

    post_processing.post_process(output)


if __name__ == '__main__':
    read_doc()

