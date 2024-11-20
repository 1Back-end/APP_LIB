import hashlib
import os
import uuid
from base64 import b64decode
from mimetypes import MimeTypes
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.storage import Storage
from .uploads import upload_file  # Assurez-vous que cette fonction est correcte
from .config import Config


CHUNK_SIZE = 1024 * 1024  # Taille des morceaux du fichier pour le téléchargement


def convert_data(file_name):
    """ Convertit un fichier en données binaires """
    with open(file_name, 'rb') as file:
        return file.read()


def hash_files(filename: str):
    file = filename  # Location of the file (can be set a different way)
    block_size = 65536  # The size of each read from the file

    # Create the hash object, can use something other than `.sha256()` if you wish
    file_hash = hashlib.sha256()
    with open(file, 'rb') as f:  # Open the file to read it's bytes
        # Read from the file. Take in the amount declared above
        fb = f.read(block_size)
        while len(fb) > 0:  # While there is still data being read from the file
            file_hash.update(fb)  # Update the hash
            fb = f.read(block_size)  # Read the next block from the file
    print(file_hash.hexdigest())  # Get the hexadecimal digest of the hash
    return file_hash.hexdigest()


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

class FileUtils:
    def __init__(self, my_file: UploadFile = None, base64: str = None, streaming_content: any = None, name: str = None):
        """ Initialisation de la gestion du fichier """
        if (not my_file and not base64 and not streaming_content) or (my_file and base64 and streaming_content):
            raise Exception("Provide only file or base64 or streaming content")

        # Traitement des fichiers basés sur base64
        if base64:
            if len(base64.split(",")) != 2:
                raise Exception("Invalid base 64")
            info = base64.split(",")[0].split(";")[0].split(":")[1]
            uuid_file_name = uuid.uuid1()
            self.blob_name = "{}{}".format(uuid_file_name, "-{}".format(name.replace(" ", "-")) if name else ".{}".format(info.split("/")[1]))
            self.path_file = os.path.join(Config.UPLOADED_FILE_DEST, self.blob_name)
            self.mimetype = info
            byte = b64decode(base64.split(",")[1], validate=True)

            try:
                with open(self.path_file, 'wb') as f:
                    f.write(byte)
            except OSError as error:
                raise Exception(f"Error writing base64 file: {error}")
        elif my_file:
            """ Si c'est un fichier envoyé par l'utilisateur """
            self.blob_name = "{}-{}".format(uuid.uuid1(), my_file.filename.replace(" ", "-"))
            self.path_file = os.path.join(Config.UPLOADED_FILE_DEST, self.blob_name)
            with open(self.path_file, 'wb') as out_file:
                contents = my_file.file.read()
                out_file.write(contents)
            self.mimetype = my_file.content_type

        else:
            """ Gestion d'un fichier de streaming """
            uuid_file_name = uuid.uuid1()
            self.blob_name = "{}{}".format(uuid_file_name, "-{}".format(name.replace(" ", "-")))
            self.path_file = os.path.join(Config.UPLOADED_FILE_DEST, self.blob_name)
            self.mimetype = MimeTypes().guess_type(os.path.basename(self.path_file))[0]

        # On obtient les informations sur le fichier
        self.size = os.stat(self.path_file).st_size
        self.is_image = False
        self.thumbnail = {}
        self.medium = {}
        self.width = 0
        self.height = 0
        if self.mimetype.split("/")[0] in ["image"]:
            self.is_image = True

    def __repr__(self):
        """ Représentation du fichier """
        return f"<FileUtils: blob_name: {self.blob_name} path_file: {self.path_file} mimetype: {self.mimetype} is_image: {self.is_image} width: {self.width} height: {self.height}/>"
    
    def save(self, db: Session):
        """ Sauvegarde le fichier dans la base de données """
        url, test = upload_file(self.path_file, self.blob_name, content_type=self.mimetype)
        os.remove(self.path_file)  # On supprime le fichier après l'upload

        # Sauvegarde des miniatures si elles existent
        if "file_name" in self.thumbnail:
            url_thumbnail, test = upload_file(rreplace(self.path_file, '.', '_thumbnail.', 1), self.thumbnail["file_name"], content_type=self.mimetype)
            self.thumbnail["url"] = url_thumbnail
            os.remove(rreplace(self.path_file, '.', '_thumbnail.', 1))

        if "file_name" in self.medium:
            url_medium, test = upload_file(rreplace(self.path_file, '.', '_medium.', 1), self.medium["file_name"], content_type=self.mimetype)
            self.medium["url"] = url_medium
            os.remove(rreplace(self.path_file, '.', '_medium.', 1))

        # Sauvegarde de l'objet dans la base de données
        db_obj = Storage(
            uuid=str(uuid.uuid4()),
            file_name=self.blob_name,
            url=url,
            width=self.width,
            height=self.height,
            size=self.size,
            thumbnail=self.thumbnail,
            medium=self.medium,
            mimetype=self.mimetype
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj
