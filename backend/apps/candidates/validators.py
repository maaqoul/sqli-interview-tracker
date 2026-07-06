MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024


def validate_resume_file(uploaded_file):
    """Return an error message if the file is invalid, else None."""
    if uploaded_file.size > MAX_RESUME_SIZE_BYTES:
        return "File size must not exceed 5MB."

    if not uploaded_file.name.lower().endswith(".pdf"):
        return "Only PDF files are allowed."

    content_type = getattr(uploaded_file, "content_type", "")
    if content_type and content_type != "application/pdf":
        return "Only PDF files are allowed."

    header = uploaded_file.read(4)
    uploaded_file.seek(0)
    if header != b"%PDF":
        return "Only PDF files are allowed."

    return None
