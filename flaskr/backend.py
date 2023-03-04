# TODO(Project 1): Implement Backend according to the requirements.
import hashlib
import json
import os
import io
import re  # for regex password validation
from google.cloud import storage
class Backend:
    '''
    Facade for the underlying GCS buckets.
    '''
    def __init__(self):
        '''
        Initializing
        '''
        self.client = storage.Client(project='groupx-2023')
        self.wiki_content_bucket = self.client.get_bucket('wiki_contents_groupx')
        self.users_bucket = self.client.get_bucket('users_and_passwords_groupx')
        self.about_us_pictures = self.client.get_bucket('about-us-pictures')

    def get_wiki_page(self, name):
        '''
        Retrieving uploaded page from wiki_content_bucket
        '''
        cur_blob = self.wiki_content_bucket.blob(f"pages/{name}")
        if not cur_blob.exists():
            return None
        return cur_blob.download_as_text()
    
    def get_all_image_names(self):
        try:
            all_blobs = list(self.about_us_pictures.list_blobs())
            names = [os.path.basename(blob.name) for blob in all_blobs]
            return names
        except Exception as e:
            print(f"An error occurred while retrieving image names: {e}")
            return []

    def get_all_page_names(self):
        '''
        Retrieves the names of all the pages from the bucket
        '''
        all_blobs = self.wiki_content_bucket.list_blobs(prefix="pages/")
        names = [os.path.splitext(os.path.basename(blob.name))[0] for blob in all_blobs]
        return names

    def upload(self, content, name):
        '''
        Adding data to the bucket
        '''
        cur_blob = self.wiki_content_bucket.blob(f"pages/{name}")
        cur_blob.upload_from_string(content)
    
    def sign_up(self, username, password):
        '''
        Adding user data with a hashed password.
        '''
        cur_blob = self.users_bucket.blob(f"users/{username}")
        if cur_blob.exists():
            raise ValueError("This User Already Signed Up! Please sign in.")
        site_secret = "ProjectX_User"
        with_salt = f"{username}{site_secret}{password}"
        hash_pass = hashlib.blake2b(with_salt.encode()).hexdigest()
        credentials = {"username":username, "password":hash_pass}
        cur_blob.upload_from_string(json.dumps(credentials))
        #print(credentials, with_salt)

    def sign_in(self, username, password):
        print("I'm here")
        '''
        Checking if a password  matches the bucket data once hashed
        '''
        try:
            cur_blob = self.users_bucket.blob(f"users/{username}")
            site_secret = "ProjectX_User"
            with_salt = f"{username}{site_secret}{password}"
            hash_pass = hashlib.blake2b(with_salt.encode()).hexdigest()
            data = json.loads(cur_blob.download_as_text())
            return data['password'] == hash_pass
        except:
            return

    def authenticate_user(self, username, password):
        '''
        This is what pages.py calls, an intermediary method for Auth
        '''
        if self.sign_in(username, password):
            return {'success': True, 'message': 'Authentication successful.'}
        else:
            return {'success': False, 'message': 'Invalid username or password.'}

    def authenticate_new_user(self, username, password):
        '''
        This is what pages.py calls, an intermediary method for new user Auth Validation
        '''
        if len(username)<4:
            return {'success': False, 'message': 'Username needs to be longer than four characters! Try again please.'}
        r_check = r"^(?=.*\d)(?=.*[a-zA-Z]).{6,}$"  # Define the regular expression pattern
        reg = re.compile(r_check)  # Compile the regular expression
        valid = reg.match(password)
        if not bool(valid):
            return {'success': False, 'message': 'Password needs to include at least one number and be longer than 5 characters.'}
        self.sign_up(username, password)
        return {'success': True, 'message': 'New Account Created!'}

    def get_image(self,name):
        '''
        Retrieving an image from the bucket
        '''
        cur_blob = self.wiki_content_bucket.blob(f"images/{name}")
        if not cur_blob.exists():
            return None
        data = io.BytesIO()
        cur_blob.download_to_file(data)
        data.seek(0)
        return data.getvalue()
'''
trial = Backend()
#trial.sign_up("Dagi_Works","dagi_does_work")
print(trial.sign_in("Dagi_Work","dagi_does_work"))
print(trial.sign_in("Dagi_Works","dagi_does_work"))
'''