#!/usr/bin/env python3

import os
import subprocess
import logging
import uuid

from pyclowder.extractors import Extractor
import pyclowder.files


class Tesseract(Extractor):

    def __init__(self):
        Extractor.__init__(self)
        self.setup()
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

    def ocr(self, filename, tmpfilename, noColumns, minLineLength):
        text = ""
        tmpfile = None
        try:
            subprocess.check_call(["tesseract", "--psm", noColumns, filename, tmpfilename])
            tmpfile = "./" + tmpfilename + ".txt"
            with open(tmpfile, 'r') as f:
                text = f.read()
        finally:
            if tmpfile is not None and os.path.isfile(tmpfile):
                os.remove(tmpfile)
            return self.clean_text(text, minLineLength)

    def clean_text(self, text, minLineLength):
        t = ""
        lines = text.splitlines()
        for line in lines:
            if line != "" and len(line) >= int(minLineLength):
                if len(t) == 0:
                    t = line
                else:
                    t += "\n" + line
        return t

    def process_message(self, connector, host, secret_key, resource, parameters):
        inputfile = resource["local_paths"][0]

        # get the parameters
        noColumns = parameters['parameters']["no-columns"]
        minLineLength = parameters['parameters']["min-line-length"]

        ocrtext = self.ocr(inputfile, str(uuid.uuid4()), str(noColumns), minLineLength).strip()
        if not ocrtext:
            ocrtext = 'No text detected'

        content = {'ocr_text': ocrtext}
        metadata = self.get_metadata(content, "file", parameters['id'], host)

        # upload metadata
        pyclowder.files.upload_metadata(connector, host, secret_key, parameters['id'], metadata)

        logging.info("Uploaded metadata %s", metadata)

if __name__ == "__main__":
    extractor = Tesseract()
    extractor.start()
