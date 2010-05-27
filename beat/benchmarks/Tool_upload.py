import os
import beat.settings

def handle_uploaded_file(f, title):
	print os.path.join(beat.settings.STATIC_MEDIA_ROOT, 'upload', 'logs', f.name)
	destination = open(os.path.join(beat.settings.STATIC_MEDIA_ROOT, 'upload', 'logs', f.name), 'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()
