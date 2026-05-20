from flask import Flask, Response
import hardware
from vision import gen_frames, cleanup as vision_cleanup

app = Flask(__name__)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <html>
    <body style="margin:0;background:black;">
        <img src="/video_feed" style="width:100vw;height:100vh;">
    </body>
    </html>
    '''

if __name__ == '__main__':
    try:
        hardware.setup()
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("Cerrando aplicación...")
    finally:
        vision_cleanup()
        hardware.cleanup()
