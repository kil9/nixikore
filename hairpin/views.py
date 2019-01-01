#!/usr/bin/env python3

from flask import request, render_template, url_for, flash, redirect

from config import hairpin, session_scope, db
from model import PeriodicScript, Word
from support import get_twitter_api
from category import Categories


@hairpin.before_request
def log_before_request():
    hairpin.logger.info(f'[{request.method}] {request.path}')

@hairpin.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', menu='home')

@hairpin.route('/scripts', methods=['GET', 'POST'])
def scripts():
    if request.method == 'POST':
        post_scripts(request)

    page = request.args.get('page', default=1, type=int)

    scripts = PeriodicScript.query \
	.order_by(PeriodicScript.id.desc()) \
	.paginate(page=page, per_page=20)
    payload = {
	    'scripts': scripts,
	    'page': page,
	    'next_url': url_for('scripts', page=scripts.next_num) if scripts.has_next else None,
	    'prev_url': url_for('scripts', page=scripts.prev_num) if scripts.has_prev else None,
    }
    return render_template('scripts.html', menu='scripts', payload=payload)

def post_scripts(request):
    script = request.form['script']
    image_keyword = request.form['image_keyword']

    if not script:
        flash('스크립트 내용이 비어있습니다.')
        return redirect(url_for('scripts'))

    if image_keyword:
        periodic_script = PeriodicScript(content=script, image_keyword=image_keyword)
    else:
        periodic_script = PeriodicScript(content=script)

    db.session.add(periodic_script)
    try:
        db.session.commit()
    except Exception as e:
        hairpin.logger.exception(e)
        flash('저장에 실패했습니다. 로그를 확인해주세요.')
        return redirect(url_for('scripts'))

    flash('성공적으로 저장했습니다.')
    return redirect(url_for('scripts'))

@hairpin.route('/scripts/<int:script_id>', methods=['DELETE'])
def delete_scripts(script_id):
    script = PeriodicScript.query.filter_by(id=script_id).first()
    db.session.delete(script)

    try:
        db.session.commit()
    except Exception as e:
        hairpin.logger.exception(e)
        flash(f'script#{script_id} 삭제에 실패했습니다. 로그를 확인해주세요.')
        return redirect(url_for('words'))

    flash(f'script#{script_id} 삭제에 성공했습니다.')
    return 'ok'

@hairpin.route('/words', methods=['GET', 'POST'])
def words():
    if request.method == 'POST':
        post_words(request)

    page = request.args.get('page', default=1, type=int)
    category = request.args.get('category', default=None, type=str)

    categories = [c[0] for c in db.session.query(Word.category).distinct().all()]

    if category:
        words = Word.query \
                .filter_by(category=category) \
                .order_by(Word.id.desc()) \
	        .paginate(page=page, per_page=20)
    else:
        words = Word.query \
                .order_by(Word.id.desc()) \
	        .paginate(page=page, per_page=20)

    payload = {
            'words': words,
            'categories': categories,
            'category': category,
            }

    return render_template('words.html', menu='words', payload=payload)

def post_words(request):
    category = request.form['category']
    content = request.form['content']

    if not category or not content:
        flash('내용이 비어있습니다.')
        return redirect(url_for('words'))

    word = Word(category=category, content=content)

    db.session.add(word)
    try:
        db.session.commit()
    except Exception as e:
        hairpin.logger.exception(e)
        flash('저장에 실패했습니다. 로그를 확인해주세요.')
        return redirect(url_for('words'))

    flash('성공적으로 저장했습니다.')
    return redirect(url_for('words', category=category))

@hairpin.route('/words/<int:word_id>', methods=['DELETE'])
def delete_words(word_id):
    word = Word.query.filter_by(id=word_id).first()
    db.session.delete(word)

    try:
        db.session.commit()
    except Exception as e:
        hairpin.logger.exception(e)
        flash(f'word#{word_id} 삭제에 실패했습니다. 로그를 확인해주세요.')
        return redirect(url_for('words'))

    flash(f'word#{word_id} 삭제에 성공했습니다.')
    return 'ok'

@hairpin.route('/categories', methods=['GET', 'POST'])
def categories():
    payload = {'raw': Categories.raw, 'category': Categories.category}
    return render_template('categories.html', menu='categories', payload=payload)
