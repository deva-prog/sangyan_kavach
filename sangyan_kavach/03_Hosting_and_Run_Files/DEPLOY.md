# Get a live demo link (free)

## Option 1: Render.com
1. Push this folder to a public GitHub repo.
2. On render.com: New > Web Service > connect the repo.
3. Runtime: Python 3. Build command: leave empty (or `echo ok`). Start command: `python server.py`.
4. Choose the free plan and deploy. Render sets PORT automatically; the server listens on 0.0.0.0 when PORT is set.
5. Copy the https://....onrender.com URL. This is your "Live Demo Link". Free services sleep when idle, so open it once just before submitting.

## Option 2: PythonAnywhere / Railway
Upload the folder and run `python server.py` as the web process, or use their WSGI/start command equivalent.

Voice input needs HTTPS (hosted links have it) and Chrome or Edge.
