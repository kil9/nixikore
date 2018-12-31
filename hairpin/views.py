#!/usr/bin/env python3

from flask import request, render_template, url_for

from config import hairpin, session_scope, db
from .config import log
from model import PeriodicScript, Word
from support import get_twitter_api


@hairpin.route('/', methods=['GET', 'POST'])
def home():
    log.info('called /home')
    return render_template('home.html', menu='home')

@hairpin.route('/scripts', methods=['GET', 'POST'])
def scripts():
    page = request.args.get('page', default=1, type=int)

    log.info('called /scripts?page={}'.format(page))

    scripts = PeriodicScript.query \
	.order_by(PeriodicScript.modified_at.desc()) \
	.paginate(page=page, per_page=20)
    payload = {
	    'scripts': scripts,
	    'page': page,
	    'next_url': url_for('scripts', page=scripts.next_num) if scripts.has_next else None,
	    'prev_url': url_for('scripts', page=scripts.prev_num) if scripts.has_prev else None,
    }
    return render_template('scripts.html', menu='scripts', payload=payload)

@hairpin.route('/words', methods=['GET', 'POST'])
def words():
    page = request.args.get('page', default=1, type=int)
    category = request.args.get('category', default=None, type=str)

    log.info('called /words page: {} category: {}'.format(page, category))

    categories = [c[0] for c in db.session.query(Word.category).distinct().all()]

    if category:
        words = Word.query \
                .order_by(Word.modified_at.desc()) \
                .filter_by(category=category) \
	        .paginate(page=page, per_page=20)
    else:
        words = Word.query \
                .order_by(Word.modified_at.desc()) \
	        .paginate(page=page, per_page=20)

    payload = {
            'words': words,
            'categories': categories,
            'category': category,
            }

    return render_template('words.html', menu='words', payload=payload)
