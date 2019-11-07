#!/usr/bin/env python3

from flask import request, render_template, url_for, flash, redirect

from category import Categories
from config import hairpin, db
from model import PeriodicScript, Word, PendingTweet, ResponseScript
from nixiko import do_generate as generate
from nixiko import do_tweet as tweet


@hairpin.before_request
def log_before_request():
    hairpin.logger.info(f'[{request.method}] {request.path}')


@hairpin.route('/', methods=['GET'])
def home():
    return render_template('home.html', menu='home')


@hairpin.route('/tweet', methods=['POST'])
def do_tweet():
    try:
        tweet(False)
    except Exception as e:
        hairpin.logger.exception(e)
        flash('트윗에 실패했습니다.')
        return 'failed'

    flash('트윗에 성공했습니다.')
    return 'ok'


@hairpin.route('/pending_tweets', methods=['GET'])
def pending_tweets():
    page = request.args.get('page', default=1, type=int)

    tweets = PendingTweet.query \
        .order_by(PendingTweet.id.asc()) \
        .paginate(page=page, per_page=20)

    next_url = url_for('pending_tweets', page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for('pending_tweets', page=tweets.prev_num) if tweets.has_prev else None
    payload = {
            'tweets': tweets,
            'page': page,
            'next_url': next_url,
            'prev_url': prev_url,
    }

    return render_template('pending_tweets.html', menu='pending_tweets', payload=payload)


@hairpin.route('/pending_tweets/publish/<int:tweet_id>', methods=['POST'])
def publish_tweet(tweet_id: int):
    flash(f'{tweet_id} 스크립트를 트윗했습니다.')

    pending_tweet = PendingTweet.query.filter_by(id=tweet_id).first()
    tweet(False, tweet=pending_tweet)

    return 'ok'


@hairpin.route('/pending_tweets/<int:tweet_count>', methods=['POST'])
def generate_tweets(tweet_count: int):
    try:
        generate(False, tweet_count)
    except Exception as e:
        hairpin.logger.exception(e)
        flash('트윗 생성에 실패했습니다.')
        return 'failed'

    flash(f'{tweet_count} 개의 트윗을 생성했습니다.')
    return 'ok'


@hairpin.route('/pending_tweets/<tweet_id>', methods=['DELETE'])
def delete_tweets(tweet_id):
    if type(tweet_id) is str and tweet_id == 'all':
        PendingTweet.query.delete()
    else:
        tweet = PendingTweet.query.filter_by(id=tweet_id).first()
        db.session.delete(tweet)

    try:
        db.session.commit()
    except Exception as e:
        hairpin.logger.exception(e)
        flash(f'tweet#{tweet_id} 삭제에 실패했습니다. 로그를 확인해주세요.')
        return redirect(url_for('pending_tweets'))

    flash(f'tweet#{tweet_id} 삭제에 성공했습니다.')
    return 'ok'


@hairpin.route('/scripts', methods=['GET'])
def scripts():
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


@hairpin.route('/scripts/test/<int:script_id>', methods=['GET'])
def test_scripts(script_id):
    tweets = generate(True, 10, id=script_id)
    return render_template('test_result.html', tweets=tweets)


@hairpin.route('/scripts', methods=['POST'])
def post_scripts():
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
        return 'failed'

    flash(f'script#{script_id} 삭제에 성공했습니다.')
    return 'ok'


@hairpin.route('/response_scripts', methods=['GET'])
def response_scripts():
    page = request.args.get('page', default=1, type=int)

    scripts = ResponseScript.query \
        .order_by(ResponseScript.id.desc()) \
        .paginate(page=page, per_page=20)
    payload = {
      'scripts': scripts,
      'page': page,
      'next_url': url_for('scripts', page=scripts.next_num) if scripts.has_next else None,
      'prev_url': url_for('scripts', page=scripts.prev_num) if scripts.has_prev else None,
    }
    return render_template('response_scripts.html', menu='response_scripts', payload=payload)


@hairpin.route('/response_scripts/test/<int:script_id>', methods=['GET'])
def test_response_scripts(script_id):
    tweets = generate(True, 10, id=script_id, is_response=True)
    return render_template('test_result.html', tweets=tweets)


@hairpin.route('/response_scripts', methods=['POST'])
def post_response_scripts():
    keyword = request.form['keyword']
    script = request.form['script']
    image_keyword = request.form['image_keyword']

    if not script:
        flash('스크립트 내용이 비어있습니다.')
        return redirect(url_for('response_scripts'))

    if not keyword:
        keyword = None

    if not image_keyword:
        image_keyword = None

    response_script = ResponseScript(
            content=script,
            image_keyword=image_keyword,
            keyword=keyword)

    db.session.add(response_script)

    try:
        db.session.commit()
    except Exception as e:
        hairpin.logger.exception(e)
        flash('저장에 실패했습니다. 로그를 확인해주세요.')
        return redirect(url_for('response_scripts'))

    flash('성공적으로 저장했습니다.')
    return redirect(url_for('response_scripts'))


@hairpin.route('/response_scripts/<int:script_id>', methods=['DELETE'])
def delete_response_scripts(script_id):
    script = ResponseScript.query.filter_by(id=script_id).first()
    db.session.delete(script)

    try:
        db.session.commit()
    except Exception as e:
        hairpin.logger.exception(e)
        flash(f'script#{script_id} 삭제에 실패했습니다. 로그를 확인해주세요.')
        return 'failed'

    flash(f'script#{script_id} 삭제에 성공했습니다.')
    return 'ok'


@hairpin.route('/words', methods=['GET'])
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

    next_url = url_for('words', page=words.next_num, category=category) if words.has_next else None
    prev_url = url_for('words', page=words.prev_num, category=category) if words.has_prev else None
    payload = {
            'words': words,
            'categories': categories,
            'category': category,
            'next_url': next_url,
            'prev_url': prev_url,
            }

    return render_template('words.html', menu='words', payload=payload)


@hairpin.route('/words', methods=['POST'])
def post_words():
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
        return 'failed'

    flash(f'word#{word_id} 삭제에 성공했습니다.')
    return 'ok'


@hairpin.route('/categories', methods=['GET', 'POST'])
def categories():
    payload = {'raw': Categories.raw, 'category': Categories.category}
    return render_template('categories.html', menu='categories', payload=payload)
