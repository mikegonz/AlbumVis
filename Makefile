PATHS = cached_albums/solid/*.png cached_albums/gradient-rect/*.png cached_albums/mirror-side/*.png

all: albumvis.py
	python3 albumvis.py mpgonz solid
purge:
	rm $(PATHS)
purgeraw:
	rm cached_albums/raw/*.jpg
