# -*- coding: utf-8 -*-
import json
import logging
from lib.utils import decode_source, get_fontmap
from flask import Blueprint, request, make_response
from blockdiag.utils.rst.directives import with_blockdiag

app = Blueprint('nwdiag_main', __name__)


@app.route('/image', methods=['GET', 'POST'])
def nwdiag_image():
    if request.method == 'POST':
        source = request.form.get('src')
        encoding = request.form.get('encoding')
        compression = request.form.get('compression')
    else:
        source = request.args.get('src')
        encoding = request.args.get('encoding')
        compression = request.args.get('compression')

    source = decode_source(source, encoding, compression)

    format = request.args.get('format', 'SVG')
    image = nwdiag_generate_image(source, format)
    if encoding == 'jsonp':
        callback = request.args.get('callback')
        if callback:
            dumped = json.dumps(image, ensure_ascii=False)
            jsonp = u'%s(%s)' % (callback, dumped)
        else:
            jsonp = ''

        response = make_response(jsonp)
        response.headers['Content-Type'] = 'text/javascript'
    else:
        response = make_response(image['image'])
        if format == 'PNG':
            response.headers['Content-Type'] = 'image/png'
        elif encoding == 'base64':
            response.headers['Content-Type'] = 'image/svg+xml'
        else:
            response.headers['Content-Type'] = 'text/plain'

    return response


@with_blockdiag
def nwdiag_generate_image(source, format):
    from nwdiag import parser, builder, drawer

    try:
        tree = parser.parse_string(source)
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = drawer.DiagramDraw(format, diagram, fontmap=get_fontmap(),
                                  ignore_pil=True)
        draw.draw()

        image = draw.save('')
        etype = None
        error = None
    except Exception, e:
        image = ''
        etype = e.__class__.__name__
        error = str(e)
        logging.exception(e)

    return dict(image=image, etype=etype, error=error)
