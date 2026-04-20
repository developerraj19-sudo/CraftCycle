"""
backend/utils/storage.py
────────────────────────
Handle image uploads to Supabase Storage.
Replaces Cloudinary.
"""
import os
import uuid
from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # service_role key required for server-side uploads

# Initialize Supabase client
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_image(file_bytes, bucket, original_filename, user_id):
    """
    Upload image to Supabase Storage and return public URL.
    :param file_bytes: File content in bytes
    :param bucket: 'product-images', 'scan-images', or 'avatars'
    :param original_filename: Original name to extract extension
    :param user_id: ID of the user uploading the file
    """
    if not supabase:
        print("Error: Supabase client not initialized. Check environment variables.")
        return None

    try:
        ext = original_filename.rsplit('.', 1)[-1].lower()
        # Path: user_id/unique_id.ext
        file_path = f"{user_id}/{uuid.uuid4()}.{ext}"

        # Upload to bucket
        response = supabase.storage.from_(bucket).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": f"image/{ext}"}
        )

        # Build and return the public URL
        # Note: Bucket must be public for this URL to be accessible without auth
        public_url_res = supabase.storage.from_(bucket).get_public_url(file_path)
        return public_url_res
    except Exception as e:
        print(f"Supabase Upload Error: {str(e)}")
        return None

def delete_image(bucket, file_path):
    """
    Delete a file from Supabase Storage.
    :param bucket: Name of the bucket
    :param file_path: Path to the file (e.g., '123/unique_id.jpg')
    """
    if not supabase:
        return False
        
    try:
        supabase.storage.from_(bucket).remove([file_path])
        return True
    except Exception as e:
        print(f"Supabase Delete Error: {str(e)}")
        return False
