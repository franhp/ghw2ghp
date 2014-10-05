import commands
from flask import Flask, abort, request
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def api():
    r = request.get_json(force=True)
    if r['ref'] == 'refs/heads/master':
        status, output = commands.getstatusoutput('python ghw2ghp.py -u True deploy')
        app.logger.debug(output)
        if status is 0: 
            return 'OK'
        else:
            abort(400)
    else:
        return 'Not Master branch'

if __name__ == '__main__':
    app.debug = True
    app.run(port=8001)
