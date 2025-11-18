from app.application.use_cases.call_process_photo import CallProcessPhoto

def cli_main(file_path: str):
    call_process_photo = CallProcessPhoto()
    call_process_photo.process_photo(file_path)
    