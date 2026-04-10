from huggingface_hub import HfApi, create_repo
import os

# Your Space name
repo_id = "arya89/openops"

# Initialize API
api = HfApi()

# Create/update the space
try:
    create_repo(
        repo_id=repo_id,
        repo_type="space",
        space_sdk="docker",
        exist_ok=True
    )
    print(f"✅ Space created/verified: {repo_id}")
except Exception as e:
    print(f"Space already exists or error: {e}")

# Upload all files
print("📤 Uploading files...")
api.upload_folder(
    folder_path=".",
    repo_id=repo_id,
    repo_type="space",
    ignore_patterns=[
        "__pycache__",
        "*.pyc",
        ".git",
        ".gitattributes",
        "deploy.py",
        "openops-incident-commander"
    ]
)

print(f"✅ Deployment complete!")
print(f"🌐 View your Space: https://huggingface.co/spaces/arya89/openops")