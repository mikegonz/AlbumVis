PATHS = cached_albums/solid/*.png cached_albums/center/*.png cached_albums/mirror-side/*.png cached_albums/mirror-side-blur/*.png

all: albumvis.py
	python3 albumvis.py USERNAME solid
purge:
	rm $(PATHS)
purgeraw:
	rm cached_albums/raw/*.jpg
