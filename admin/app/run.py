#!/usr/bin/python

from views import app


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5698, debug=True)

